# File Research: sources/block-storage/libcryptsetup-rs/src/context.rs

Implements `CryptContextHandle<'a>`, covering high-level crypt device context operations.

Key API:
- `format`
- `convert`
- `set_uuid`
- `set_label`
- `volume_key_keyring`
- `load`
- `repair`
- `resize`
- `suspend`
- `resume_by_passphrase`
- `resume_by_keyfile_device_offset`

Behavior:
- `format` accepts `EncryptionFormat`, cipher/mode strings, optional UUID, either provided volume key bytes or generated key length, and optional format params.
- `load`, `convert`, and `repair` use generic `CryptParams`.
- `resume_by_passphrase` passes the passphrase as a C string pointer plus explicit length.
- `resume_by_keyfile_device_offset` passes keyfile path, size, and offset.

Important dependencies:
- `either::Either`
- `uuid::Uuid`
- `CryptParams`
- `EncryptionFormat`
- FFI macros

Research notes:
- Volume key length is byte-based; docs explicitly warn about bit-to-byte conversion.
- Passphrase resume uses `CString`, so embedded NUL bytes are rejected there, unlike byte-slice passphrase activation methods.
