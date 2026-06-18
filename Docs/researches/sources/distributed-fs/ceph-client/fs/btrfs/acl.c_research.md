# sources/distributed-fs/ceph-client/fs/btrfs/acl.c

## Purpose
Implements Btrfs POSIX ACL get/set operations on top of Btrfs xattrs. It translates VFS ACL requests into `system.posix_acl_access` and `system.posix_acl_default` xattr reads/writes and keeps the inode ACL cache consistent.

## Important APIs, Types, And Functions
`btrfs_get_acl(struct inode *inode, int type, bool rcu)` implements ACL retrieval. `__btrfs_set_acl(struct btrfs_trans_handle *trans, struct inode *inode, struct posix_acl *acl, int type)` writes or removes an ACL xattr, optionally within an existing transaction. `btrfs_set_acl(struct mnt_idmap *idmap, struct dentry *dentry, struct posix_acl *acl, int type)` is the VFS-facing setter that also updates inode mode for access ACLs.

## Control Flow
`btrfs_get_acl()` rejects RCU mode with `-ECHILD`, maps ACL type to the correct xattr name, queries xattr size, allocates a buffer when data exists, fetches the xattr value, and converts it through `posix_acl_from_xattr()`. Missing or zero-length ACLs return `NULL`; other negative xattr errors are propagated.

`__btrfs_set_acl()` validates type, rejects default ACLs on non-directories unless clearing, converts a non-null ACL to xattr bytes using `posix_acl_to_xattr()` under a NOFS allocation context when a transaction handle is held, and writes through `btrfs_setxattr()` or `btrfs_setxattr_trans()`. On success it calls `set_cached_acl()`.

`btrfs_set_acl()` updates `inode->i_mode` for access ACLs via `posix_acl_update_mode()`, calls the internal setter without an existing transaction, and restores the old mode if xattr writing fails.

## State And Persistence
ACLs are persisted as Btrfs xattrs. Successful writes update the in-memory ACL cache. Access ACL updates may change `inode->i_mode`; failures restore it. The NOFS allocation scope prevents transaction-held memory reclaim from re-entering filesystem paths.

## Dependencies And Integration Points
The file depends on POSIX ACL core helpers, xattr conversion helpers, Btrfs xattr APIs, Btrfs transactions, inode/dentry VFS structures, and `init_user_ns` for ACL xattr serialization. It is compiled only when `CONFIG_BTRFS_FS_POSIX_ACL` adds `acl.o`.

## Risks
ACL serialization occurs while transactions may be active, so allocation context matters. Mode update and xattr persistence must stay atomic from the VFS caller's perspective; otherwise inode permissions can diverge from stored ACLs. Default ACL handling must reject non-directories to avoid invalid metadata. RCU get support is intentionally absent and must return `-ECHILD` so VFS retries in sleepable context.

## Test Signals
Tests should create, read, replace, and remove access and default ACLs; verify mode changes from `posix_acl_update_mode()`; reject default ACLs on regular files; exercise missing ACL xattrs; inject xattr write failures to confirm mode rollback; and run ACL operations during transaction-heavy workloads.
