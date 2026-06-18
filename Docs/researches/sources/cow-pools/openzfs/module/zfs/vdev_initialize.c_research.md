# File Research: sources/cow-pools/openzfs/module/zfs/vdev_initialize.c

## Purpose

Implements `zpool initialize` support for leaf vdevs. Initialization writes a known filler pattern over currently free physical regions so previously unwritten disk space is forced through the device, while persisting progress and state in leaf-vdev ZAP entries.

## Main APIs And Entry Points

- Public control APIs: `vdev_initialize()`, `vdev_uninitialize()`, `vdev_initialize_stop()`, `vdev_initialize_stop_wait()`, `vdev_initialize_stop_all()`, and `vdev_initialize_restart()`.
- State persistence: `vdev_initialize_change_state()`, `vdev_initialize_zap_update_sync()`, `vdev_initialize_zap_remove_sync()`, and `vdev_initialize_load()`.
- I/O path: `vdev_initialize_thread()`, `vdev_initialize_ranges()`, `vdev_initialize_write()`, and `vdev_initialize_cb()`.
- Progress/range translation: `vdev_initialize_calculate_progress()`, `vdev_initialize_xlate_progress()`, `vdev_initialize_xlate_last_rs_end()`, `vdev_initialize_range_add()`, and `vdev_initialize_xlate_range_add()`.
- Pattern buffer helpers: `vdev_initialize_block_alloc()`, `vdev_initialize_block_fill()`, and `vdev_initialize_block_free()`.

## Control Flow And State

`vdev_initialize()` requires the caller to hold the vdev initialize lock, validates a concrete writable leaf that is not already initializing/removing/expanding, records `VDEV_INITIALIZE_ACTIVE`, and starts `vdev_initialize_thread()`. State changes schedule sync tasks that persist last offset, state, and action time in the leaf ZAP, and log pool history. Transition to `NONE` removes initialize ZAP keys.

The worker thread enters config as reader, loads persisted progress, allocates a reusable ABD filled with `zfs_initialize_value`, creates a physical range tree, then walks top-level metaslabs. For each metaslab it disables allocation, loads the metaslab, walks allocatable free ranges, translates logical free ranges through `vdev_xlate_walk()` to this leaf's physical offsets, skips ranges already below the last persisted offset, writes remaining ranges in `zfs_initialize_chunk_size` chunks, then reenables/unloads as appropriate. The range tree is vacated after each metaslab.

`vdev_initialize_write()` limits concurrent initialization writes per leaf using `zfs_initialize_limit`, creates a DMU transaction so progress can be synced in the same txg, records the txg-local next offset, enters state config as reader for vdev lifetime protection, checks stop conditions, then issues `zio_write_phys()` under the txg root ZIO. The callback updates error counters or bytes done, rolls back txg-local offset for unavailable-device `ENXIO`, decrements inflight count, wakes waiters, and releases the state config lock.

Progress calculation estimates total/done free bytes by walking metaslabs and translating top-level logical ranges to this leaf's physical ranges. Fully unvisited metaslabs contribute estimated free space; fully visited metaslabs count as done; the current metaslab is loaded and its free tree is walked for finer-grained progress.

Stop and restart paths coordinate with locks and condition variables. `vdev_initialize_stop()` changes to a target state, sets `exit_wanted`, and either waits immediately or queues the vdev for later `vdev_initialize_stop_wait()`. `vdev_initialize_stop_all()` recursively stops concrete leaves and waits for synced state. `vdev_initialize_restart()` reads persisted state/action time during import or namespace-held operations and resumes active writable leaves unless the device is offline, suspended, removing, or raidz-expanding.

## Dependencies And Integration

This file integrates with metaslab loading/disabling, range trees/btrees, vdev translation, physical ZIO writes, DMU sync tasks, txg waiting, leaf-vdev ZAP metadata, spa history/notifications, config/state locks, and vdev removal/raidz expansion state. It exports the public initialize control functions and exposes `zfs_initialize_value` and `zfs_initialize_chunk_size` as module parameters.

## Risks And Invariants

- Initialization writes only free space as observed under disabled metaslabs; it must not race normal allocator use of the same ranges.
- Last-offset persistence is per txg slot and relies on spa sync waiting on `spa_txg_zio` before sync tasks run.
- Stop paths must not hold config/state writer locks while waiting, because the worker may need reader locks to exit.
- `vdev_xlate_walk()` is required for composite top-level layouts; physical progress and write ranges cannot assume a direct logical-to-leaf offset mapping.
- The filler pattern is configurable but not data-protection metadata; initialization is best-effort and I/O errors increment stats rather than necessarily failing the device.

## Summary

`vdev_initialize.c` is the leaf-device initialization engine, coordinating persisted state, metaslab free-space traversal, translated physical writes, progress estimation, cancellation, and import-time restart.
