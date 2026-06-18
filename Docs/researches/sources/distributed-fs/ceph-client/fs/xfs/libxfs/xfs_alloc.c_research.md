# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.c

## Purpose
This file is the core XFS data-device free-space allocator. It manages AG free-space btrees, AGFL refill/drain, AGF/AGFL verification, extent allocation strategies, extent freeing and coalescing, reservation-aware accounting, busy extent avoidance, delayed frees, and allocator query helpers.

## Important APIs, Types, and Functions
- Geometry/accounting helpers: `xfs_agfl_size`, `xfs_refc_block`, `xfs_prealloc_blocks`, `xfs_alloc_set_aside`, `xfs_alloc_ag_max_usable`, `xfs_alloc_compute_maxlevels`, `xfs_alloc_longest_free_extent`, and `xfs_alloc_min_freelist`.
- Btree helpers: `xfs_alloc_lookup_{eq,ge,le}`, `xfs_alloc_update`, `xfs_alloc_btrec_to_irec`, `xfs_alloc_check_irec`, `xfs_alloc_get_rec`, `xfs_alloc_fixup_trees`, and longest-record maintenance.
- Allocation search structures/functions: `struct xfs_alloc_cur`, `xfs_alloc_cur_setup/check/finish/close`, `xfs_alloc_ag_vextent_exact`, `xfs_alloc_ag_vextent_near`, `xfs_alloc_ag_vextent_size`, and small/freelist fallback handling.
- Public allocation APIs: `xfs_alloc_vextent_this_ag`, `xfs_alloc_vextent_near_bno`, `xfs_alloc_vextent_exact_bno`, `xfs_alloc_vextent_start_ag`, and `xfs_alloc_vextent_first_ag`.
- Free path APIs: `xfs_free_ag_extent`, `__xfs_free_extent`, `xfs_free_extent_fix_freelist`, `xfs_free_extent_later`, and autoreap helpers.
- AGFL/AGF APIs: `xfs_alloc_fix_freelist`, `xfs_alloc_get_freelist`, `xfs_alloc_put_freelist`, `xfs_alloc_log_agf`, `xfs_read_agf`, `xfs_alloc_read_agf`, AGF/AGFL buffer ops and verifiers.
- Query helpers: `xfs_alloc_query_range`, `xfs_alloc_query_all`, `xfs_alloc_has_records`, and `xfs_agfl_walk`.

## Control Flow
Allocation begins by validating and normalizing `struct xfs_alloc_arg` in `xfs_alloc_vextent_check_args`, including transaction AG ordering constraints via `t_highest_agno`. The caller-specific wrapper prepares an AG with `xfs_alloc_vextent_prepare_ag`, which initializes/locks AGF state and calls `xfs_alloc_fix_freelist`. That function checks reservation-aware availability, resets corrupt AGFL indexes if needed, drains surplus AGFL blocks to deferred frees, and refills a short AGFL by allocating free-space extents and adding each block to the freelist.

Exact allocations search the bnobt for the containing free extent, trim busy ranges, and remove the requested range from both btrees. Near allocations run locality-aware parallel searches across cntbt and bnobt, retrying after busy-extent flushes when necessary. Anywhere allocations primarily search cntbt for the largest viable extent, scan for a better aligned candidate if needed, and fall back to small allocations or single AGFL blocks. Successful allocations update btrees, set `args->fsbno`, optionally add reverse mappings, decrement AGF/freeblock counters, debit reservations, and update stats.

Freeing fixes the freelist first, validates the extent against AGF length, optionally removes rmap ownership, finds left/right neighboring free extents in bnobt, coalesces with either or both neighbors, updates cntbt and bnobt, refreshes `agf_longest`, increments counters, replenishes reservations, and inserts a busy extent so recently freed blocks are not immediately reused unsafely.

## State and Persistence Behavior
Persistent state includes AGF fields, AGFL entries, bnobt/cntbt records, rmap records, transaction log items, deferred extent free intents, and buffer checksums/LSNs. In-core state includes perag cached freeblock/freelist/btree counters, btree levels, `m_allocbt_blks`, transaction highest-AG tracking, busy extent lists, allocator workqueue/cache state, and reservation counters. Deferred frees are persisted as EFI/EFD intent items so recovery can complete or cancel frees.

## Dependencies and Integration Points
The allocator integrates with XFS btree core, allocation btree ops, rmap updates, extent busy tracking, transactions and log item types, AG reservation code, AG/perag helpers, health/sick marking, buffer verifiers, error injection, tracepoints, deferred operation infrastructure, and slab caches for extent-free items. It is called by file block mapping, metadata allocation, grow/shrink, repair/scrub, and log recovery paths.

## Risks and Edge Cases
Primary risks are bnobt/cntbt divergence, stale `agf_longest`, AGFL count/index corruption, busy extent reuse races, transaction AG lock ordering deadlocks, incorrect reservation accounting, rmap update mismatches, and silent block-device write loss. The code has many corruption assertions and sick marking paths, but failure handling must preserve `NULLFSBLOCK` on allocation failure and release AGF/AGFL buffers correctly. AGFL reset intentionally leaks blocks to keep the filesystem online and requires repair.

## Test Signals
High-value tests include fragmented free-space allocation, exact/near/anywhere allocation with alignment/mod/prod constraints, delayed allocation under ENOSPC, AGFL refill/drain at low space, busy extent flush and retry, concurrent frees and allocations, reverse-map enabled filesystems, reflink/refcount pressure, transaction roll/deadlock avoidance across AGs, forced verifier failures, dmflakey stale AGF reads, EFI/EFD log recovery, discard skip paths, and scrub queries over free-space btrees.
