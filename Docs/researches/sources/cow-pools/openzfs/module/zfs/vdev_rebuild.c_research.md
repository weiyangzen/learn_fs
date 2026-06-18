# File Research: sources/cow-pools/openzfs/module/zfs/vdev_rebuild.c

## Scope

Sequential resilver/device rebuild implementation for OpenZFS top-level vdevs. This file reconstructs allocated logical address ranges in LBA/metaslab order, primarily for mirror and dRAID-style rebuilds, and persists progress in each top-level vdev ZAP.

## Main Interfaces

- `vdev_rebuild(vdev_t *vd, uint64_t txg)`: start a sequential rebuild or request a reset of an active one.
- `vdev_rebuild_load(vdev_t *vd)`: load on-disk rebuild state from `VDEV_TOP_ZAP_VDEV_REBUILD_PHYS`.
- `vdev_rebuild_restart(spa_t *spa)`: restart active rebuild threads after import/load.
- `vdev_rebuild_stop_all()` / `vdev_rebuild_stop_wait()`: stop rebuild threads while leaving active state resumable.
- `vdev_rebuild_active(vdev_t *vd)`: report whether any top-level vdev is rebuilding.
- `vdev_rebuild_txgs()`: expose the min/max TXG range covered by the rebuild.
- `vdev_rebuild_get_stats()`: return per-top-level rebuild status and progress counters.
- `vdev_rebuild_clear_sync()`: clear completed/canceled rebuild status.
- Tunables: `zfs_rebuild_max_segment`, `zfs_rebuild_vdev_limit`, `zfs_rebuild_scrub_enabled`.

## State And Control Flow

The on-disk state is `vdev_rebuild_phys_t` stored in the top-level vdev ZAP. Active rebuilds also use in-memory state in `vdev_rebuild_t`, including scan offsets per TXG, pass counters, in-flight byte accounting, current metaslab/range tree, and a rebuild thread pointer on the top-level vdev.

Starting a rebuild sets `vd->vdev_rebuilding`, increments `SPA_FEATURE_DEVICE_REBUILD`, initializes `vrp_rebuild_state = VDEV_REBUILD_ACTIVE`, records TXG bounds from `vdev_resilver_needed()`, writes the ZAP entry, logs history/events, and creates `vdev_rebuild_thread()`.

The rebuild thread cancels any scrub, creates a range tree, clears rebuild byte counters, then walks metaslabs in order. For each metaslab it disables allocations, waits for outstanding allocating ranges to sync, loads allocated ranges from the space map, overlays unflushed alloc/free trees, removes already rebuilt offsets, and issues rebuild I/O for the remaining allocated ranges. After each metaslab it waits for the last rebuild TXG to sync before re-enabling the metaslab.

`vdev_rebuild_ranges()` splits each allocated range into legal chunks using the top-level vdev op’s `vdev_op_rebuild_asize()` method. `vdev_rebuild_range()` builds a synthetic checksum-disabled block pointer for the target range, skips it if DTLs do not require resilvering, rate-limits queued bytes, schedules an update sync task for progress, and issues a raw resilver read with `ZIO_PRIORITY_REBUILD`. The I/O callback frees the ABD, records errors, releases in-flight byte accounting, wakes waiters, and exits the config lock held for the I/O.

Completion schedules one of three sync tasks: complete, cancel, or reset. Successful completion marks state complete, sets end time, reassesses DTLs, decrements the device rebuild feature, emits finish events, requests spare-detach handling, optionally starts a scrub, wakes waiters, and clears recent error-event deduplication. Cancel marks state canceled and decrements the feature. Reset clears progress and starts a fresh rebuild thread without fully canceling the feature.

## Dependencies

Depends on vdev internals, dRAID/mirror/replacing/spare rebuild hooks, metaslab space maps, range trees, DTL logic, ZIO, ABD allocation, DMU sync tasks, SPA feature accounting, ARC sizing, ZAP persistence, pool scan setup/cancel paths, and event/history reporting.

## Correctness Notes

Sequential rebuild deliberately does not verify block checksums during reconstruction; the optional post-rebuild scrub is the checksum verification phase and is strongly recommended. RAIDZ is excluded because variable stripe width prevents this simple LBA-order reconstruction model, while dRAID supplies fixed-width rebuild sizing.

Metaslabs are disabled while their allocated ranges are captured and rebuilt so new allocations cannot race the scan of that address range. Waiting for the rebuild TXG before re-enabling the metaslab prevents later allocations from interfering with reconstructed ranges. Progress is written by sync task and rolled back on certain top-level unavailability errors so import/resume can restart from a safe offset.

The stop/cancel/reset flags are intentionally separate: export/suspend leaves the on-disk state active, detach can cancel if no missing DTLs remain, and attaching another replacement device resets the active pass so the new participant receives all needed data. The in-flight byte limiter is important for latency and memory pressure; it derives from ARC size, top-level count, `zfs_rebuild_vdev_limit`, and child count.
