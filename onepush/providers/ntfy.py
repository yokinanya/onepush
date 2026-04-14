import base64

from ..core import Provider

NTFY_JSON_OPTIONAL_FIELDS = (
    'title',
    'tags',
    'priority',
    'actions',
    'click',
    'attach',
    'markdown',
    'icon',
    'filename',
    'delay',
    'email',
    'call',
    'sequence_id',
)

NTFY_PRIORITY_NAMES = {
    'min': 1,
    'low': 2,
    'default': 3,
    'high': 4,
    'max': 5,
    'urgent': 5,
}


class Ntfy(Provider):
    name = 'ntfy'
    _params = {
        'required': ['url', 'content', 'topic'],
        'optional': ['token', 'title', 'tags', 'priority', 'actions', 'click', 'attach', 'markdown', 'icon', 'filename', 'delay', 'email', 'call', 'sequence_id', 'username', 'password']
    }

    def _prepare_url(self, url: str, **kwargs):
        self.url = url
        return self.url

    @staticmethod
    def _prepare_token(token: str = None, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        if username and password:
            credentials = f'{username}:{password}'.encode()
            encoded_credentials = base64.b64encode(credentials).decode('utf-8')
            return f'Basic {encoded_credentials}'
        if token:
            return f'Bearer {token}'
        return None

    @staticmethod
    def _normalize_param(field: str, value):
        if field == 'priority' and isinstance(value, str):
            return NTFY_PRIORITY_NAMES.get(value.lower(), value)
        if field == 'tags' and isinstance(value, str):
            return [tag.strip() for tag in value.split(',') if tag.strip()]
        return value

    def _prepare_data(self, topic: str, content: str, token: str = None, **kwargs):
        data = {'topic': topic, 'message': content}
        for field in NTFY_JSON_OPTIONAL_FIELDS:
            if field not in kwargs or kwargs[field] is None:
                continue
            data[field] = self._normalize_param(field, kwargs[field])
        data['token'] = self._prepare_token(token=token, **kwargs)
        self.data = data
        return self.data

    def _send_message(self):
        data = self.data.copy()
        token = self.data.get('token')
        headers = {'Authorization': token} if token else None
        data.pop('token', None)
        return self.request('post', self.url, json=data, headers=headers)
