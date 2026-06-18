# sources/distributed-fs/ceph-client/fs/jfs/acl.c

## Purpose
Implements JFS POSIX ACL get/set/inheritance using JFS extended attributes and transactions.

## Important APIs, types, and functions
`jfs_get_acl()` reads ACL xattrs and converts with `posix_acl_from_xattr()`. `__jfs_set_acl()` serializes ACLs and writes through `__jfs_setxattr()`. `jfs_set_acl()` wraps updates in `txBegin()`/`txCommit()` and `commit_mutex`, with optional `posix_acl_update_mode()`. `jfs_init_acl()` applies inherited ACLs during inode creation.

## Control flow
Get rejects RCU lookup, maps ACL type to xattr name, sizes and reads the EA, and returns null on `-ENODATA`. Set updates mode when access ACLs change permissions, writes ACL xattrs, dirty-marks changed mode, commits, and updates VFS ACL caches.

## State and persistence behavior
ACLs persist as JFS xattrs. In-memory ACL caches are refreshed on success; inode mode changes persist through the same transaction.

## Dependencies and integration points
Depends on Linux POSIX ACL helpers, JFS xattr internals, transaction manager, and inode commit locking.

## Risks and test signals
Test inheritance, chmod recalculation, ACL removal, remount persistence, RCU fallback, allocation failures, and transaction failure injection.
