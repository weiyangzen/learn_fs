# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_token.c

This file implements LUKS2 token handler registration, built-in/external token loading, token JSON creation/removal, token status, assignment to keyslots, and unlock flows.

Token handler model:
- `token_handlers` is a fixed-size array of internal handler slots.
- The built-in keyring token is registered by default with open/free/validate/dump callbacks.
- Additional built-in-like names are blocked by the reserved `LUKS2_BUILTIN_TOKEN_PREFIX`.
- External token support is conditional on `USE_EXTERNAL_TOKENS`.

External token loading:
- External token path defaults to `EXTERNAL_LUKS2_TOKENS_PATH` and can be changed to an absolute path.
- Names must be non-empty, max `LUKS2_TOKEN_NAME_MAX`, and only alnum, `-`, or `_`.
- Loader builds `libcryptsetup-token-<name>.so`, uses `dlopen`, resolves ABI symbols, validates required callbacks, records ABI version, and stores the dlhandle.
- `crypt_token_unload_external_all()` unloads v2 external handlers and frees copied names.

Token metadata operations:
- `LUKS2_token_create()` creates, replaces, or removes a token JSON object at a given token id or first free slot.
- It parses JSON, validates against LUKS2 schema, validates handler-specific constraints when a handler exists, rejects missing built-in handlers, checks header JSON size, and optionally commits.
- `LUKS2_token_status()` reports inactive, internal/external known, or internal/external unknown.
- `LUKS2_token_json_get()` returns serialized token JSON.
- `LUKS2_token_dump()` delegates pretty-printing to the token handler.

Unlock flow:
- `LUKS2_token_unlock_key()` unlocks a volume key using a specific token or any usable token.
- Token usability checks assigned keyslots, requested segment, minimum keyslot priority, and whether a keyslot assignment is required.
- A token handler returns a passphrase/key buffer, then `LUKS2_keyslot_open_by_token()` attempts assigned keyslots in priority order.
- For `CRYPT_ANY_TOKEN`, token attempts are ordered by priority: prefer first, then normal.
- Return priority is carefully preserved: `-ENOENT` unusable, `-EPERM` provided material did not unlock, `-EAGAIN` hardware unavailable/not ready, `-ENOANO` wrong/missing PIN. Other errors short-circuit.
- Tokens returning `-ENOANO` are blocked from later priority loops.

Passphrase extraction:
- `LUKS2_token_unlock_passphrase()` opens a token without requiring assigned keyslots and copies the returned buffer into a crypt safe allocation for caller use.

Assignment operations:
- `LUKS2_token_assign()` assigns/unassigns one keyslot, all keyslots, one token, or all tokens.
- `LUKS2_token_is_assigned()` checks a token’s `keyslots` array.
- `LUKS2_token_assignment_copy()` copies token assignments from one keyslot to another.

Safety behavior:
- Token buffers are freed through handler `buffer_free` when available; otherwise they are zeroed and freed.
- External token positive returns, `-EINVAL`, and `-EPERM` are normalized to `-ENOENT` in `translate_errno()` for non-built-in handlers.
- External loading is disabled cleanly when unsupported or explicitly disabled.

Dependencies:
- JSON-C
- dynamic loader APIs when enabled
- keyslot priority/open helpers
- LUKS2 token JSON/schema helpers
- built-in keyring token callbacks from `luks2_token_keyring.c`
