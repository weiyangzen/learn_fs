# sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.h

## Purpose
`xfs_handle.h` declares the handle, by-handle attribute, and parent-pointer ioctl helpers implemented in `xfs_handle.c`.

## Important APIs, types, and functions
It declares attrlist/attrmulti by handle, path/fd-to-handle conversion, open/readlink by handle, single attrmulti operation, attr list on an inode, user handle-to-dentry decode, and getparents ioctl handlers.

## Control flow
`xfs_ioctl.c` dispatches legacy XFS handle and parent-pointer ioctls to these functions. Other XFS code can decode handles to dentries through the declared helper.

## State and persistence
The header owns no state. The declared functions work with persistent fsids, inode generation handles, xattrs, and parent pointer attributes.

## Dependencies and integration points
It depends on XFS ioctl ABI structures, VFS file/inode/dentry types, and user pointer annotations.

## Risks and test signals
Risks are ABI signature changes that break ioctl dispatch or compat paths. Test signals are build coverage and ioctl coverage for all declared operations.
