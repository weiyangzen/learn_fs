# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_xattr.c

## Purpose
Implements Linux extended attribute and POSIX ACL support for ZFS. It bridges Linux name/value xattrs to either ZFS directory-based xattrs or SA/spill-block xattrs, handles namespace-specific permissions, initializes security labels, stores POSIX ACLs as xattrs, and provides compatibility behavior for legacy unprefixed user attributes.

## Main APIs and Data
- `zpl_xattr_handlers[]` exports security, trusted, user, and optional POSIX ACL handlers.
- `zpl_xattr_list()` lists visible xattrs from SA storage and xattr directories.
- `zpl_xattr_get()` and `zpl_xattr_set()` are shared internal get/set engines.
- Directory storage helpers: `zpl_xattr_list_dir()`, `zpl_xattr_get_dir()`, `zpl_xattr_set_dir()`.
- SA storage helpers: `zpl_xattr_list_sa()`, `zpl_xattr_get_sa()`, `zpl_xattr_set_sa()`.
- POSIX ACL entry points include `zpl_set_acl()`, `zpl_get_acl()`, `zpl_init_acl()`, and `zpl_chmod_acl()`.
- Tunable `zfs_xattr_compat` controls whether new user xattrs are written in legacy unprefixed format.

## Control Flow
Listing creates an `xattr_filldir_t`, enters the zfsvfs/znode, takes `z_xattr_lock`, lists SA xattrs first when enabled, then lists xattr-directory entries. Each candidate name is filtered by `zpl_xattr_permission()`, which dispatches to namespace handlers and maps unknown non-FreeBSD names into the Linux `user.` namespace for compatibility.

Get first tries SA storage when dataset/znode state allows it. If the name is absent there, it falls back to the xattr directory. Directory get looks up the hidden xattr directory, then the attribute object, checks size, and reads with `zfs_read()`. SA get loads cached nvlist data with `zfs_sa_get_xattr()` and returns byte-array values.

Set takes the writer xattr lock and first determines whether the name exists in SA, directory, both, or neither so `XATTR_CREATE`/`XATTR_REPLACE` semantics are honored. It prefers SA when configured and possible, removes stale duplicates from the other backend after successful writes, and falls back to directory storage when SA size limits are exceeded or unsupported. Directory set creates/removes/truncates hidden xattr files and updates parent ctime/dirty state. SA set mutates the cached nvlist and persists through `zfs_sa_set_xattr()`, dropping the cache on error.

Namespace handlers apply Linux xattr rules:
- `user.*` requires dataset xattr support and rejects forbidden namespace forms; get tries prefixed then unprefixed for compatibility; set clears the alternate representation before writing the configured representation.
- `trusted.*` requires `CAP_SYS_ADMIN`.
- `security.*` is available for LSMs and file capabilities; security initialization stores labels from `security_inode_init_security()`.
- POSIX ACL handlers convert between Linux ACL xattr format and `struct posix_acl`, validate ownership/capability, and update inode mode where ACL equivalence requires it.

## Integration Points
This file connects Linux xattr/ACL VFS hooks to ZFS SA, hidden xattr directories, nvlist encoding, security modules, idmapped owner checks, inode dirtying, and create/chmod paths in `zpl_inode.c`.

## Invariants and Edge Cases
- SA xattrs are limited by `DXATTR_MAX_ENTRY_SIZE` and `DXATTR_MAX_SA_SIZE`.
- A warning is emitted if the same xattr exists in both SA and directory backends.
- Directory xattrs may create real hidden inodes not referenced by dentries.
- FreeBSD system namespace xattrs are hidden from Linux listing.
- Unknown namespace names are exposed as `user.*` for cross-platform compatibility.
- Symlinks cannot receive POSIX ACLs.
- Default ACLs only apply to directories.
- ACL freeing is delayed through a lockless multi-producer/single-consumer queue to avoid RCU/lifetime issues with kernel ACL caching.

## Risks and Testing Signals
Test SA and directory xattr get/set/list/remove, backend fallback and duplicate cleanup, `XATTR_CREATE`/`XATTR_REPLACE`, `xattr=off`, legacy `zfs_xattr_compat`, FreeBSD namespace hiding, trusted/security permission rules, SELinux label initialization, POSIX ACL inheritance/chmod/default ACLs, large xattr limits, and cache invalidation after SA persistence errors.
