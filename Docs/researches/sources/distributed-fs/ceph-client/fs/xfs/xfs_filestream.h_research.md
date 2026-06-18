# sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.h

## Purpose
`xfs_filestream.h` declares the filestream allocation API and the predicate for deciding if an inode should use filestream placement.

## Important APIs, types, and functions
It declares mount/unmount lifecycle functions, `xfs_filestream_deassociate`, `xfs_filestream_select_ag`, and inline `xfs_inode_is_filestream`, which checks the mount-wide feature or the inode `XFS_DIFLAG_FILESTREAM` bit.

## Control flow
Allocation code calls `xfs_inode_is_filestream` to decide whether to route through `xfs_filestream_select_ag`; inode teardown can call `xfs_filestream_deassociate`; mount setup/teardown initializes and destroys the MRU cache.

## State and persistence
The header has no state. It exposes the runtime association machinery implemented in `xfs_filestream.c`; the inode flag used by the predicate is persistent inode metadata.

## Dependencies and integration points
It forward-declares XFS mount, inode, bmalloc, and allocation argument types and is included by allocation and inode lifecycle code.

## Risks and test signals
Risks are incorrect predicate behavior when mount-wide and inode-level filestream settings interact. Test signals include mount option behavior, inherited inode flags, and allocation path selection.
