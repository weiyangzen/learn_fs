# sources/distributed-fs/ceph-client/include/linux/xattr.h

## Purpose
Defines kernel extended-attribute interfaces for VFS and simple in-memory xattr storage. It provides handler dispatch contracts for filesystems, VFS get/set/list/remove declarations, POSIX ACL name detection, and rhashtable-backed `simple_xattrs` helpers used by pseudo filesystems.

## Important APIs, Types, and Functions
`is_posix_acl_xattr()` identifies access/default POSIX ACL xattr names. `struct xattr_handler` describes exact-name or prefix-based handlers with optional `list`, `get`, and `set` callbacks. VFS APIs include `__vfs_getxattr()`, `vfs_getxattr()`, `vfs_listxattr()`, `__vfs_setxattr()`, `__vfs_setxattr_noperm()`, locked set/remove variants, `vfs_setxattr()`, and `vfs_removexattr()`. `xattr_prefix()`, `xattr_full_name()`, `generic_listxattr()`, `vfs_getxattr_alloc()`, and `xattr_supports_user_prefix()` are helper APIs. Simple storage uses `struct simple_xattrs`, `struct simple_xattr`, `struct simple_xattr_limits`, `SIMPLE_XATTR_MAX_NR`, `SIMPLE_XATTR_MAX_SIZE`, allocation/free/get/set/list/add helpers, and cleanup `DEFINE_CLASS()` wrappers.

## Control Flow
Filesystem xattr operations match a requested name against handler name or prefix, call `xattr_handler_can_list()` for list visibility, and dispatch to handler callbacks through VFS helpers with mount idmap, dentry, inode, value buffer, size, and flags. Simple xattrs are initialized or lazily allocated, entries are allocated with flexible-array value storage, inserted into an rhashtable by name, replaced or removed through set helpers, and freed directly or by RCU callback.

## State and Persistence
VFS xattrs persist in filesystem-specific metadata, while `simple_xattrs` persist in an in-memory rhashtable owned by the containing object. `simple_xattr_limits` atomically tracks count and aggregate value bytes for bounded `user.*` storage. Individual `simple_xattr` objects persist name, size, value bytes, hash node, and RCU head until explicitly freed.

## Dependencies and Integration Points
Depends on slab allocation, spinlocks, MM types, rhashtable types, user namespaces/idmapped mounts, delegated inode handling, and UAPI xattr constants. Integrates with filesystems, security modules, POSIX ACL code, tmpfs/pseudo-filesystem helpers, and user-facing `getxattr`, `setxattr`, `listxattr`, and `removexattr` syscalls.

## Risks
Risks include handler prefix/name mismatches, listing attributes that should be hidden by permissions, idmap confusion in `set`, RCU lifetime bugs in simple storage, unbounded memory growth if limits are not used, and incorrect handling of `size == 0` probe semantics. POSIX ACL xattrs have special semantics and should not be treated as ordinary user metadata.

## Test Signals
Signals include xattr syscall tests, filesystem xattr and ACL suites, idmapped mount tests, LSM permission tests, simple_xattr limit tests, rhashtable/RCU debug coverage, and fault injection for allocation and replacement paths.
