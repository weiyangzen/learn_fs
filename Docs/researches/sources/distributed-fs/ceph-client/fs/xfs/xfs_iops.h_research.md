## sources/distributed-fs/ceph-client/fs/xfs/xfs_iops.h

Purpose: declares inode-operation helpers shared outside `xfs_iops.c`, primarily for inode setup, setattr, security initialization, listxattr, and atomic write reporting.

Important APIs and types: it forward-declares `struct xfs_inode` and declares `xfs_vn_listxattr`, `xfs_vn_setattr_size`, `xfs_inode_init_security`, `xfs_setup_inode`, `xfs_setup_iops`, `xfs_diflags_to_iflags`, `xfs_get_atomic_write_min`, `xfs_get_atomic_write_max`, and `xfs_get_atomic_write_max_opt`.

Control flow: this header does not execute code. It defines external call points for VFS-facing and inode-cache code that need to initialize or mutate VFS inode state and query atomic write limits.

State and persistence behavior: no direct state is stored here. Declared functions can initialize VFS inode fields, set persistent inode size, create security xattrs, and report derived device/filesystem limits.

Dependencies and integration: integrates inode cache setup, VFS setattr/listxattr paths, file/stat code, security hooks, and atomic write reporting. It depends on surrounding includes to provide Linux inode, dentry, iattr, idmap, and qstr types.

Risks and test signals: the header is small, so risks are mostly stale declarations and config-dependent type visibility. Build coverage across security, ACL, DAX, and atomic-write configurations plus runtime statx/setattr tests exercise the exported surface.
