# File Research: sources/cow-pools/openzfs/module/zfs/dsl_dataset.c

## Role

`dsl_dataset.c` is the central OpenZFS DSL dataset implementation. It manages dataset lifetime, dataset object loading/eviction, block birth/death accounting, snapshots, clones, rollback, clone promotion, quota/refreservation behavior, per-dataset feature flags, remap deadlists, redaction state, receive-resume tokens, and exported dataset statistics.

This file is a major coordination point between the DMU object set layer, DSL directory layer, snapshot namespace, deadlist/bookmark subsystems, scan/destroy paths, encryption/key mapping, zvol minor handling, and SPA feature accounting.

## Major Responsibilities

- Maintain dataset object references, ownership, long holds, and eviction lifecycle.
- Create filesystems, volumes, snapshots, clones, temporary snapshots, and clone-origin relationships.
- Track block accounting for born, killed, remapped, referenced, unique, compressed, and uncompressed bytes.
- Manage snapshot namespace ZAP entries and snapshot counts.
- Manage `ds_deadlist`, `ds_remap_deadlist`, pending deadlist entries, and clone livelist flushing.
- Enforce rollback, clone, promotion, refquota, refreservation, and compression-feature checks.
- Export stats for `zfs get`, fast object-set stats, receive-resume tokens, clone lists, redaction lists, and space/written calculations.
- Activate/deactivate per-dataset SPA features, including large blocks, checksum/compression features, redacted datasets, and obsolete-count/remap state.

## Key Data Flow

Block writes call `dsl_dataset_block_born()`, which updates referenced/compressed/uncompressed/unique bytes, activates dataset features implied by block properties, tracks livelist allocations for clones, and transfers space into the containing `dsl_dir`.

Block frees call `dsl_dataset_block_kill()`, which decides whether the block can be freed immediately, queued to the pool free bpobj, added to the dataset deadlist, or deferred for sync-thread processing. It updates previous snapshot unique space where needed and adjusts `DD_USED_HEAD`, `DD_USED_SNAP`, and `DD_USED_REFRSRV`.

Snapshot creation flows through `dsl_dataset_snapshot_check()` and `dsl_dataset_snapshot_sync_impl()`. The sync path creates a new DSL dataset object for the snapshot, copies feature state and block pointer metadata, moves the head deadlist into the snapshot, creates a new head deadlist, updates previous/next snapshot links, adjusts refreservation accounting, records snapshot ZAP entries, updates bookmarks, and logs history.

Clone creation uses `dsl_dataset_clone_check()` and `dsl_dataset_clone_sync()`, which validate the origin is a snapshot and create a new DSL directory/dataset whose previous snapshot is the origin. Clone creation can initialize a livelist when the livelist feature is enabled.

Rollback is implemented as a clone swap: `dsl_dataset_rollback_sync()` creates a `%rollback` clone from the target snapshot, swaps it with the current head via `dsl_dataset_clone_swap_sync_impl()`, zeroes the ZIL, and destroys the temporary clone.

Promotion uses lists of shared, clone, and origin snapshots to rewire snapshot ownership and origin pointers. `dsl_dataset_promote_check()` performs space, encryption-root, conflict, and long-hold validation. `dsl_dataset_promote_sync()` transfers snapshots/bookmarks, rewrites clone/origin metadata, updates deadlist-derived space accounting, removes now-invalid livelists, and swaps head error log ownership when supported.

## Important Functions

- `dsl_dataset_hold_obj()`, `dsl_dataset_hold_flags()`, `dsl_dataset_hold()`: open and initialize `dsl_dataset_t` objects from MOS bonus buffers.
- `dsl_dataset_tryown()`, `dsl_dataset_disown()`, `dsl_dataset_long_hold()`: ownership and destruction-prevention hold model.
- `dsl_dataset_create_sync_dd()`, `dsl_dataset_create_sync()`: allocate dataset objects and connect them to DSL directories.
- `dsl_dataset_snapshot_check_impl()`, `dsl_dataset_snapshot_sync_impl()`, `dsl_dataset_snapshot()`: snapshot validation and creation.
- `dsl_dataset_snapshot_tmp()`: temporary held snapshot creation and immediate deferred destroy.
- `dsl_dataset_sync()` and `dsl_dataset_sync_done()`: objset sync and post-sync deadlist/livelist/feature finalization.
- `dsl_dataset_rollback_check()` and `dsl_dataset_rollback_sync()`: rollback validation and execution.
- `dsl_dataset_clone_swap_check_impl()` and `dsl_dataset_clone_swap_sync_impl()`: core clone/head swap primitive used by rollback/receive paths.
- `dsl_dataset_promote_check()` and `dsl_dataset_promote_sync()`: clone promotion.
- `dsl_dataset_space_written()`, `dsl_dataset_space_written_bookmark()`, `dsl_dataset_space_wouldfree()`: deadlist/bookmark-based written/freeable space calculations.
- `dsl_dataset_set_refquota()`, `dsl_dataset_set_refreservation()`, `dsl_dataset_check_quota()`: quota and refreservation enforcement.
- `dsl_dataset_create_remap_deadlist()`, `dsl_dataset_destroy_remap_deadlist()`, `dsl_dataset_block_remapped()`: indirect-vdev remap accounting.
- `dsl_dataset_activate_redaction()`: stores redaction snapshot arrays as per-dataset feature state.

## On-Disk Structures and Fields

This file works heavily with `dsl_dataset_phys_t` fields including:

- `ds_dir_obj`, `ds_bp`, `ds_prev_snap_obj`, `ds_prev_snap_txg`, `ds_next_snap_obj`
- `ds_snapnames_zapobj`, `ds_deadlist_obj`, `ds_next_clones_obj`
- `ds_referenced_bytes`, `ds_compressed_bytes`, `ds_uncompressed_bytes`, `ds_unique_bytes`
- `ds_flags`, `ds_userrefs_obj`, `ds_props_obj`, `ds_fsid_guid`, `ds_guid`

Zapified dataset fields include receive resume data, remap deadlist object, IV set GUID, per-dataset feature GUIDs, redaction state, and bookmark-related metadata.

## Concurrency and Locking

The file assumes many structural operations occur under the DSL pool config lock, often as writer during sync tasks. Dataset mutable fields are protected by:

- `ds_lock` for owner, snapname, quota/refreservation cache, and byte fields in some paths.
- `ds_bp_rwlock` for root block pointer reads/writes.
- `ds_remap_deadlist_lock` for lazy remap deadlist creation.
- `ds_longholds` to prevent destruction while open-context operations drop pool holds.
- `dd_activity_lock` via handoff checks for rollback/clone swap operations.

Most persistent modifications happen in syncing context through `dsl_sync_task()`.

## Interactions

- `dsl_dir`: parent/child directory accounting, clone origin tracking, reservations, limits, counts, livelist storage.
- `dsl_deadlist`: deadlist cloning, key insertion/removal, deadlist space accounting, remap deadlists.
- `dsl_bookmark`: snapshot/bookmark transitions, written-space calculations, receive/redaction metadata.
- `dsl_destroy`: head and snapshot destruction paths call into dataset primitives.
- `dmu_objset`: object set sync, evict, hold, and root block pointer state.
- `spa_feature`: feature activation/deactivation and pool feature reference counts.
- `dmu_send`/`dmu_recv`: receive resume token state and raw/encrypted write handling.
- `zvol`: zvol minor creation/removal/rename after dataset namespace changes.

## Tunables and Exports

Module parameters include `zfs_max_recordsize`, `zfs_allow_redacted_dataset_mount`, and `zfs_snapshot_history_enabled`.

The file exports many dataset APIs, including hold/release/own, create, snapshot, promote, user hold/release, block born/kill, dirty/sync, stats, quota check, clone swap, and space-written helpers.
