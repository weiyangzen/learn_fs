# sources/distributed-fs/ceph-client/fs/ocfs2/acl.c

## Purpose
`acl.c` implements OCFS2 POSIX ACL conversion, retrieval, update, chmod adjustment, and new-inode ACL inheritance. ACLs are stored as OCFS2 xattrs and coordinated through inode locks, xattr semaphores, and journal transactions.

## Important APIs and Functions
`ocfs2_acl_from_xattr()` converts little-endian on-disk ACL entries to `posix_acl`. `ocfs2_acl_to_xattr()` serializes ACLs. `ocfs2_get_acl_nolock()` reads access/default ACL xattrs. `ocfs2_acl_set_mode()` updates inode mode and ctime in memory and dinode, starting a transaction if needed. `ocfs2_set_acl()` writes ACL xattrs and updates cache. Public entry points are `ocfs2_iop_get_acl()`, `ocfs2_iop_set_acl()`, `ocfs2_acl_chmod()`, and `ocfs2_init_acl()`.

## Control Flow
ACL get rejects RCU lookup, checks the POSIX ACL mount option, locks the inode, reads under `ip_xattr_sem`, and releases resources. ACL set takes an exclusive lock; access ACLs update mode before xattr write. Chmod reads the existing access ACL, rewrites it for the new mode, and stores it. New inode initialization inherits the parent's default ACL or applies umask, then stores default/access ACLs as needed.

## State and Persistence Behavior
ACL values persist in OCFS2 xattrs. Mode and ctime persist in the dinode through journaled writes. The VFS ACL cache is updated after successful writes. New inode initialization can persist mode changes even without an ACL xattr.

## Dependencies and Integration Points
The file depends on OCFS2 xattr, inode locking, journal, allocation context, dinode, masklog, and POSIX ACL APIs. It is compiled into `ocfs2.o` and declared by `acl.h`.

## Risks
Distributed locks, xattr semaphores, buffer heads, and journal handles must remain balanced. ACL id conversion uses the initial user namespace. Error paths during initialization must release ACL references and preserve transaction consistency.

## Test Signals
Test ACL get/set/remove, symlink rejection, default ACL inheritance, umask fallback, chmod rewriting, no-ACL mounts, journal aborts, clustered concurrent updates, and allocation-context growth.
