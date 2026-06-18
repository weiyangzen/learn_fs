# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.h

Purpose: Declares metadata inode flagging and reservation interfaces.

Important APIs and types: mandatory flag masks `XFS_METAFILE_DIFLAGS` and `XFS_METADIR_DIFLAGS`; type string lookup; metadata flag set/clear; reservation critical/allocation/free/init APIs; external iget hooks `xfs_trans_metafile_iget` and `xfs_metafile_iget`.

Control flow: callers use set/clear helpers within transactions to change inode identity and reservation helpers from allocation/freeing paths. The external iget hooks are implementation-specific for kernel/userspace.

State and persistence: flag helpers persist inode metadata status and metatype. Reservation helpers manage mount-wide reserved/used/available counters and superblock free-space accounting through implementation in `xfs_metafile.c`.

Dependencies and integration: used by metadir create/load, inode verifier metadata checks, realtime metadata btree allocation, quota metadata inode loading, and repair tools.

Risks and test signals: mandatory flag masks must match verifier expectations. Tests should pair metadata flag creation with `xfs_dinode_verify_metadir`, and reservation tests should verify fdblocks/delalloc invariants before and after allocation and unmount.
