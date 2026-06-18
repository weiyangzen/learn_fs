# File Research: sources/cow-pools/openzfs/module/zfs/vdev_indirect.c

## Purpose

Implements indirect vdevs, which represent removed top-level vdevs whose old block-pointer locations must be remapped to new locations elsewhere in the pool. It also implements obsolete-space accounting and condensing for indirect mappings, and handles split-block reads/reconstruction when one old DVA maps to multiple new segments.

## Main APIs And Entry Points

- Obsolete marking and syncing: `vdev_indirect_mark_obsolete()`, `spa_vdev_indirect_mark_obsolete()`, `vdev_indirect_sync_obsolete()`, `vdev_obsolete_sm_object()`, and `vdev_obsolete_counts_are_precise()`.
- Condense lifecycle: `vdev_indirect_should_condense()`, `spa_condense_indirect_start_sync()`, `spa_condense_indirect_thread()`, `spa_condense_indirect_generate_new_mapping()`, `spa_condense_indirect_commit_entry()`, `spa_condense_indirect_commit_sync()`, `spa_condense_indirect_complete_sync()`, `spa_condense_init()`, `spa_condense_fini()`, and `spa_start_indirect_condensing_thread()`.
- Indirect remapping: `vdev_indirect_remap()`, `vdev_indirect_mapping_duplicate_adjacent_entries()`, and `vdev_indirect_gather_splits()`.
- I/O path: `vdev_indirect_io_start()`, `vdev_indirect_child_io_done()`, `vdev_indirect_io_done()`, `vdev_indirect_read_all()`, `vdev_indirect_reconstruct_io_done()`, repair/checksum helpers, and `vdev_indirect_ops`.

## Data Structures

`indirect_vsd_t` is attached to each ZIO and records whether a block is split, whether reconstruction is active, the number of unique reconstruction combinations, attempt limits, and the list of split segments. Each `indirect_split_t` describes one contiguous remapped segment with its target top-level vdev, offset, size, child-copy array, and unique-child list. `indirect_child_t` stores per-copy ABD data, target child vdev, duplicate markers, and read/DTL error state.

The condense path uses `spa_condensing_indirect_t` and its on-disk `spa_condensing_indirect_phys_t` to track the vdev being condensed, the next mapping object, the previous obsolete spacemap, and per-TXG lists of new mapping entries awaiting sync-context commit.

## Control Flow

Obsolete tracking appends newly obsolete ranges to an in-memory range tree and dirties the vdev. Syncing creates the obsolete spacemap object on demand, writes the accumulated ranges as `SM_ALLOC` entries, and clears the in-memory tree. Condense decisions require the feature to be enabled, no other condense in progress, a quiescent indirect vdev rather than a still-removing vdev, and either sufficient obsolete percentage of mapped bytes or an oversized obsolete spacemap.

Condensing starts in sync context by creating a new mapping object, moving the current obsolete spacemap into `scip_prev_obsolete_sm_object`, removing the vdev's obsolete spacemap ZAP entry so new obsolete ranges go to a fresh map, recording condense state in the MOS, and waking the condense zthr. The zthr opens the previous obsolete spacemap, loads obsolete counts, folds spacemap entries into those counts, resumes from the new mapping's max offset if needed, and emits only entries that are not fully obsolete. Completion switches `vd->vdev_indirect_mapping` under `vdev_indirect_rwlock`, frees the old mapping and previous obsolete spacemap, removes MOS condense state, destroys in-memory condense state, and dirties pool config.

`vdev_indirect_remap()` is the central mapping walker. It uses a stack of remap segments so nested indirect mappings can be followed without recursion. For each segment it takes the target indirect vdev's mapping rwlock, duplicates the relevant adjacent mapping entries, drops the lock, then calls the supplied callback for each mapped concrete or indirect target segment. This lets condensing replace mapping objects without waiting for the entire remap callback chain to finish.

I/O startup gathers split segments. If the remap is not split, the child ZIO receives the original BP so normal checksum and mirror retry behavior applies. For split blocks, reads/writes issue per-segment child I/Os without per-segment checksums. Scrub/resilver reads all mirror copies for every split immediately; normal split reads first read one copy per split, verify the whole-block checksum in `vdev_indirect_io_done()`, and if verification fails, read all copies and retry reconstruction.

Reconstruction de-duplicates identical child copies per split, computes the product of unique choices, and either enumerates all combinations or samples random combinations up to `zfs_reconstruct_indirect_combinations_max`. A valid combination is copied into the parent ABD and verified by the whole-block checksum. Successful reconstruction issues self-heal writes to incorrect copies and posts checksum errors; total failure reports checksum errors for all read copies.

## Dependencies And Integration

This file integrates with DMU/MOS object management, ZAP, space maps, DSL sync tasks, zthr threads, pool config locks, vdev removal/remap, vdev indirect mapping helpers, ABDs, ZIO checksum/reporting paths, DTLs, mirror vdev semantics, and SPA feature accounting for obsolete counts. Module parameters tune condense thresholds, commit-entry delay, and split reconstruction attempt limits.

## Risks And Invariants

- Mapping entries are copied while holding `vdev_indirect_rwlock`; callbacks must operate on the copy because condense may swap the mapping object later.
- Split-block reconstruction can be combinatorially expensive; the configured cap intentionally trades exhaustive recovery for bounded CPU time on large combinations.
- Condense restart depends on durable `DMU_POOL_CONDENSING_INDIRECT` state plus max-offset resume from the partially written new mapping.
- Sync-context and open-context boundaries are strict: object creation/deletion and mapping commits happen through DMU transactions/sync tasks, while the zthr performs long-running scan work.
- Obsolete counts must never exceed mapped entry size; fully obsolete entries are omitted from new mappings.
- Non-split indirect I/O intentionally preserves normal vdev checksum behavior by passing the original BP to the child I/O.

## Summary

`vdev_indirect.c` is the removed-vdev remap engine. It translates old DVAs to current pool locations, tracks and condenses obsolete mapping entries, and reconstructs rare split blocks whose pieces may have multiple mirrored copies.
