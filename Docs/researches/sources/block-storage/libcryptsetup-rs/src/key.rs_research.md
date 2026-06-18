# File Research: sources/block-storage/libcryptsetup-rs/src/key.rs

Implements `CryptVolumeKeyHandle<'a>`.

Key API:
- `get`
- `verify`

Behavior:
- `get` retrieves a volume key into a caller-provided mutable byte buffer and returns `(keyslot, actual_size)`.
- Optional keyslot maps to `CRYPT_ANY_SLOT`.
- Optional passphrase is passed as nullable pointer plus length.
- `verify` checks a supplied volume key against the crypt device.

Research notes:
- The caller controls output buffer capacity; libcryptsetup updates the size value.
- Passphrase is byte-slice based, so embedded NUL is allowed.
