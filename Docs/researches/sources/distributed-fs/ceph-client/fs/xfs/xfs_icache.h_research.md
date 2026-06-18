# sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.h

## Purpose
`xfs_icache.h` declares the public inode cache, inode reclaim, block garbage collection, and inodegc interfaces used throughout XFS. The full 84-line header was read.

## Important APIs, Types, and Functions
`struct xfs_icwalk` packages inode-walk filters: flags, uid, gid, project id, minimum file size, and scan limit. Public flags include sync mode, uid/gid/project filtering, and minimum file size filtering. `XFS_IGET_*` flags control inode lookup creation, untrusted lookup, dontcache behavior, incore-only lookup, and noretry behavior.

The header declares inode allocation/free and lookup (`xfs_inode_alloc`, `xfs_inode_free`, `xfs_iget`), reclaim (`xfs_reclaim_worker`, `xfs_reclaim_inodes`, `xfs_reclaim_inodes_count`, `xfs_reclaim_inodes_nr`, `xfs_inode_mark_reclaimable`), blockgc (`xfs_blockgc_free_dquots`, `xfs_blockgc_free_quota`, `xfs_blockgc_free_space`, `xfs_blockgc_flush_all`, tag setters/clearers, worker stop/start), and inodegc (`xfs_inodegc_worker`, push/flush/stop/start, shrinker registration).

## Control Flow
Callers use `xfs_iget` to obtain in-core inodes under requested locks, use tag setters to schedule EOF/COW block cleanup, and use inodegc/reclaim interfaces to transition unused inodes through inactivation to reclaimable cache entries and final free.

## State and Persistence Behavior
The header exposes flags and APIs that drive incore inode state transitions. Persistence happens indirectly through the implementation when inode inactivation, EOF/COW cleanup, quota changes, or log pushes commit metadata updates.

## Dependencies and Integration Points
The declarations are used by VFS operation code, transaction code, reclaim shrinkers, quota allocation retry paths, unmount/remount code, speculative preallocation cleanup, and inode lifetime management.

## Risks and Edge Cases
Misusing `XFS_IGET_CREATE`, `XFS_IGET_UNTRUSTED`, or `XFS_IGET_INCORE` can produce incorrect corruption handling or lookup semantics. The header notes that blockgc synchronous scans must not be called while holding inode ILOCK/IOLOCK/MMAPLOCK. Filter flags must remain disjoint from private implementation flags.

## Test Signals
Build and API tests should validate flag combinations, incore-only lookup, no-retry lookup under contention, blockgc scans filtered by uid/gid/project/min-size, and shrinker registration during mount/unmount.
