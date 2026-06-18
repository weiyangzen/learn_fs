# sources/distributed-fs/ceph-client/fs/xfs/xfs_icache.c

## Purpose
`xfs_icache.c` implements XFS in-core inode allocation, lookup, recycling, reclaim, inode-cache walking, speculative preallocation garbage collection, deferred inode inactivation, and the inodegc shrinker. It is the main memory-lifetime and background-cleanup manager for XFS inodes. The full 2354-line file was read.

## Important APIs, Types, and Functions
Public APIs include `xfs_inode_alloc`, `xfs_inode_free`, `xfs_iget`, `xfs_trans_metafile_iget`, `xfs_metafile_iget`, reclaim functions (`xfs_reclaim_worker`, `xfs_reclaim_inodes`, `xfs_reclaim_inodes_nr`, `xfs_reclaim_inodes_count`, `xfs_inode_mark_reclaimable`), blockgc functions (`xfs_inode_set_eofblocks_tag`, `xfs_inode_clear_eofblocks_tag`, `xfs_inode_set_cowblocks_tag`, `xfs_inode_clear_cowblocks_tag`, `xfs_blockgc_worker`, `xfs_blockgc_stop`, `xfs_blockgc_start`, `xfs_blockgc_free_space`, `xfs_blockgc_flush_all`, `xfs_blockgc_free_dquots`, `xfs_blockgc_free_quota`), and inodegc functions (`xfs_inodegc_worker`, `xfs_inodegc_push`, `xfs_inodegc_flush`, `xfs_inodegc_stop`, `xfs_inodegc_start`, `xfs_inodegc_register_shrinker`).

Internal machinery includes per-AG radix tree tags `XFS_ICI_RECLAIM_TAG` and `XFS_ICI_BLOCKGC_TAG`, per-mount xarray marks, `xfs_perag_set_inode_tag`, `xfs_perag_clear_inode_tag`, `xfs_iget_cache_hit`, `xfs_iget_cache_miss`, `xfs_iget_recycle`, `xfs_reclaim_inode`, `xfs_icwalk_ag`, `xfs_icwalk`, `xfs_blockgc_igrab`, `xfs_blockgc_scan_inode`, `xfs_inode_free_eofblocks`, and `xfs_inode_free_cowblocks`.

## Control Flow
`xfs_iget` validates the inode number, finds the containing per-AG structure, and looks up the agino in the per-AG radix tree under RCU. Cache hits are screened for stale RCU objects, `XFS_INEW`, reclaim, inactivation, free-state mismatches, and reclaimable recycling. Cache misses allocate a fresh inode, map it to disk, optionally read the disk inode, check free/allocated state, preload the radix tree, lock as requested, and insert under the per-AG lock.

Reclaim starts when `xfs_inode_mark_reclaimable` either queues inodegc for inactivation or directly tags the inode reclaimable. Reclaim workers and shrinkers walk marked per-AG trees in batches, grab eligible inodes by setting `XFS_IRECLAIM`, flush AIL as needed, skip pinned or dirty inodes, remove clean reclaimable inodes from the radix tree, and free them through RCU.

Blockgc tags inodes with post-EOF or COW preallocations. Background or synchronous scans grab safe live inodes, filter by quota/user/group/project/min-size criteria, take IO/MMAP locks as needed, free EOF blocks, cancel idle COW reservations, clear tags when stale, and flush inodegc at the end of synchronous space reclamation.

Inodegc queues unreferenced inodes needing metadata cleanup to per-CPU llist work items. Workers set `XFS_INACTIVATING`, run `xfs_inactive`, mark the inode reclaimable, and record errors. Stop/start/flush routines coordinate delayed work, mount state, and shrinker-triggered throttling.

## State and Persistence Behavior
The file manages incore state: `struct xfs_inode` initialization, VFS inode state, fork memory, dquot attachment pointers, inode flags, sickness bits, per-AG radix tree membership, per-AG reclaimable counts, blockgc/reclaim xarray marks, delayed work state, per-CPU inodegc lists, and shrinker private data. It does not directly define on-disk formats, but it triggers persistent metadata updates through `xfs_inactive`, EOF/COW block freeing, transaction commits, dquot updates, and log/AIL pushes.

RCU freeing is used so lookup can safely see objects until grace periods complete. Inode numbers are set to zero before free to detect stale RCU lookups. Reclaim and blockgc tags bridge inode flags to per-AG scans and mount-level work scheduling.

## Dependencies and Integration Points
This file integrates with VFS inode allocation and `iput`, XFS inode buffer conversion, imap, transactions, quota/dquot code, AIL/log forcing, per-AG group management, radix trees/xarrays, reflink COW cancellation, bmap EOF freeing, health marking, metadata inodes, delayed workqueues, shrinker APIs, memory reclaim NOFS context, and mount tunables such as blockgc/inodegc enablement.

## Risks and Edge Cases
The highest-risk areas are lock/RCU ordering during cache lookup and reclaim, recycling reclaimable inodes, avoiding deadlock with inodegc while creating inodes, and not reclaiming sick inodes except during unmount/norecovery/shutdown. Dirty, pinned, flushing, or stale inodes must not be freed. Blockgc cannot free COW fork blocks under active writeback or direct I/O. Inodegc queue throttling must avoid NOFS deadlocks. Per-AG tag counts must stay balanced or background workers and shrinkers will either spin or miss reclaimable work.

## Test Signals
Tests should cover cache hit, miss, stale RCU lookup, inode recycling, `XFS_IGET_CREATE`, `XFS_IGET_INCORE`, noretry behavior, malformed free/allocated state detection, metadata inode type validation, reclaim of clean inodes, shutdown reclaim of dirty/sick inodes, blockgc EOF and COW cleanup under sync and background modes, quota-triggered blockgc filters, inodegc start/stop/flush races, shrinker-triggered inodegc throttling, unmount draining, and tag/count balance assertions.
