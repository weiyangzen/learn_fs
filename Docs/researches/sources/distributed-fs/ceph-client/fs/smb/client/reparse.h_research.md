# sources/distributed-fs/ceph-client/fs/smb/client/reparse.h

## Purpose
`reparse.h` is the CIFS reparse-point interface header. It declares reparse creation/parsing entry points and provides small conversion helpers used by lookup, inode validation, and metadata translation.

## Important APIs, types, and functions
The header defines `REPARSE_SYM_PATH_MAX` and the internal sentinel `IO_REPARSE_TAG_INTERNAL`. Inline helpers include `reparse_mkdev`, `wsl_make_kuid`, `wsl_make_kgid`, `reparse_mode_nfs_type`, `reparse_mode_wsl_tag`, `reparse_inode_match`, and `cifs_open_data_reparse`. Declarations expose `cifs_reparse_point_to_fattr`, `create_reparse_symlink`, `mknod_reparse`, and `smb2_get_reparse_point_buffer`.

## Control flow
Callers use the mode-to-tag helpers before creating special-file reparse points, use `cifs_open_data_reparse` to normalize open-info attributes, and use `reparse_inode_match` during inode revalidation. The inline uid/gid helpers honor mount overrides before constructing kernel ids from WSL metadata.

## State and persistence
The header itself stores no state. It defines how persisted reparse tag, ctime, and WSL EA values are interpreted. `reparse_inode_match` treats tag plus ctime as the cache coherency signal, except for the internal sentinel used when full reparse data is unavailable.

## Dependencies and integration points
It depends on VFS mode bits, uid/gid types, CIFS mount flags, `cifsglob.h`, `fs_context.h`, and `smbfsctl.h`. It is included by reparse creation/parsing code and SMB1 operations that need to create or inspect reparse-backed inodes.

## Risks and test signals
Risks include stale inode matching if a server changes reparse data without ctime changes, wrong major/minor ordering for WSL devices, invalid uid/gid mapping under user namespaces, and accidentally matching `IO_REPARSE_TAG_INTERNAL` as a real tag. Test signals include inode revalidation after tag/data changes, uid/gid override mounts, WSL device decoding, and open-info paths with both POSIX and all-info layouts.
