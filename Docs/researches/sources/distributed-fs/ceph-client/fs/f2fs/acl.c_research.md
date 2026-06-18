# sources/distributed-fs/ceph-client/fs/f2fs/acl.c

## Purpose

`fs/f2fs/acl.c` implements POSIX ACL support for F2FS on top of F2FS xattrs. It converts between the F2FS on-disk ACL xattr format and in-memory `struct posix_acl`, handles get/set operations for access and default ACLs, applies ACL inheritance and umask behavior during inode creation, and keeps inode mode bits synchronized with equivalent access ACLs.

## Important APIs, Types, and Functions

Public entry points are `f2fs_get_acl()`, `f2fs_set_acl()`, and `f2fs_init_acl()`. Internal format helpers are `f2fs_acl_size()`, `f2fs_acl_count()`, `f2fs_acl_from_disk()`, and `f2fs_acl_to_disk()`. ACL mutation helpers include `__f2fs_get_acl()`, `f2fs_acl_update_mode()`, `__f2fs_set_acl()`, `f2fs_acl_clone()`, `f2fs_acl_create_masq()`, and `f2fs_acl_create()`.

The on-disk structs and `F2FS_ACL_VERSION` come from `acl.h`; xattr indexes come from `xattr.h`. Values are stored in the empty-name POSIX ACL xattr entries `F2FS_XATTR_INDEX_POSIX_ACL_ACCESS` and `F2FS_XATTR_INDEX_POSIX_ACL_DEFAULT`.

## Control Flow

`f2fs_get_acl()` rejects RCU lookup with `-ECHILD` and calls `__f2fs_get_acl()`. The internal getter selects access or default ACL index, first probes `f2fs_getxattr()` for the value size, allocates a zeroed buffer if present, fetches the value, and parses it with `f2fs_acl_from_disk()`. `-ENODATA` becomes a NULL ACL, while other errors become `ERR_PTR()`.

`f2fs_set_acl()` checks for checkpoint error and then calls `__f2fs_set_acl()`. For access ACLs, `f2fs_acl_update_mode()` uses `posix_acl_equiv_mode()` to update the inode mode and drop an ACL that is equivalent to mode bits; it also clears setgid if the caller lacks group ownership/capability. Default ACLs are allowed only on directories. Non-NULL ACLs are serialized with `f2fs_acl_to_disk()` and stored through `f2fs_setxattr()`. On success, the VFS ACL cache is updated.

`f2fs_init_acl()` is called during inode creation. It obtains the parent directory default ACL, applies umask when no default ACL exists, clones and masks the inherited ACL against the new mode, installs a default ACL for new directories, installs an access ACL when the inherited ACL is not mode-equivalent, and marks the inode dirty synchronously after mode changes.

## State and Persistence Behavior

The persistent ACL xattr starts with `struct f2fs_acl_header` and version `F2FS_ACL_VERSION`. The first four ACL classes use compact `f2fs_acl_entry_short` records without an ID; named user and group entries use full `f2fs_acl_entry` records with little-endian UID/GID values in the initial user namespace. Access ACL changes may update `inode->i_mode`, `F2FS_I(inode)->i_acl_mode`, and cached ACL pointers. ACL xattrs are persisted by the common F2FS xattr layer and therefore participate in checkpointing and node/page writeback indirectly.

## Dependencies and Integration Points

This file depends on Linux POSIX ACL helpers, F2FS xattr APIs, F2FS inode dirtying, checkpoint error state, idmapped mount permission helpers, and `init_user_ns` UID/GID conversion. It is linked only when `CONFIG_F2FS_FS_POSIX_ACL` is enabled.

## Risks and Edge Cases

Parser risks include malformed length, wrong version, unexpected trailing bytes, unknown tags, and invalid short/full entry transitions. Setter risks include clearing `FI_ACL_MODE` correctly on serialization failure, default ACL rejection on non-directories, mode/ACL equivalence handling, and setgid stripping under idmapped mounts. Creation-time inheritance must release all ACL references on every error path.

## Test Signals

Tests should cover malformed ACL xattrs, empty ACLs, all POSIX ACL tag types, access ACLs equivalent and non-equivalent to mode bits, default ACL inheritance by files and directories, symlink creation, idmapped mount setgid behavior, checkpoint error returning `-EIO`, and ACL cache updates after set/remove.
