# File Research: sources/cow-pools/openzfs/module/zfs/zvol.c

## Purpose

Implements the shared OpenZFS zvol core: the DMU-backed virtual block-device layer that exposes `DMU_OST_ZVOL` datasets as persistent volume minors, handles zvol properties and lifecycle, integrates with the ZIL for synchronous block-device semantics, supports block cloning between zvols, and coordinates OS-specific minor operations through per-pool task queues.

The file is platform-neutral for the core logic and delegates device-node and block-device operations to `zvol_os_*()` helpers. It also documents the principal locking model: `zvol_state_lock` protects global name lookup structures, each `zv_state_lock` protects one `zvol_state_t`, and `zv_suspend_lock` gates data I/O across receive, rollback, open, close, and removal operations.

## Main APIs And Entry Points

- Request task helpers: `zv_request_task_create()` and `zv_request_task_free()` allocate/free OS I/O request task wrappers.
- Name lookup and registration: `zvol_name_hash()`, `zvol_find_by_name_hash()`, internal `zvol_find_by_name()`, `zvol_insert()`, and internal `zvol_remove()`.
- Dataset creation/stats/properties: `zvol_create_cb()`, `zvol_get_stats()`, `zvol_check_volsize()`, `zvol_set_volsize()`, `zvol_set_volthreading()`, `zvol_set_ro()`, `zvol_check_volblocksize()`, and `zvol_set_common()`.
- ZIL replay/logging: `zvol_replay_truncate()`, `zvol_replay_write()`, `zvol_replay_clone_range()`, `zvol_replay_vector`, `zvol_log_write()`, `zvol_log_truncate()`, `zvol_log_clone_range()`, and `zvol_get_data()`.
- Block cloning: `zvol_clone_range()` validates clone compatibility, locks source/destination ranges, clones L0 block pointers through `dmu_brt_clone()`, and logs clone-range intent records.
- Open/suspend lifecycle: `zvol_setup_zv()`, `zvol_shutdown_zv()`, `zvol_tag()`, `zvol_suspend()`, `zvol_resume()`, `zvol_first_open()`, and `zvol_last_close()`.
- Minor management: `zvol_create_minors()`, `zvol_remove_minors()`, `zvol_rename_minors()`, plus internal create/remove/rename/snapdev/volmode task implementations.
- Module lifecycle: `zvol_init_impl()` creates zvol I/O taskqs and global lookup state; `zvol_fini_impl()` removes all minors and destroys those structures.
- Module parameters: `zvol_inhibit_dev`, `zvol_prefetch_bytes`, `zvol_volmode`, `zvol_threads`, `zvol_num_taskqs`, and `zvol_request_sync`.

## Data Structures

Global state consists of `zvol_state_list`, the name-hash table `zvol_htable`, `zvol_state_lock`, and `zvol_taskqs`. `zvol_state_t` is defined elsewhere but this file relies on its name/hash linkage, per-zvol locks, objset/dnode/zilog pointers, open count, flags, volume size/block size, rangelock, removal condition variable, and OS-specific disk state.

`zvol_task_t` describes serialized per-pool asynchronous minor/property work. It carries an operation enum, one or two dataset names, a property value, progress counters, and error/status fields. `zvol_task_cb()` dispatches these tasks on `spa->spa_zvol_taskq`, preserving ordering for create/remove/rename/property effects within a pool.

`minors_job_t` is a temporary list entry used while discovering minors to create. It records candidate dataset names and prefetch status so discovery can parallelize dnode prefetch on `system_taskq` but perform OS minor creation sequentially afterward.

`zvol_set_prop_int_arg_t` bridges DSL sync-task property updates with async zvol minor updates. It records the property/value/source, the highest dispatched task id, and a condition variable used to wait until sync context has queued all required async work.

## Control Flow

Zvol creation uses `zvol_create_cb()` to claim the fixed zvol data object and ZAP property object, then stores the logical volume size in the ZAP. Stats read the same ZAP `size` entry and the DMU object block size. Volume-size changes first reject readonly datasets, find or temporarily own the zvol objset, validate alignment to the DMU data block size, update the ZAP in a synced transaction, free data past the new end, update in-memory state, and notify the OS-specific disk layer.

First open owns the objset, sets `zv_objset`, reads readonly and size state, holds the zvol dnode, updates OS capacity, and sets the disk readonly flag if the dataset is readonly, a snapshot, or in a non-writable pool. Last close reverses this by closing the ZIL if the zvol was written, releasing the dnode, syncing and evicting dbufs when needed, disowning the objset, and clearing `zv_objset`.

Suspend for receive/rollback finds the zvol with the write side of `zv_suspend_lock`, rejects zvols already being removed, increments `zv_suspend_ref`, shuts down active objset-related state if open, and returns with the suspend lock held for the caller. Resume reacquires the objset and reruns setup for open zvols, releases the suspend lock, decrements the suspend reference, and wakes removers if needed.

ZIL replay supports only the transaction types meaningful to zvols. `TX_WRITE` replays data into `ZVOL_OBJ`, expanding dmu-sync records to full block size when required. `TX_TRUNCATE` replays free-long-range operations. `TX_CLONE_RANGE` replays logged block-pointer clones after validating block alignment and using DMU clone holds. All other replay vector slots return `ENOTSUP`.

Write logging chooses immediate, need-copy, or indirect write records through `zil_write_state()`, optionally embeds copied data by reading from the zvol dnode, assigns intent log records, and accounts write-log bytes. `zvol_get_data()` later supplies immediate or indirect data to the ZIL writer while holding the zvol rangelock over the affected byte range or full block.

`zvol_clone_range()` takes destination and source suspend locks, lazily opens the destination ZIL if needed, verifies the block-cloning feature, same-SPA requirement, encryption compatibility, optional strict property compatibility, identical zvol block sizes, in-range offsets, non-overlap for same-zvol clones, and block alignment. It then locks source and destination byte ranges in a deterministic order, reads source L0 block pointers in batches, clones them to the destination with `dmu_brt_clone()`, logs clone-range records, and commits the ZIL for `sync=always`.

Minor creation scans datasets and visible snapshots while avoiding DSL config-lock inversion with zvol open. Candidate zvol dnodes are prefetched in parallel, then OS minors are created sequentially. Removal first marks matching zvols with `ZVOL_REMOVING` under the suspend lock so new OS-side operations fail, waits for open and suspend references to drain, removes OS minors, then removes the zvol from global lookup structures and frees it. Rename walks the global list under the writer lock and renames exact matches plus child and snapshot names.

Property changes for `snapdev` and `volmode` are coordinated by `zvol_set_common()`: a DSL sync task sets the property and queues async work for every affected child according to its effective property. The caller waits until the sync callback has dispatched all work and then waits for the highest dispatched per-pool task id.

Initialization chooses a default zvol worker-thread count from active CPUs when `zvol_threads` is zero, derives the number of task queues, creates prepopulated dynamic taskqs, initializes global list/lock/hash table state, and registers module parameters. Finalization removes all minors, frees lookup state, and destroys task queues.

## Dependencies And Integration

This file integrates with DMU object allocation, dnodes, transactions, dbufs, object-set ownership, DSL properties and sync tasks, ZAP, ZIL replay/logging, block reference tables via `dmu_brt_clone()`, SPA features and task queues, range locks, dataset encryption/key checks, `spa_namespace_held()` open paths, SPL task queues and locks, dataset kstats, and OS-specific zvol hooks declared through `zvol_impl.h`.

It is the core coordination point between ZFS datasets and the host block-device interface. OS-specific files provide minor creation/removal/rename, capacity and readonly changes, close waiting, zvol-name detection, and request execution, while this file owns the shared dataset, logging, property, and synchronization semantics.

## Risks And Invariants

- Lock ordering matters: global `zvol_state_lock`, then `zv_suspend_lock`, then `zv_state_lock`. The code deliberately drops/reacquires locks in lookup paths to preserve this ordering.
- `zvol_state_lock` should protect name/list/hash operations only; long waits happen under per-zvol locks or outside the global lock.
- Minor operations are serialized per pool through `spa_zvol_taskq`; callers rely on this to preserve create/remove/rename/property ordering.
- Removal cannot remove a zvol from global lookup lists until OS-side operations can no longer reach it and open/suspend references have drained.
- `zv_suspend_ref` exists because removal cannot atomically infer safety solely from the rwlock once `zvol_resume()` releases it outside `zvol_state_lock`.
- ZIL replay must call `zil_replaying()` in successful replay transactions so replay progress is recorded in the ZIL header.
- Block cloning requires same SPA, compatible encryption/master keys, matching zvol block sizes, aligned ranges, and non-overlap for same-zvol clones.
- The strict block-clone property checks intentionally avoid surprising cross-dataset behavior when checksum, compression, copies, dedup checksum, or special-small-block settings differ.
- `zvol_update_volsize()` syncs the ZAP size update before freeing the truncated tail so VFS/device capacity observations do not race durable size metadata.
- `zvol_inhibit_dev` short-circuits minor creation/removal paths and is respected throughout minor-management code.

## Summary

`zvol.c` is the shared zvol control plane and log/data integration layer. It turns zvol datasets into orderly OS-visible block devices while preserving DMU ownership rules, ZIL consistency, clone semantics, property-driven minor visibility, and careful lock ordering across open, close, suspend, rollback, receive, and removal paths.
