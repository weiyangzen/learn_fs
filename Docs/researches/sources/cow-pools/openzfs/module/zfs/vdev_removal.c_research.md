# File Research: sources/cow-pools/openzfs/module/zfs/vdev_removal.c

## Purpose
Implements OpenZFS vdev removal: auxiliary vdev removal, log vdev evacuation/removal, primary top-level singleton/mirror removal by copying allocated ranges elsewhere, recording indirect mappings, handling concurrent frees, canceling removals, and reporting removal progress.

## Main Responsibilities
- Disables/re-enables allocation for concrete top-level vdevs via `spa_vdev_noalloc()` and `spa_vdev_alloc()`.
- Removes hot spares and L2ARC devices from SPA auxiliary config nvlists.
- Evacuates log vdevs by passivating allocation, resetting logs, cleaning metadata, labeling removal, and replacing the slot with a hole vdev.
- Starts primary top-level removal by allocating indirect mapping/birth objects, recording `spa_removing_phys`, counting bytes to copy, dirtying MOS config state, and spawning `spa_vdev_remove_thread()`.
- Copies allocated segments from the removing vdev to replacement allocations, then syncs partial mappings through `vdev_mapping_sync()`.
- Handles frees during removal in `free_from_removing_vdev()`, including already-synced, in-flight, and not-yet-visited ranges.
- Completes successful removals by replacing the concrete vdev with an indirect vdev and destroying old space maps/ZAPs.
- Cancels removals by freeing mapped destinations, destroying mapping/birth objects, restoring allocation when allowed, and clearing removal state.

## Key Data And State
- `vdev_copy_arg_t`: per-copy-thread accounting for outstanding copy bytes and read/write error bytes.
- `spa_vdev_removal_t`: SPA removal state with range trees for not-yet-copied allocated segments, per-TXG deferred frees, new indirect mapping entries, bytes-done counters, max offsets to sync, a thread pointer, and synchronization primitives.
- Tunables:
  - `zfs_remove_max_copy_bytes`: memory budget for outstanding removal I/O.
  - `zfs_remove_max_segment`: largest requested destination allocation.
  - `zfs_removal_ignore_errors`: test/debug override allowing removal to continue after hard I/O errors.
  - `vdev_removal_max_span`: maximum free gap a remap segment may span.
  - `zfs_removal_suspend_progress`: test hook to pause removal progress.
- `DMU_POOL_REMOVING`: MOS ZAP entry persisted by `spa_sync_removing_state()`.

## Important Functions
- `vdev_passivate()` / `vdev_activate()`: toggle allocation state for a vdev and its log metaslab group while preserving pool progress guarantees.
- `vdev_remove_initiate_sync()`: sync-task initializer for primary device removal; creates indirect mapping state, initializes `spa_removing_phys`, counts bytes, dirties config blocks, and starts the copy thread.
- `spa_remove_init()`: pool-open recovery path that reloads active removal state and all indirect vdev mappings in newest-to-oldest order.
- `free_from_removing_vdev()`: synchronizing-context handler that updates original space maps, tracks in-flight frees, frees synced destination mappings, and adjusts progress accounting.
- `vdev_mapping_sync()`: sync task that persists new indirect mapping entries, records birth offsets, drains per-TXG deferred frees, and writes updated removal progress.
- `spa_vdev_copy_segment()` / `spa_vdev_copy_impl()`: allocate destination DVAs, create mapping entries, issue physical read/write zio trees, handle mirrors child-by-child, and shrink allocation size on `ENOSPC`.
- `spa_vdev_remove_thread()`: open-context background worker that walks metaslabs, loads allocated space maps, copies segments TXG by TXG, detects copy errors, and either completes or cancels removal.
- `vdev_remove_complete()` / `vdev_remove_complete_sync()`: convert the removed vdev to an indirect vdev and finish on-disk state cleanup.
- `spa_vdev_remove_cancel_sync()`: undo partial removal by freeing mapped destinations, dropping obsolete state, destroying indirect mapping objects, and reactivating allocation if the property permits.
- `spa_vdev_remove_top_check()`: enforces removal constraints: top-level concrete vdev, feature enabled, no active removal, sufficient free space, healthy DTLs, same ashift, no raidz/draid destinations, and simple mirror topology.
- `spa_vdev_remove()`: public dispatcher for spares, L2ARC, log vdevs, and primary top-level vdevs.

## Control Flow Notes
- Primary device removal begins under config locks but data evacuation happens in a background open-context thread; every copied range is committed through sync tasks.
- Mapping entries are append-only by increasing source offset. This ordering lets frees compare their offset against synced and in-flight max offsets.
- Removal requires same ashift across normal-class vdevs because copied ranges must not gain allocator padding that would desynchronize mapping sizes.
- Normal-class raidz/draid destination vdevs are rejected because segment copies are not block-boundary aware and cannot synthesize parity columns.
- Removal and pool checkpoint/discard are mutually exclusive.
- Successful completion waits for deferred frees, stops initialize/TRIM/autotrim/rebuild activity, tears down metaslabs, then relabels the removed physical vdev.

## Error Handling And Invariants
- The copy thread cancels removal on read/write errors unless `zfs_removal_ignore_errors` is set.
- `vdev_passivate()` refuses to disable allocation on the last usable normal-class allocating vdev.
- Cancel paths assert no new segment lists are pending, free all already-mapped destinations, and remove feature references.
- Sync-time assertions require `svr_bytes_done[]`, `svr_max_offset_to_sync[]`, and per-TXG lists to be drained before destruction.
- L2ARC and log removal stop TRIM/initialize activity before vdev teardown.

## Dependencies
Strongly coupled to SPA config locking, DMU transactions, DSL sync tasks, metaslab space maps, range trees, zio physical I/O, indirect vdev mapping/birth objects, ZAP metadata, vdev initialize/TRIM/rebuild code, and pool feature accounting.

## Research Notes
This is one of the highest-risk vdev state-machine files: correctness depends on TXG ordering, config-lock choreography, precise space accounting, and crash-resumable indirect mapping persistence. Any change should be tested across removal start, import/resume, concurrent frees, cancellation, error injection, log vdev removal, and aux vdev removal.
