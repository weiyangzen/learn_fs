## sources/distributed-fs/ceph-client/fs/orangefs/symlink.c

Purpose: this small file publishes the inode operation table for OrangeFS symlinks. It binds generic VFS symlink reading to OrangeFS metadata, xattr, permission, setattr, getattr, and timestamp helpers.

Important APIs and functions: `orangefs_symlink_inode_operations` sets `.get_link = simple_get_link`, `.setattr = orangefs_setattr`, `.getattr = orangefs_getattr`, `.listxattr = orangefs_listxattr`, `.permission = orangefs_permission`, and `.update_time = orangefs_update_time`.

Control flow: symlink target contents are prepared elsewhere during inode getattr/copy from the OrangeFS downcall into `orangefs_inode->link_target`; `simple_get_link()` then returns the cached `inode->i_link`. Metadata and permission operations delegate to common OrangeFS inode/xattr paths.

State and persistence behavior: this file owns no storage. Symlink target state lives in the OrangeFS private inode and is populated when `orangefs_inode_getattr()` handles a new symlink. Updates and timestamps are persisted through shared OrangeFS setattr/upcall logic.

Dependencies and integration points: depends on `protocol.h`, `orangefs-kernel.h`, and `orangefs-bufmap.h` for declarations. The operation table is selected by OrangeFS inode construction code for `S_IFLNK` objects.

Risks and test signals: correctness depends on new symlink inodes having `i_link` set before VFS follows the link and on stale symlink target detection in `orangefs_inode_is_stale()`. Tests should cover symlink lookup/follow, target length boundary at `ORANGEFS_NAME_MAX`, stale target replacement returning `-ESTALE`, listxattr on symlinks returning the expected unsupported behavior from xattr code, and timestamp/setattr propagation.
