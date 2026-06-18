# File Research: sources/cow-pools/openzfs/module/zfs/dmu_objset.c

## Purpose
Implements OpenZFS DMU objset lifecycle and synchronization: opening/holding/owning objsets, creating filesystems/objsets, syncing dirty dnodes and special dnodes, eviction, user/group/project accounting, dataset enumeration, snapshot/child listing, and objset stats/helpers.

## Main Responsibilities
- Initializes global `os_lock` for safe interaction with `dnode_move()` and objset teardown.
- Opens `objset_t` from a root block or hole, reads/writes `objset_phys_t`, registers dataset property callbacks, and opens special dnodes.
- Provides hold/own/release/disown APIs around `dsl_dataset_t` and `dsl_pool_t`.
- Creates objsets and datasets through DSL sync tasks, including encrypted dataset creation edge cases.
- Syncs dirty dnodes in parallel, writes the objset root block, updates ZIL state, and runs sync-done accounting cleanup.
- Maintains user/group/project byte and object accounting through per-sync-task AVL caches.
- Runs background user-space and id/project quota upgrades.
- Enumerates datasets/snapshots/children through DSL/ZAP traversal, optionally parallelized.
- Exports objset metadata helpers and kernel symbols.

## Key Data And State
- `krwlock_t os_lock`: teardown barrier for object relocation safety.
- `dmu_find_threads`: optional tunable for parallel dataset discovery.
- `dmu_rescan_dnode_threshold`: threshold for enabling meta-dnode backfill after enough dnodes are freed.
- `upgrade_tag`: long-hold tag for background objset upgrades.
- `file_cbs[DMU_OST_NUMTYPES]`: per-objset-type callback table for extracting file owner/generation info.
- `userquota_node_t`, `userquota_cache_t`, `userquota_updates_arg_t`: batching structures for syncing quota deltas.
- `dmu_objset_find_ctx_t`: recursive dataset traversal context.

## Important Functions
- `dmu_objset_open_impl()`: allocates and initializes `objset_t`, reads the root BP through ARC, expands old objset phys buffers as needed, registers property callbacks, initializes lists/locks/per-cpu object allocators, opens meta/user/group/project dnodes, and allocates ZIL.
- `dmu_objset_from_ds()`: lazily opens and attaches an objset to a dataset under `ds_opening_lock`.
- `dmu_objset_hold_flags()`, `dmu_objset_own()`, `dmu_objset_own_obj()`: public entry points for holding or owning datasets and obtaining objsets, including decryption/MAC handling for encrypted objsets.
- `dmu_objset_create_impl_dnstats()` and `dmu_objset_create_impl()`: initialize a new objset’s meta-dnode, type, feature-accounting flags, and dirty the dataset.
- `dmu_objset_create_check()` / `dmu_objset_create_sync()`: DSL sync-task pair for dataset creation, parent validation, crypto validation, filesystem limits, and encrypted creation sync forcing.
- `dmu_objset_sync()`: core sync path. Releases the objset phys ARC buffer, creates the root block write, syncs special dnodes, builds `os_synced_dnodes`, dispatches dirty dnode sync tasks, then schedules meta-dnode/ZIL finalization.
- `sync_dnodes_task()` / `sync_meta_dnode_task()`: parallel dirty-dnode sync workers and final root/ZIL completion stage.
- `dmu_objset_sync_done()`: dispatches either quota update tasks or simple dnode release tasks after syncing.
- `dmu_objset_userquota_get_ids()`: extracts old/new user, group, and project IDs from bonus or spill buffers for accounting.
- `dmu_objset_space_upgrade()`: walks objects and dirties bonus buffers to backfill accounting state.
- `dmu_objset_find_dp()` / `dmu_objset_find_impl()` / `dmu_objset_find()`: recursive dataset/snapshot traversal with hidden dataset filtering.
- `dmu_objset_evict()` / `dmu_objset_evict_done()`: unregisters properties, tears down SA/ZIL/dbufs/dnodes, waits through `os_lock`, destroys locks/lists, deregisters from SPA eviction tracking, and frees `objset_t`.

## Control Flow Notes
- Opening a normal dataset requires the pool config lock because property registration may query DSL properties.
- Snapshots do not register mutable checksum/compression/copies/dedup/logbias/sync-style properties.
- Encrypted objsets read the root block raw/authenticated and later untransform during ownership when decrypting.
- Objset sync writes the root block only after special dnodes and dirty dnodes are coordinated; final `zio_nowait()` is deferred until `sync_meta_dnode_task()`.
- User-accounting updates are intentionally skipped for encrypted receives and pool claiming.
- Parallel `dmu_objset_find_dp()` uses child task dispatch while each worker takes a priority pool config read lock to avoid deadlock behind pending writers.

## Error Handling And Invariants
- Creation rejects snapshot names, overlong names, excessive nesting, existing targets, invalid crypto, wrong parent type, and filesystem/snapshot limit violations.
- Objset ownership rejects wrong objset type, writable snapshot ownership, and incompatible encryption versions.
- ARC checksum errors from root block reads are normalized to `EIO`.
- Eviction asserts no dirty txg state and that all dnodes are gone before final destruction.
- User quota ZAP increments are protected by `os_userused_lock` because `zap_increment()` is not atomic.
- Dataset traversal stores only the first error under a shared mutex.

## Dependencies
Heavy coupling with DMU/DSL/SPA internals: `dsl_dataset`, `dsl_dir`, `dsl_pool`, `dnode`, `dbuf`, `arc`, `zio`, `zil`, `zap`, `zfeature`, `zvol`, `sa`, and encryption/key mapping code.

## Research Notes
This file is the central objset management layer. For changes touching receive, send, quota accounting, encryption, or dataset lifecycle, this file defines the object lifetime and sync constraints that those higher-level features depend on.
