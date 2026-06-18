# sources/distributed-fs/ceph-client/fs/xfs/xfs_inode.h

## Purpose
`xfs_inode.h` defines the core in-memory XFS inode structure, inode flag and locking contracts, convenience helpers, and public inode operation prototypes. The full 679-line header was read.

## Important APIs, Types, and Functions
`typedef struct xfs_inode` embeds mount pointer, dquot pointers, inode number and disk mapping, data/attr/COW forks, log item pointer, locks, pin count, inodegc list node, health state, flags, delayed block count, disk size, block counts, project id, extent hints, fork offset, metadata type, dinode flags, unlinked-list pointers, embedded VFS inode, and pending I/O completion work.

Important inline helpers include `XFS_I`, `VFS_I`, `VFS_IC`, `XFS_ISIZE`, `xfs_new_eof`, `xfs_iflags_*`, `xfs_is_reflink_inode`, `xfs_is_metadir_inode`, `xfs_is_internal_inode`, `xfs_is_zoned_inode`, `xfs_is_cow_inode`, `xfs_inode_has_filedata`, `xfs_inode_has_cow_data`, `xfs_inode_has_bigtime`, `xfs_inode_has_large_extent_counts`, `xfs_inode_buftarg`, atomic write capability checks, `xfs_finish_inode_setup`, and `xfs_setup_existing_inode`.

The header defines incore flags (`XFS_IRECLAIM`, `XFS_ISTALE`, `XFS_IRECLAIMABLE`, `XFS_INEW`, `XFS_IFLUSHING`, `XFS_NEED_INACTIVE`, `XFS_INACTIVATING`, `XFS_IREMAPPING`, and more), lock flags for IOLOCK/ILOCK/MMAPLOCK modes, lockdep subclass fields, and layout break reasons.

## Control Flow
Most source files use this header to transition between XFS and VFS inodes, test or mutate inode flags under `i_flags_lock`, choose forks, determine data size semantics, choose data/realtime devices, and enforce lock ordering. Public prototypes expose namespace operations, locking, truncation, inode free, log force, inactivation, unlinked-list reload, remap locks, fork-zap checks, block accounting, and create-time dquot allocation.

## State and Persistence Behavior
`struct xfs_inode` is the authoritative incore shadow of persistent dinode state and related runtime-only state. Persistent fields include disk size, block counts, forks, project id, extent hints, flags, creation time, metadata type, unlinked pointers, and VFS inode mode/uid/gid/nlink/times/generation. Runtime-only fields include locks, health bits, reclaim/inactivation/remap/flush flags, dquot pointers, COW fork pointer, delayed block counters, and workqueue state.

## Dependencies and Integration Points
The header is included across nearly all XFS subsystems: VFS operations, inode cache, inode item logging, bmap, directory, attributes, reflink, quota, recovery, health, realtime, metadata directory, DAX/layout code, and writeback. It also encodes lock ordering assumptions used by lockdep and by multi-inode transaction code.

## Risks and Edge Cases
Flag operations must hold `i_flags_lock` unless documented otherwise. `XFS_ISIZE` differs for regular files because VFS `i_size` can be newer than `i_disk_size`; using the wrong size risks stale exposure or missed truncation. Lock subclass bit fields are tight due to lockdep limits. Internal inode detection changes with metadata directory support. COW and realtime/zoned helpers affect allocation and write semantics; mistakes can free or write the wrong fork/device.

## Test Signals
Test coverage should include flag transition assertions, lockdep validation for nested locks, regular versus non-regular size behavior, internal inode detection with and without metadata directories, fork size helpers with and without attr forks, COW/reflink/zoned predicates, atomic write capability, and inode setup completion clearing `XFS_INEW`.
