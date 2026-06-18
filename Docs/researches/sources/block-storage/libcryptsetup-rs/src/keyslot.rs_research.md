# File Research: sources/block-storage/libcryptsetup-rs/src/keyslot.rs

Implements `CryptKeyslotHandle<'a>` for keyslot management.

Key API:
- `add_by_passphrase`
- `change_by_passphrase`
- `add_by_keyfile_device_offset`
- `add_by_key`
- `destroy`
- `status`
- `get_priority`
- `set_priority`
- `max_keyslots`
- `area`
- `get_key_size`
- `get_encryption`
- `get_pbkdf`
- `set_encryption`
- `get_dir`

Behavior:
- Supports passphrase, keyfile, and raw-volume-key based keyslot operations.
- Optional keyslots map to `CRYPT_ANY_SLOT`.
- `add_by_key` supports explicit volume key bytes, generated key length, or no volume key.
- Converts status and priority through typed enums.
- Returns keyslot area offsets and sizes.
- Retrieves PBKDF parameters into `CryptPbkdfType`.

Research notes:
- `get_encryption` returns `&str` borrowed from libcryptsetup-managed memory plus key size.
- `get_dir` returns a boxed path built from libcryptsetup’s device mapper directory string.
