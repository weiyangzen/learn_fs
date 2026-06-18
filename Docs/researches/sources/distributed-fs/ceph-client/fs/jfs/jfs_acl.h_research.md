# sources/distributed-fs/ceph-client/fs/jfs/jfs_acl.h

## Purpose
Declares JFS ACL entry points and provides a no-op ACL initialization path when ACL support is disabled.

## Important APIs, types, and functions
With `CONFIG_JFS_POSIX_ACL`, declares `jfs_get_acl()`, `jfs_set_acl()`, and `jfs_init_acl()`. Without ACL support, inline `jfs_init_acl()` returns success.

## Control flow
Creation paths can call `jfs_init_acl()` unconditionally; inode operation tables include ACL hooks only under config guards.

## State and persistence behavior
No state; gates whether ACL xattrs are initialized and maintained.

## Dependencies and integration points
Integrates VFS inode/dentry/idmap ACL operations with JFS transaction-aware ACL implementation.

## Risks and test signals
Build and creation tests should cover ACL enabled and disabled kernels.
