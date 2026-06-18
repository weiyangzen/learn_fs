# sources/distributed-fs/ceph-client/fs/ntfs/ea.h

Purpose: declares the NTFS EA/xattr and ACL interface used by inode and file operation setup.

Important APIs and types:
- `NTFS_EA_UID`, `NTFS_EA_GID`, and `NTFS_EA_MODE` select which WSL metadata EAs should be written.
- `ntfs_xattr_handlers` is the exported VFS xattr handler table.
- `ntfs_ea_get_wsl_inode()` loads WSL uid/gid/mode/device metadata from EAs.
- `ntfs_ea_set_wsl_inode()` writes WSL metadata EAs and can return packed EA size.
- `ntfs_listxattr()` is the inode operation hook for listing xattrs.
- When `CONFIG_NTFS_FS_POSIX_ACL` is enabled, `ntfs_get_acl()`, `ntfs_set_acl()`, and `ntfs_init_acl()` are declared; otherwise get/set are `NULL`.

Control flow and integration:
- `inode.c` calls WSL EA helpers during inode load and metadata changes.
- `file.c` exposes `ntfs_listxattr` and ACL handlers through regular and special inode operations.
- `ea.c` owns all implementations behind this header.

State and persistence behavior:
- The header defines selection bits but no state. Persistence happens through `$EA_INFORMATION` and `$EA` writes in `ea.c`.
- ACL macro fallback means builds without POSIX ACL omit ACL operation hooks cleanly.

Dependencies:
- Requires NTFS inode and VFS type declarations from surrounding includes in consumers.
- Uses kernel `xattr_handler`, `dentry`, `inode`, `mnt_idmap`, `posix_acl`, `dev_t`, and endian types.

Risks and edge cases:
- Callers must hold the expected NTFS inode locks around WSL EA setters where required by implementation.
- The compile-time ACL `NULL` macros mean code must tolerate missing ACL handlers.

Test signals:
- Build matrix should cover `CONFIG_NTFS_FS_POSIX_ACL=y` and disabled cases.
- Metadata tests should verify chmod/chown update WSL EAs only for selected flags.
