<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Makefile -->
# sources/distributed-fs/ceph-client/fs/9p/Makefile

## Purpose
This Makefile builds the 9p filesystem object from VFS, session, fid, inode, xattr, address-space, and optional cache/ACL sources.

## Important APIs, types, and functions
It creates `9p.o` from `vfs_super.o`, `vfs_inode.o`, `vfs_inode_dotl.o`, `vfs_addr.o`, `vfs_file.o`, `vfs_dir.o`, `vfs_dentry.o`, `v9fs.o`, `fid.o`, and `xattr.o`, with optional `cache.o` and `acl.o`.

## Control flow
Kbuild links selected objects according to `CONFIG_9P_FS`, `CONFIG_9P_FSCACHE`, and `CONFIG_9P_FS_POSIX_ACL`.

## State and persistence
No runtime state. The file defines build composition only.

## Dependencies and integration points
It maps Kconfig symbols to implementation files and must stay aligned with declarations in `v9fs_vfs.h`, `cache.h`, `acl.h`, and `xattr.h`.

## Risks and test signals
Risks include missing optional objects or stale object lists. Test signals include module and built-in builds with cache/ACL toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Makefile -->
