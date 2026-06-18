# Group Research: group_1436_openzfs_sources_cow_pools_openzfs_module_zfs_dsl_dataset_c_sources__3de5fc6c4ff6

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/openzfs`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_dataset.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_dataset.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_deadlist.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_deadlist.c

## Role

`dsl_deadlist.c` implements OpenZFS deadlists and livelists. Deadlists track blocks that died after particular transaction group boundaries and are needed for snapshot, clone, and destroy accounting. Livelists reuse the same data structure to track clone-specific ALLOC/FREE block pointer history so clone deletion can avoid traversing the full block tree.

## Major Responsibilities

- Allocate, open, close, clone, free, and mutate deadlist objects.
- Support old-format `bpobj` deadlists and newer ZAP-backed deadlists.
- Maintain per-deadlist used/compressed/uncompressed accounting.
- Lazily load full AVL trees for mutation and sparse cache trees for range space queries.
- Add/remove transaction group keys and merge/move deadlist contents.
- Process livelist sublists by matching FREE and ALLOC records.
- Provide tunables for livelist sublist sizing and disable thresholds.

## Data Model

New-format deadlists are ZAP objects keyed by minimum txg. Each key maps to a `bpobj` containing block pointers for that txg interval. The bonus buffer stores `dsl_deadlist_phys_t`, including aggregate used/compressed/uncompressed counts.

Old-format deadlists are direct `bpobj` objects. Most functions branch on `dl_oldfmt` to preserve compatibility.

The in-memory form uses:

- `dl_tree`: full AVL tree of `dsl_deadlist_entry_t`, used for mutation.
- `dl_cache`: sparse AVL tree of non-empty `bpobj` entries, used for faster space-range queries.
- `dl_lock`: protects lazy loading, tree/cache state, and aggregate counters.

## Important Functions

- `dsl_deadlist_open()` / `dsl_deadlist_close()`: initialize or release old/new-format deadlist handles.
- `dsl_deadlist_alloc()` / `dsl_deadlist_free()`: allocate or recursively destroy deadlist storage.
- `dsl_deadlist_load_tree()`: loads all ZAP entries, prefetches bpobjs, opens them, and builds the mutation AVL.
- `dsl_deadlist_load_cache()`: loads only non-empty bpobjs and their space stats for efficient range queries.
- `dsl_deadlist_insert()`: inserts a block pointer into the correct txg interval and updates aggregate counters.
- `dsl_deadlist_add_key()` / `dsl_deadlist_remove_key()`: split or collapse txg ranges.
- `dsl_deadlist_remove_entry()` / `dsl_deadlist_clear_entry()`: delete or reset individual deadlist entries.
- `dsl_deadlist_clone()`: creates a new deadlist with matching txg keys up to `maxtxg`.
- `dsl_deadlist_space()` / `dsl_deadlist_space_range()`: return total or txg-range deadlist space.
- `dsl_deadlist_merge()`: merges another deadlist into this one and clears the source.
- `dsl_deadlist_move_bpobj()`: moves entries newer than a txg into a pool-level `bpobj`, used by destroy paths.
- `dsl_process_sub_livelist()`: reduces a livelist sublist into block pointers that still need freeing.

## Livelist Behavior

The file documents livelists as clone-specific histories of block pointer ALLOC and FREE events. Deleting a clone can process these records instead of walking the entire object tree. Livelists are split into sublists by txg to bound memory and allow incremental deletion.

`dsl_livelist_iterate()` uses an AVL tree keyed by DVA vdev/offset. FREE records create or increment a tracked entry. ALLOC records either cancel a prior FREE or are appended to the `to_free` bplist. The refcount handling supports dedup and block cloning cases where the same block pointer may appear multiple times.

## Concurrency

The file states the core concurrency contract:

- Deadlists are modified only from syncing context.
- Except for `dsl_deadlist_insert()`, modification requires `dp_config_rwlock` as writer.
- Accessors may run from open context with config lock as reader.
- `dl_lock` protects aggregate stats, lazy tree/cache loading, and concurrent insertion/stat collection.

`bpobj_t` provides its own internal locking where needed.

## Interactions

- `dsl_dataset.c` uses deadlists for block death, snapshots, remap deadlists, promotion, clone swap, written-space calculations, and livelist flushing.
- `dsl_destroy.c` uses deadlists to destroy snapshots, collapse txg keys, move freeable blocks to pool free queues, and process livelists.
- `dsl_pool` provides `dp_empty_bpobj`, pool free bpobj, and metadata object set state.
- `bpobj` is the lower-level persistent block pointer list container.

## Tunables

- `zfs_livelist_max_entries`: threshold for creating new livelist sublists.
- `zfs_livelist_min_percent_shared`: threshold below which clone livelists are disabled because the clone has diverged too far from the origin.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_deadlist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_deleg.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_deleg.c

## Role

`dsl_deleg.c` implements ZFS delegated administration permissions stored in DSL directory ZAP objects. It handles granting, revoking, listing, checking, inheriting create-time permissions, and destroying delegation metadata.

## Permission Storage Model

Delegated permissions are stored through a two-level ZAP layout. The first-level ZAP maps a “who key” to a jump object. The jump object contains individual permissions or permission-set names.

Who-key classes encode target and scope, including:

- User, group, everyone.
- Local versus descendent permissions.
- Permission sets granted to users/groups/everyone.
- Create-time permissions and create-time permission sets.
- Named permission sets and nested named sets.

The comment at the top of the file documents key forms such as `ul$<id>`, `gd$<id>`, `El$`, `c-$`, and `s-$@<name>`.

## Major Responsibilities

- Validate whether a caller may delegate or undelegate permissions.
- Apply delegated permission changes in sync tasks.
- Retrieve all delegated permissions from a dataset up through ancestors.
- Evaluate access for a dataset, including local/descendent inheritance and named permission sets.
- Copy create-time delegated permissions from ancestors to newly created datasets.
- Destroy delegation ZAP objects during DSL directory destruction.
- Respect pool feature availability and global delegation enablement.

## Important Functions

- `dsl_deleg_can_allow()`: requires `allow` permission and verifies the caller also has each permission being delegated. It refuses delegation of `allow` itself.
- `dsl_deleg_can_unallow()`: requires `allow` and restricts undelegation to the caller’s own user entries.
- `dsl_deleg_set()`: public sync-task wrapper for grant/revoke operations.
- `dsl_deleg_set_sync()`: creates delegation ZAPs and jump objects as needed, then updates permissions.
- `dsl_deleg_unset_sync()`: removes permissions or whole who-key jump objects, destroying empty jump objects.
- `dsl_deleg_get()`: walks from the target DSL directory up to root and builds an nvlist of delegated permissions by source dataset.
- `dsl_deleg_access_impl()`: core access check for a held dataset and credential.
- `dsl_deleg_access()`: pool/dataset hold wrapper for permission checking by dataset name.
- `dsl_deleg_set_create_perms()`: copies ancestor create-time permissions into a new dataset for the creating UID.
- `dsl_deleg_destroy()`: destroys all jump objects and the base delegation ZAP.
- `dsl_delegation_on()`: checks SPA delegation enablement.

## Access Check Flow

`dsl_deleg_access_impl()` first rejects checks when delegation is disabled or the pool lacks delegated-permission support. It determines whether to start with local or descendent scope: snapshots are treated as descendent-only, while heads start local and then move to descendent as ancestors are traversed.

For each DSL directory from the dataset upward:

1. Non-global-zone callers are constrained by `zoned`/`zoned_uid` properties.
2. User, group, everyone, and supplemental group permission sets are loaded into an AVL tree.
3. Named sets are recursively expanded through nested set references.
4. The requested permission is checked against matching sets.
5. If sets do not grant it, direct user/group/everyone permissions are checked.

## Concurrency and Syncing

Permission mutations are performed through `dsl_sync_task()`. The check phase verifies the `SPA_VERSION_DELEGATED_PERMS` feature and that the target DSL directory exists. Sync functions mutate MOS ZAP objects and log pool history records.

Access checks require the DSL pool config to be held and use held dataset/directory structures for stable traversal.

## Interactions

- `dsl_dataset_create_sync()` calls `dsl_deleg_set_create_perms()` for new dataset creation.
- `dsl_dir_destroy_sync()` in destroy code calls `dsl_deleg_destroy()` when removing a DSL directory.
- `zfs_deleg_whokey()` from `zfs_deleg.h` centralizes who-key formatting.
- Credentials are inspected through `crgetuid`, `crgetgid`, `crgetngroups`, and `crgetgroups`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_deleg.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_destroy.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_destroy.c

## Role

`dsl_destroy.c` implements destruction of snapshots, head datasets, inconsistent datasets, and clone/livelist-backed deletion. It coordinates namespace removal, deadlist merging, space accounting, feature cleanup, async destroy queues, zvol minor cleanup, bookmarks, remap deadlists, and DSL directory destruction.

## Major Responsibilities

- Validate and destroy snapshots, including deferred destroy handling.
- Destroy head datasets and their DSL directories.
- Support old synchronous destroy, async bptree destroy, and livelist-based clone destroy.
- Collapse snapshot/deadlist txg ranges after snapshot removal.
- Merge/remap deadlists and move freeable block pointers to pool-level queues.
- Remove related bookmarks, delegation metadata, properties, userrefs, clone links, and error logs.
- Clean up inconsistent datasets left by failed operations unless they are resumable receives.

## Snapshot Destroy Flow

`dsl_destroy_snapshot_check_impl()` requires the target to be a snapshot, rejects long-held snapshots, supports deferred destroy only on pools with userrefs, rejects non-deferred snapshots with userrefs, and prevents deleting branch points with multiple children.

`dsl_destroy_snapshot_sync_impl()` handles the full destructive rewrite:

- Optionally marks the snapshot `DS_FLAG_DEFER_DESTROY`.
- Logs history before namespace removal.
- Notifies scan/bookmark subsystems.
- Deactivates per-dataset features.
- Rewires previous and next snapshot pointers.
- Adjusts previous snapshot unique space and snapshot-used accounting.
- Moves newly freeable blocks from the next deadlist to the pool free bpobj.
- Merges the destroyed snapshot’s deadlist into the next dataset.
- Handles remap deadlists and obsolete block movement.
- Removes txg keys from clone/head deadlists when no bookmark preserves the range.
- Updates head unique/refreservation accounting when the next dataset is a head.
- Removes the snapshot from the snapshot namespace.
- Destroys properties, userrefs, next-clones ZAPs, deadlists, and the dataset object.

Multi-snapshot destruction is implemented by `dsl_destroy_snapshots_nvl()` using a ZCP Lua program that first checks all requested snapshots and then sync-destroys them all-or-nothing, returning per-snapshot errors.

## Head Dataset Destroy Flow

`dsl_destroy_head_check_impl()` requires a head dataset, checks long-hold count, rejects datasets with snapshots on the active branch, rejects child filesystems, and handles the special case where destroying a clone also allows removing a deferred origin snapshot.

`dsl_destroy_head_sync_impl()`:

- Cancels DSL directory waiters.
- Clears refreservation.
- Deactivates dataset features.
- Notifies scan.
- Updates origin clone links and child counts.
- Destroys normal and remap deadlists.
- Chooses one of three block-destroy strategies:
  - livelist clone destroy via `dsl_async_clone_destroy()`;
  - async bptree destroy via `dsl_async_dataset_destroy()`;
  - old synchronous traversal via `old_synchronous_dataset_destroy()`.
- Removes clone references, evicts the objset, clears the DSL directory head pointer, destroys snapname/bookmark ZAPs, clears bootfs, frees the dataset object, destroys the DSL directory, optionally destroys a deferred origin snapshot, and deletes head errlog state when supported.

`dsl_destroy_head()` performs an old-pool pre-pass for non-async-destroy pools: it marks the dataset inconsistent, frees objects in open context, waits for sync, and then runs the sync destroy.

## Deadlist and Clone Range Handling

`process_old_deadlist()` preserves compatibility with old-format deadlists by iterating the next dataset’s `bpobj`, moving older blocks into the current deadlist and freeing newer blocks directly.

`dsl_dir_remove_clones_key()` recursively walks clone directories and removes a deadlist key from clone/remap deadlists when a snapshot range collapses. It uses a stack of held clone datasets to cover nested clone trees.

`dsl_destroy_snapshot_handle_remaps()` moves remap-deadlist entries that are now obsolete into the pool obsolete bpobj and merges destroyed snapshot remap deadlists into the next dataset when needed.

## Livelist Clone Destroy

`dsl_async_clone_destroy()` handles fast deletion for clones with livelists:

- Verifies livelist accounting matches DSL directory usage.
- Destroys the ZIL.
- Adds the livelist object to `DMU_POOL_DELETED_CLONES`.
- Transfers clone-used space from the clone directory to `dp_free_dir`.
- Removes the livelist from the DSL directory without freeing it immediately.
- Wakes the SPA livelist delete thread.

This keeps clone deletion incremental and avoids full block-tree traversal.

## Async Dataset Destroy

`dsl_async_dataset_destroy()` initializes async destroy support if needed, allocates the pool bptree, destroys the ZIL, adds the dataset root block pointer and accounting into the bptree, and transfers dataset used space to `dp_free_dir`.

## Inconsistent Dataset Cleanup

`dsl_destroy_inconsistent()` is a callback for dataset enumeration. It holds each object set, checks `DS_FLAG_INCONSISTENT`, skips datasets with receive-resume state, and invokes `dsl_destroy_head()` for inconsistent datasets that should be removed.

## Interactions

- `dsl_dataset.c`: dataset flags, deadlists, block-kill accounting, feature deactivation, remap deadlists, unique recalculation, refreservation clearing.
- `dsl_deadlist.c`: deadlist key removal, merge, move-to-bpobj, livelist space checks.
- `dsl_bookmark`: destruction may preserve txg ranges if bookmarks remain.
- `dsl_scan`: notified when datasets are destroyed.
- `dsl_deleg`: delegation ZAPs are destroyed with DSL directories.
- `zvol`: minors are removed for destroyed datasets/snapshots.
- `spa_feature`: async destroy, livelist, bookmark, redaction, and errlog feature state are updated.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_destroy.c -->