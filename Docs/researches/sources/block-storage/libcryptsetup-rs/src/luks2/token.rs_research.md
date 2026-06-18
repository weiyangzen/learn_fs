# File Research: sources/block-storage/libcryptsetup-rs/src/luks2/token.rs

Implements LUKS2 token APIs.

Key types:
- `CryptTokenInfo`
- `TokenInput<'a>`
- `CryptLuks2TokenHandle<'a>`

Key API:
- `json_get`
- `json_set`
- `status`
- `luks2_keyring_set`
- `luks2_keyring_get`
- `assign_keyslot`
- `unassign_keyslot`
- `is_assigned`
- `activate_by_token`
- `activate_by_token_pin` behind `cryptsetup24supported`
- free function `register`

Behavior:
- Converts token JSON between `serde_json::Value` and C strings.
- Represents token status as typed enum with optional token type string.
- Allows add/replace/remove token via `TokenInput`.
- Supports keyring token parameter set/get.
- Token assignment maps `None` keyslot to all slots.
- `is_assigned` maps `0` to true and `-ENOENT` to false.
- Registers token handlers after checking handler name is NUL-terminated.

Research notes:
- Token activation accepts optional user data pointer.
- `register` requires callers to pass a static string ending with `\0`, typically via `c_str!`.
