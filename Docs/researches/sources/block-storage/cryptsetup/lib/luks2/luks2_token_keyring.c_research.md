# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_token_keyring.c

This file implements the built-in LUKS2 kernel keyring token handler.

Main behavior:
- `keyring_open()` loads the LUKS2 header, gets the token JSON, reads `key_description`, and calls `crypt_keyring_get_user_key()` to retrieve key material from the kernel keyring.
- `-ENOTSUP` from keyring access maps to `-ENOENT`; other negative failures map to `-EPERM`.
- `keyring_validate()` parses token JSON and requires exactly three fields, including non-empty string `key_description`.
- `keyring_dump()` prints the key description.
- `LUKS2_token_keyring_json()` formats a token JSON string with type `LUKS2_TOKEN_KEYRING`, empty `keyslots`, and the given key description.
- `LUKS2_token_keyring_get()` extracts `key_description` into `crypt_token_params_luks2_keyring`.
- `keyring_buffer_free()` releases retrieved material with `crypt_safe_free()`.

Important assumptions:
- `LUKS2_token_keyring_get()` asserts the token type is the keyring token.
- Validation only checks the description is a string and non-empty; a TODO notes possible future format validation.

Dependencies:
- `luks2_internal.h`
- JSON-C
- kernel keyring helper `crypt_keyring_get_user_key`
- safe free helper
