# File Research: sources/block-storage/libcryptsetup-rs/src/backup.rs

Implements `CryptBackupHandle<'a>` for header backup and restore.

Key API:
- `header_backup`
- `header_restore`

Behavior:
- Accepts optional `EncryptionFormat`; `None` becomes a null requested type pointer.
- Converts backup file `Path` to `CString`.
- Calls `crypt_header_backup` and `crypt_header_restore`.

Important dependencies:
- `EncryptionFormat::as_ptr`
- `CryptDevice`
- `LibcryptErr`
- `path_to_cstring!`, `errno!`, `mutex!`

Research notes:
- File is a direct FFI wrapper with minimal policy.
- Restore/backup safety and overwrite semantics are delegated to libcryptsetup.
