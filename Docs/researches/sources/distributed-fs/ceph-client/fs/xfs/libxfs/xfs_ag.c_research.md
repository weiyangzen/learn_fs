# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.c

## Purpose
This file manages XFS allocation group lifecycle and geometry: per-AG allocation/free, initialization of in-core counters from AG headers, AG header construction for growfs, tail-AG shrink/extend operations, grow delta calculation, and reporting AG geometry.

## Important APIs and Functions
- `xfs_initialize_perag_data` reads every AGF/AGI, totals free blocks, freelist blocks, btree blocks, inode counts, validates counters, updates the in-core superblock, and reinitializes percpu counters.
- `xfs_initialize_perag`, `xfs_free_perag_range`, and `xfs_perag_alloc` create or free `struct xfs_perag` instances via generic `xfs_group` infrastructure.
- `xfs_ag_block_count`, `xfs_agino_range`, and `xfs_update_last_ag_size` compute AG block and inode ranges, especially for a short last AG after recovery/growfs.
- `xfs_ag_init_headers` initializes secondary superblocks, AGF/AGFL/AGI headers, and btree roots for new AGs.
- `xfs_ag_shrink_space` removes free space from the end of the last AG, updates AGF/AGI length, reinitializes reservations, and adjusts perag geometry.
- `xfs_growfs_compute_deltas` computes new AG count and data-block delta under minimum/maximum AG constraints.
- `xfs_ag_extend_space` extends the last AG, frees the new space into rmap/free-space metadata, and updates perag geometry.
- `xfs_ag_get_geometry` fills `xfs_ag_geometry` from AGF/AGI and in-core health/free-space accounting.

## Control Flow
Mount initialization allocates perag structures, then `xfs_initialize_perag_data` forces AGF/AGI reads so lazy superblock counters can be reconstructed from authoritative per-AG metadata. Growfs creates perag structures and writes new headers using uncached buffers, with initializer callbacks for each header/root type gated by rmap, finobt, and reflink features. Shrink first validates AGF/AGI consistency and inode-cluster safety, temporarily frees per-AG reservations, allocates the terminal range exactly to remove it from free-space btrees, rechecks reservations, and only then commits AG length reductions.

## State and Persistence Behavior
Persistent state includes AGF, AGFL, AGI, secondary superblocks, and btree root blocks written during grow/shrink/extend. In-core state includes `xfs_perag` counters, geometry, blockgc work, inode cache roots, opstate bits, and superblock/percpu counters. New secondary superblocks are marked `sb_inprogress` until growfs activation completes, giving recovery/repair a signal for incomplete growth.

## Dependencies and Integration Points
This file depends on allocation btrees, rmap/refcount/inode btrees, transactions, deferred ops, health marking, buffer operations, mount geometry, blockgc, and generic group reference management. It is used by mount, growfs, shrink, geometry ioctl paths, and recovery.

## Risks and Edge Cases
Counter reconstruction rejects obviously impossible `fdblocks` or inode totals to avoid mounting corrupt AGFs. Growfs must use uncached buffers because new AG headers are beyond current valid filesystem space. Shrink is risky: it must avoid inode clusters beyond the new end, handle ENOSPC when reservations cannot be reestablished, roll transactions while holding AGF/AGI to avoid allocation races, and force shutdown on reservation repair failure.

## Test Signals
Exercise mount counter rebuild after lazy counters, corrupted AGF/AGI lengths, growfs with rmap/finobt/reflink combinations, interrupted growfs recovery, shrink of a full or fragmented tail AG, shrink with inode clusters near the end, reservation reinit ENOSPC paths, geometry ioctls, and health/sick marking under verifier failures.
