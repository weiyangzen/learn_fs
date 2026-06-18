# sources/distributed-fs/ceph-client/fs/crypto/hooks.c

## Purpose
`hooks.c` provides exported fscrypt hooks that filesystems call from higher-level VFS operations. It enforces key availability, encrypted-tree policy consistency, no-key-name handling, symlink encryption/decryption, setattr restrictions, and casefold dirhash preparation.

## Important APIs and Functions
- `fscrypt_file_open()` requires the file key, then verifies the opened inode is permitted under its parent directory policy.
- `__fscrypt_prepare_link()` and `__fscrypt_prepare_rename()` reject no-key dentries and cross-directory moves that would violate encrypted-directory policy inheritance.
- `__fscrypt_prepare_lookup()` sets up encrypted filename handling and marks no-key dentries. `fscrypt_prepare_lookup_partial()` supports filesystems that implement filename encryption themselves.
- `__fscrypt_prepare_readdir()` sets up directory encryption info while allowing unsupported policies to behave like no-key access.
- `__fscrypt_prepare_setattr()` requires the key before size changes.
- `fscrypt_prepare_setflags()` derives a v2 dirhash key when enabling `FS_CASEFOLD_FL` on an encrypted directory.
- `fscrypt_prepare_symlink()`, `__fscrypt_encrypt_symlink()`, `fscrypt_get_symlink()`, and `fscrypt_symlink_getattr()` implement encrypted symlink sizing, encryption, no-key presentation, plaintext caching, and stat-size correction.

## Control Flow
Open begins with `fscrypt_require_key()` and then performs a cheap RCU parent check; only encrypted parents trigger the expensive parent dentry reference and policy comparison. Link and rename use dentry no-key flags as a proxy for unavailable directory keys, then call `fscrypt_has_permitted_context()` for policy enforcement. Symlink creation is two-stage: `fscrypt_prepare_symlink()` computes on-disk size before inode creation, then `__fscrypt_encrypt_symlink()` encrypts after `fscrypt_prepare_new_inode()` has prepared the symlink key.

## State and Persistence
The file updates dentry state via `fscrypt_prepare_dentry()`, initializes `ci_dirhash_key` in inode crypto info when casefolding is enabled, writes encrypted symlink bodies in the historical `fscrypt_symlink_data` format, and caches decrypted symlink targets in `inode->i_link`. It does not persist policies itself; it relies on policy and context helpers.

## Dependencies and Integration
It depends on filename helpers such as `fscrypt_setup_filename()`, `fscrypt_fname_encrypt()`, `fscrypt_fname_disk_to_usr()`, and `fscrypt_fname_alloc_buffer()`, policy helpers from `policy.c`, key setup from `keysetup.c`, and VFS dentry/inode APIs. Its exported symbols are used by fscrypt-enabled filesystems in open, lookup, link, rename, readdir, setattr, symlink, get_link, and getattr paths.

## Risks and Edge Cases
- Parent policy verification must run even for unencrypted children under encrypted parents to detect offline tampering.
- `RENAME_EXCHANGE` requires checking both swapped inodes against their target encrypted directories.
- Symlink ciphertext stores a redundant little-endian length and counts an extra terminator; max-length calculations must keep this historical format intact.
- `fscrypt_get_symlink()` must not cache no-key encoded targets because they become stale when the key is added later.
- Casefolded encrypted directories require v2 policies; v1 has no dirhash-key derivation.

## Test Signals
Test open/link/rename failures across mismatched encrypted policies, no-key lookup/delete behavior, symlink round trips with and without keys, symlink `st_size` matching visible target length, `FS_CASEFOLD_FL` rejection for v1 policies, and `RENAME_EXCHANGE` policy violations in both directions.
