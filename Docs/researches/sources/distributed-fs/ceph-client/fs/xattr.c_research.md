# sources/distributed-fs/ceph-client/fs/xattr.c

## Purpose
This file implements Linux VFS extended attribute handling: namespace dispatch to filesystem xattr handlers, permission and LSM checks, syscall entry points for set/get/list/remove xattrs, POSIX ACL special routing, and the in-memory `simple_xattr` helper store used by simple filesystems. It is a policy and plumbing layer, not an on-disk xattr format implementation.

## Important APIs, Types, and Functions
- `xattr_resolve_name` walks `inode->i_sb->s_xattr` handler arrays, strips the matched prefix, validates exact-name handlers, and returns `-EOPNOTSUPP`, `-EINVAL`, or `-EIO` for unsupported, malformed, or bad-inode cases.
- `may_write_xattr` rejects immutable, append-only, or unmapped-id inodes before writes.
- `xattr_permission` centralizes VFS namespace policy: `security.*` and `system.*` defer to filesystem/LSM, `trusted.*` requires `CAP_SYS_ADMIN`, and `user.*` is limited by inode type plus sticky-directory ownership rules before falling through to `inode_permission`.
- VFS entry points include `vfs_setxattr`, `vfs_getxattr`, `vfs_listxattr`, `vfs_removexattr`, and lower-level locked/noperm variants such as `__vfs_setxattr_locked`, `__vfs_setxattr_noperm`, `__vfs_getxattr`, and `__vfs_removexattr_locked`.
- Syscall helpers include `path_setxattrat`, `path_getxattrat`, `path_listxattrat`, `path_removexattrat`, plus `setxattrat/getxattrat/listxattrat/removexattrat` and legacy `l*`/`f*` variants.
- `import_xattr_name`, `setxattr_copy`, and `kernel_xattr_ctx` move user names/values into kernel memory with `XATTR_SIZE_MAX` and flag validation.
- `generic_listxattr`, `xattr_list_one`, and `xattr_full_name` support filesystem handler implementations.
- The `simple_xattr*` family stores ephemeral xattrs in an `rhashtable`: allocation/free, get, set, limited set with atomic per-inode counters, list, lazy allocation, and teardown.

## Control Flow
Set operations import the user name/value, resolve either an fd or path with `AT_EMPTY_PATH` and symlink flags, acquire write access to the mount, route POSIX ACL names to ACL helpers, and otherwise call `vfs_setxattr`. `vfs_setxattr` converts file capabilities with `cap_convert_nscap`, locks the inode, performs namespace permission, LSM set checks, delegation breaking, and finally calls `__vfs_setxattr_noperm`; the noperm layer invokes filesystem handlers or `security_inode_setsecurity` fallback for `security.*`.

Get operations import the name, allocate a bounded buffer if the caller supplied a size, route ACLs separately, check permissions and LSM access, prefer active LSM `security.*` values via `security_inode_getsecurity`, and fall back to filesystem handler `get`. List operations call the inode `listxattr` op when present, otherwise list LSM security attributes; syscall wrappers cap `XATTR_LIST_MAX` and copy results back to userspace. Remove operations mirror set: write mount access, ACL special handling, VFS permission/LSM/delegation, handler `set(..., NULL, 0, XATTR_REPLACE)`, fsnotify, and LSM post-remove.

The `simple_xattr` helpers use RCU lookups for readers, externally serialized writers for set/replace/remove, and rhashtable walks for list. Set returns the replaced/removed object to be freed by the caller, with RCU delayed free when concurrent readers may still observe it.

## State and Persistence Behavior
The main VFS xattr paths mutate filesystem state only through filesystem xattr handlers, ACL helpers, and LSM security hooks. They also emit fsnotify notifications and update transaction-like mount write access around write syscalls. The simple xattr store is in-memory state: `struct simple_xattrs` owns an rhashtable of `struct simple_xattr` objects and can be lazily allocated/published with release semantics. It is not persistent unless a filesystem persists it separately.

## Dependencies and Integration Points
This file integrates with inode operation flags (`IOP_XATTR`), superblock `s_xattr` handler tables, idmapped mounts, VFS path lookup, file delegation breaking, POSIX ACL helpers, LSM hooks, audit, fsnotify, mount write accounting, RCU, rhashtable, and capability namespace conversion for `security.capability`.

## Risks and Edge Cases
Important risks are namespace policy regressions, missing delegation retry handling, incorrect LSM fallback for `security.*`, mishandling zero-length xattrs versus removal, user buffer truncation (`-ERANGE`/`-E2BIG`), `trusted.*` disclosure, bad inode behavior, and writer serialization requirements for simple xattrs. Lazy allocation uses `smp_store_release` but does not handle competing allocations beyond publishing one pointer, so callers must match expected serialization/lifetime rules.

## Test Signals
Relevant tests exercise all syscall variants including `*at` and `AT_EMPTY_PATH`, symlink-follow behavior, file descriptor paths, xattr namespace permissions, sticky directory `user.*` write denial, immutable/append-only denial, file capabilities under idmapped mounts, LSM `security.*` get/set/list behavior, POSIX ACL routing, delegation retry, list/get size probing, and simple_xattr create/replace/remove/list limits and RCU-safe teardown.
