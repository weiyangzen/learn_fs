# Group Research: group_518_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_e06a23903edf

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`; all five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dataset.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dataset.c

## Role

`dsl_dataset.c` is the main ZFS DSL dataset implementation. It owns dataset lifetime, block accounting, dataset holds/ownership, snapshot creation and rename, temporary snapshots, rollback, clone promotion, clone swap, dataset-level quotas/reservations, dataset statistics, resume receive token reporting, per-dataset feature flags, and remap deadlist management.

It is the central bridge between object-set/block activity and higher-level dataset namespace state. It calls into `dsl_dir.c` for hierarchical space/count accounting, `dsl_deadlist.c` for dead block tracking, `dsl_destroy.c` for snapshot/head teardown helpers, `dsl_deleg.c` indirectly through creation permissions, and the DMU/SPA layers for object allocation, ZAP metadata, feature activation, encryption, scan hooks, and sync task orchestration.

## Main State And Invariants

Important persistent state lives in `dsl_dataset_phys_t`, accessed through `dsl_dataset_phys(ds)`: previous/next snapshot links, deadlist object, snapnames ZAP, referenced/compressed/uncompressed/unique bytes, dataset GUIDs, creation txg/time, flags, and root block pointer.

Runtime state in `dsl_dataset_t` includes:
- `ds_dbuf`, `ds_object`, `ds_dir`, `ds_prev`, and `ds_objset`.
- `ds_deadlist`, `ds_pending_deadlist`, and optional `ds_remap_deadlist`.
- `ds_lock`, `ds_bp_rwlock`, `ds_opening_lock`, `ds_sendstream_lock`, `ds_remap_deadlist_lock`.
- `ds_owner` and `ds_longholds` for mounted/owned dataset protection.
- `ds_feature[]` and `ds_feature_activation[]` for per-dataset feature state.

Key invariants:
- Snapshots are recognized by nonzero `ds_num_children`; heads have `ds_next_snap_obj == 0`.
- Dirtying a snapshot panics; dirtying a head must be after its previous snapshot txg.
- Dataset space changes are mirrored into dsl_dir accounting, with `parent_delta()` adjusting for refreservation.
- Snapshot operations are sync-task based and usually require the pool config lock.
- Long holds prevent destruction and constrain rollback/clone-swap handoff.

## Block Accounting

`dsl_dataset_block_born()` accounts newly born non-hole blocks, updates referenced/compressed/uncompressed/unique bytes, activates large block and checksum features when needed, and propagates head space to the containing dsl_dir. MOS blocks are accounted directly to pool MOS usage.

`dsl_dataset_block_kill()` handles removal. Blocks born after the previous snapshot are freed immediately and subtracted from unique/referenced accounting. Older blocks go to the dataset deadlist or pending deadlist when called from async write-done context. It also updates previous snapshot unique bytes when appropriate and transfers space from head to snapshot usage.

`dsl_dataset_block_remapped()` handles indirect-vdev remapping. If the remapped birth is after the previous snapshot, the segment is obsolete in the vdev. Otherwise it synthesizes a block pointer and stores it in the remap deadlist, creating that deadlist on demand.

## Dataset Opening, Holds, Ownership

`dsl_dataset_hold_obj()` is the constructor/open path. It validates object type, allocates and initializes `dsl_dataset_t`, opens the parent `dsl_dir`, initializes locks/refcounts/lists, loads per-dataset features from zapified dataset metadata, opens the previous snapshot for heads, counts userrefs for snapshots, reads refquota/refreservation, handles encryption errata checks, opens the deadlist/remap deadlist, installs the dmu buffer user, and assigns a unique fsid GUID.

Name-based holds go through `dsl_dataset_hold_flags()`, which first holds the dsl_dir and then optionally resolves `@snapshot` names through the head dataset’s snapnames ZAP. Decrypting holds call `dsl_dataset_create_key_mapping()` and releasing them removes the mapping.

Ownership is layered on top of holds through `dsl_dataset_tryown()`, `dsl_dataset_own*()`, `dsl_dataset_disown()`, and long holds. `dsl_dataset_handoff_check()` temporarily drops an owner long hold during syncing checks to verify no other long holds exist.

## Snapshot Creation And Rename

Snapshot validation is split between `dsl_dataset_snapshot_check()` and `dsl_dataset_snapshot_check_impl()`. It checks:
- no duplicate snapshot in the same txg,
- no name conflict,
- not inconsistent unless part of receive,
- filesystem/snapshot limits,
- enough space for refreservation side effects.

For multi/recursive snapshots, it rolls up per-parent snapshot counts in an nvlist before checking limits so sibling and recursive operations are evaluated as a complete batch.

`dsl_dataset_snapshot_sync_impl()` creates the snapshot dataset object, copies root block and accounting from the head, copies per-dataset features, rewires previous/next snapshot links and next-clones metadata, handles refreservation transfer, clones/rekeys the head deadlist, moves any remap deadlist to the snapshot, writes encryption ivset metadata when appropriate, inserts the snapshot into the snapnames ZAP, updates `ds_prev`, calls scan hooks, updates snapshot cmtime, and logs history.

`dsl_dataset_snapshot()` handles old-pool ZIL suspension for pools before fast snapshots and runs the sync task. `dsl_dataset_snapshot_tmp()` creates a temporary snapshot with a user hold and immediately defers its destroy.

Snapshot rename uses `dsl_dataset_rename_snapshot_check*()` and `dsl_dataset_rename_snapshot_sync*()`, optionally recursively. It checks old-name existence, new-name absence, full name length, logs before mutation, removes the old snapname entry, updates `ds_snapname`, and adds the new ZAP entry.

## Sync, Stats, And Resume Tokens

`dsl_dataset_sync()` writes fsid GUID changes, stores resumable receive progress fields when present, syncs the object set, and activates delayed per-dataset features. `dsl_dataset_sync_done()` drains the pending deadlist into the real deadlist, destroys synced dnode lists, clears raw-write flags, asserts clean objset state, and releases the dirty hold.

Statistics are provided through many `dsl_get_*()` helpers and `dsl_dataset_stats()`. It reports referenced, available, used, ratios, creation txg/time, GUID, objset ID, userrefs, defer-destroy, written space since previous snapshot, clone lists for snapshots, dsl_dir stats for heads, encryption stats, and receive resume token state.

Resume token generation packs selected ZAP resume fields into an nvlist, compresses it with gzip, checksums it with Fletcher4, and hex-encodes it in the send token format. For failed incremental receives, the code also checks the child `%recv` dataset.

## Rollback, Promotion, Clone Swap

Rollback requires a head dataset with a latest snapshot, optional target snapshot matching the latest snapshot, no later bookmarks, no conflicting holds, and quota/refreservation feasibility. Sync creates a `%rollback` clone of the previous snapshot, swaps it with the head through clone-swap logic, zeros the ZIL, then destroys the temporary clone.

Promotion builds snapshot lists for shared, clone, and origin snapshots. `dsl_dataset_promote_check()` validates promotability, encryption roots, long holds, snapshot name conflicts, namespace length, space transfer, filesystem/snapshot limit transfer, and used-snapshot accounting. `dsl_dataset_promote_sync()` rewires origin and clone ancestry, moves snapshot ZAP entries and dsl_dir ownership, updates clone references, transfers space/count accounting, updates origin unique bytes, runs crypto sync hooks, and logs history.

`dsl_dataset_clone_swap_check_impl()` validates that two heads can swap, including branch relationships, modification state, long holds, refreservation availability, and refquota slack. `dsl_dataset_clone_swap_sync_impl()` swaps per-dataset features, evicts objsets, recomputes origin unique bytes, swaps root block pointers, adjusts directory accounting, swaps dataset accounting, swaps deadlists/remap deadlists, calls scan hooks, and logs.

## Quotas, Reservations, Written Space, Remap Deadlists

`dsl_dataset_check_quota()` works with `dsl_dir_tempreserve_impl()` to enforce refquota while discounting unconsumed refreservation. Refquota/refreservation setters are sync tasks that validate feature support, dataset type, predicted property values, current referenced/unique space, dsl_dir availability, and quota interactions before storing properties and updating cached runtime values/accounting.

`dsl_dataset_space_written()` computes space written between an older snapshot and a later snapshot/head by subtracting referenced space and adding relevant deadlist ranges. `dsl_dataset_space_wouldfree()` computes reclaimable space if a contiguous snapshot range is destroyed.

Remap deadlist helpers zapify the dataset as needed, store/remove `DS_FIELD_REMAP_DEADLIST`, open/close/free the remap deadlist, and increment/decrement `SPA_FEATURE_OBSOLETE_COUNTS`. `dsl_dataset_create_remap_deadlist()` clones the normal deadlist and requires the device-removal feature to be active.

## Research Notes

This file is the highest-risk coordination point in the group. Changes here must preserve sync-task atomicity, dsl_dir accounting symmetry, snapshot-chain invariants, deadlist key ranges, encryption errata behavior, and hold/owner semantics. Many helpers assume pool config locks and syncing context rather than performing defensive locking locally.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dataset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deadlist.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deadlist.c

## Role

`dsl_deadlist.c` implements ZFS DSL deadlists: per-dataset structures that track blocks killed after particular snapshot boundaries. Deadlists are central to snapshot space accounting, clone promotion, snapshot destroy, rollback, and device-removal remap accounting.

A modern deadlist is a ZAP object whose keys are minimum txg boundaries and whose values are `bpobj` object IDs. Each `bpobj` stores block pointers for blocks born in a txg range. Older pools can store a deadlist directly as a single old-format `bpobj`; most functions preserve compatibility with this format.

## Concurrency Model

The file starts with the concurrency contract:
- Deadlists are modified only from the syncing thread.
- Except for `dsl_deadlist_insert()`, modifications require `dp_config_rwlock` held as writer.
- Accessors such as `dsl_deadlist_space()` and `dsl_deadlist_space_range()` can run concurrently from open context while the config lock is reader-held.
- `dl_lock` protects cached aggregate counters and lazy AVL loading.
- `bpobj_t` provides its own locking; `dl_oldfmt` is immutable while open.

## Data Structures

The in-memory modern deadlist lazily loads a `dl_tree` AVL of `dsl_deadlist_entry_t`, sorted by `dle_mintxg`. Each entry opens a `bpobj` for that boundary. `dsl_deadlist_load_tree()` populates this tree from the ZAP and marks `dl_havetree`.

Persistent aggregate totals live in `dsl_deadlist_phys_t`: used, compressed, and uncompressed bytes. Old-format deadlists do not have this header and delegate directly to `bpobj`.

## Open, Close, Allocate, Free

`dsl_deadlist_open()` initializes the mutex, bonus-holds the object, detects old-format `DMU_OT_BPOBJ`, and either opens the old `bpobj` or points `dl_phys` at the deadlist header. `dsl_deadlist_close()` closes all opened `bpobj`s, destroys the AVL if loaded, releases the dbuf, destroys the mutex, and clears state.

`dsl_deadlist_alloc()` creates either a legacy `bpobj` or a modern ZAP with deadlist header based on pool version. `dsl_deadlist_free()` frees either a single `bpobj` or every child `bpobj` referenced by the ZAP, accounting for the pool empty bpobj special case, then frees the deadlist object.

## Insertion And Key Management

`dsl_deadlist_insert()` inserts a block pointer into the correct `bpobj` bucket. It updates aggregate `dl_used`, `dl_comp`, and `dl_uncomp`, finds the entry whose `mintxg` is immediately before the block birth, and enqueues the block. If that entry currently points to the shared empty bpobj, `dle_enqueue()` allocates a real `bpobj`, decrements the empty bpobj reference, updates the ZAP key, and enqueues there.

`dsl_deadlist_add_key()` adds a new empty boundary greater than existing keys. `dsl_deadlist_remove_key()` removes a boundary and merges its `bpobj` into the previous boundary via `dle_enqueue_subobj()`. These operations are how snapshot creation/destruction collapses or extends deadlist txg ranges.

`dsl_deadlist_regenerate()` rebuilds a modern deadlist key structure by walking dataset previous-snapshot links. It is used when cloning an old-format deadlist into a modern deadlist.

## Clone, Space Queries, Merge, Move

`dsl_deadlist_clone()` creates a new deadlist and copies only key boundaries below `maxtxg`, using empty `bpobj`s. It does not copy actual block pointers; the new deadlist starts as a structural clone used by new snapshots/heads.

`dsl_deadlist_space()` reports aggregate totals. For old format it calls `bpobj_space()`, and for modern format it reads cached header totals under `dl_lock`.

`dsl_deadlist_space_range()` sums `bpobj_space()` across entries in `(mintxg, maxtxg]`. It asserts that missing `mintxg` means no later entries exist, reflecting the invariant that callers supply actual deadlist keys unless querying through `UINT64_MAX`.

`dsl_deadlist_merge()` merges another deadlist object into an open deadlist. Old-format sources are iterated block-by-block. Modern sources move each child `bpobj` into the destination by birth key, remove the source ZAP key, then zero the source deadlist header.

`dsl_deadlist_move_bpobj()` removes all entries at or after `mintxg`, enqueues their child `bpobj`s into a destination `bpobj`, subtracts their aggregate space from the deadlist header, removes ZAP keys, and frees in-memory entries. Snapshot destroy uses this to move now-free blocks to pool free/obsolete lists.

## Research Notes

This file’s important subtlety is that modern deadlists separate key structure from block storage. Cloning generally copies key buckets, not contents. Destroy/merge paths move sub-objects rather than copying individual blocks when possible. Any change here must preserve the exact `(mintxg, maxtxg]` semantics because dataset written-space, would-free, promotion, rollback, and remap accounting all depend on those boundaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deadlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deleg.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deleg.c

## Role

`dsl_deleg.c` implements ZFS delegated administration permissions for DSL directories and datasets. It stores permission grants in ZAP objects, validates allow/unallow operations, retrieves effective delegation data, checks user access, propagates create-time permissions to new datasets, destroys delegation metadata, and checks whether delegation is globally enabled for a pool.

## Permission Storage Model

The file documents a two-level ZAP scheme. The top-level delegation ZAP on a dsl_dir maps “who keys” to jump ZAP objects. Who keys encode:
- local vs descendant permissions,
- users, groups, everyone, create-time grants,
- direct permissions vs named permission sets,
- named set definitions.

Examples include `ul$<id>` for local user permissions, `gd$<id>` for descendant group permissions, `el$` for everyone local permissions, `c-$` for create-time permissions, and `s-$@<name>` for named sets. The second-level jump object contains one boolean-like entry per permission or set name.

## Allow And Unallow Validation

`dsl_deleg_can_allow()` first requires the caller to have `allow`, then requires the caller to already have every permission they are trying to grant. It explicitly rejects delegating `allow` itself.

`dsl_deleg_can_unallow()` requires `allow` and then restricts removal to user/user-set entries matching the caller’s own UID. Non-user entries or entries for a different UID fail with `EPERM`.

These are policy helpers; the actual on-disk mutation is performed later through sync tasks.

## Mutation Sync Tasks

`dsl_deleg_set_sync()` holds the target dsl_dir, creates its `dd_deleg_zapobj` if absent, creates jump objects as needed with `zap_create_link()`, and updates each permission entry in the jump object. Each permission update is logged to pool history.

`dsl_deleg_unset_sync()` removes whole who entries when the nvpair value is not an nvlist, or removes individual permission names from a who jump object. Empty jump objects are destroyed and removed from the top-level ZAP. It logs both whole-who and individual permission removals.

`dsl_deleg_check()` verifies pool support for delegated permissions and that the target dsl_dir can be held. `dsl_deleg_set()` wraps check and set/unset sync functions in `dsl_sync_task()`.

## Retrieval

`dsl_deleg_get()` opens the pool and starting dsl_dir, then walks from the starting dsl_dir upward to the root. For each dsl_dir with a non-empty delegation ZAP, it builds an nvlist of whokeys and their permission nvlists. The resulting nvlist is ordered bottom-up by source dataset name, matching how delegated permissions are inherited and displayed.

## Access Checking

Access checking starts with `dsl_deleg_access()`, which holds the pool and dataset, then calls `dsl_deleg_access_impl()`.

`dsl_deleg_access_impl()`:
- returns `ECANCELED` if delegation is disabled on the pool,
- requires pool version support,
- treats snapshots as descendant-only for permission purposes,
- walks from the dataset dsl_dir to ancestors,
- respects non-global-zone constraints by requiring `zoned=on`,
- loads user/group/everyone named sets for each level,
- recursively expands named sets through set-includes-set entries,
- checks direct user, primary group, everyone, and supplemental groups,
- returns success on the first matching grant.

The named-set expansion uses an AVL tree of `perm_set_t` to avoid duplicate set names and to mark sets that have already been tested.

## Create-Time Permissions And Cleanup

`dsl_deleg_set_create_perms()` walks ancestors of a newly created dsl_dir and copies create-time direct permissions and create-time permission sets to the creator UID on the new dsl_dir. `copy_create_perms()` handles creating the target delegation ZAP/jump objects and copying entries.

`dsl_deleg_destroy()` destroys a delegation ZAP by destroying every jump object and then the top-level delegation object. `dsl_delegation_on()` returns the pool-level delegation setting through `spa_delegation()`.

## Research Notes

The important security boundary is that permission checking is hierarchical and context-sensitive: local grants apply only on the starting dataset, then checks switch to descendant mode while walking ancestors. Snapshots always use descendant mode. Named sets can include other named sets, so the AVL expansion logic is part of the effective authorization model.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deleg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_destroy.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_destroy.c

## Role

`dsl_destroy.c` implements destruction of snapshots and head datasets. It handles immediate and deferred snapshot destroy, batched snapshot destroy through ZFS Channel Programs, deadlist collapse, remap deadlist cleanup, old synchronous destroy for pre-async-destroy pools, async destroy via bptree, dsl_dir teardown, and cleanup of inconsistent datasets.

It is tightly coupled to `dsl_dataset.c`, `dsl_deadlist.c`, `dsl_dir.c`, scan state, feature flags, ZAP metadata, and DMU traversal.

## Snapshot Destroy Checks

`dsl_destroy_snapshot_check_impl()` requires the target to be a snapshot, have no long holds, and, for non-deferred destroy, have no userrefs and not be a branch point (`ds_num_children > 1`). Deferred destroy requires pool support for userrefs and is allowed even when userrefs or children prevent immediate deletion.

`dsl_destroy_snapshot_check()` treats missing snapshots as success so destroy operations are idempotent from the caller’s perspective.

## Snapshot Destroy Sync

`dsl_destroy_snapshot_sync_impl()` is the main snapshot deletion engine. It:
- handles deferred destroy by setting `DS_FLAG_DEFER_DESTROY`,
- logs history before namespace removal,
- notifies the scrub/scan subsystem,
- deactivates per-dataset features,
- rewires previous and next snapshot links and next-clones references,
- updates previous snapshot unique bytes when a deadlist range becomes unique,
- subtracts snapshot-used space,
- moves freed blocks from the next snapshot deadlist to the pool free bpobj,
- merges the destroyed snapshot deadlist into the next dataset’s deadlist,
- handles remap deadlist transfer/obsolete movement,
- collapses deadlist key ranges in clone heads and the head dataset,
- recalculates head unique bytes when deleting the most recent snapshot,
- adjusts refreservation accounting,
- evicts objsets before final free,
- removes the snapshot from the head snapnames ZAP,
- clears bootfs if needed,
- frees next-clones, properties, userrefs, and zapified dataset metadata,
- releases the dsl_dir reference.

Old-format deadlists are handled by `process_old_deadlist()`, which iterates the next deadlist’s old `bpobj`, either keeps blocks on the deadlist or frees them, updates previous unique bytes, adjusts snapused, and swaps deadlist objects.

## Remap Deadlist Handling

`dsl_destroy_snapshot_handle_remaps()` handles device-removal remap deadlists. It moves remap entries from the next snapshot to the pool obsolete bpobj for entries that are no longer referenced by surviving snapshots. It also merges the destroyed snapshot’s remap deadlist into the next dataset, creating the next remap deadlist if necessary, then destroys the old remap deadlist and decrements obsolete-counts feature state.

## Batched Snapshot Destroy

`dsl_destroy_snapshots_nvl()` normalizes the caller’s nvlist, wraps arguments for Lua, and evaluates a ZFS Channel Program. The Lua program first checks all snapshots, removes missing ones, accumulates errors, and only if there are no errors runs sync destroy for each. Returned int64 errors are converted to documented int32 errlist values.

`dsl_destroy_snapshot()` is a single-name wrapper around the nvlist path.

## Head Dataset Destroy

`dsl_destroy_head_check_impl()` requires a head dataset, expected long-hold count, no normal snapshots of the head, no child filesystems, and, for special clone cases, no blocking holds on a deferred-destroy origin snapshot that can be removed together.

`dsl_destroy_head()` unmounts clone origins in kernel builds, checks async-destroy support, and for old pools marks the dataset inconsistent before freeing all objects in open context to keep the sync transaction short. It then runs the actual sync destroy.

`dsl_destroy_head_sync_impl()`:
- logs history and scan destruction,
- detects whether a deferred-destroy origin snapshot should also be removed,
- clears dataset refreservation,
- deactivates dataset features,
- updates clone origin metadata and child counts,
- closes/frees normal and remap deadlists,
- destroys the ZIL,
- either traverses/frees blocks synchronously on old pools or adds the root bp to the pool async-destroy bptree,
- transfers used space to the free dir,
- removes clone references,
- evicts objsets,
- clears `dd_head_dataset_obj`,
- destroys snapnames and bookmarks ZAPs,
- clears bootfs,
- frees the dataset object,
- destroys the containing dsl_dir,
- optionally destroys the now-unreferenced deferred origin snapshot.

`dsl_dir_destroy_sync()` tears down the directory object: decrements parent filesystem counts, removes reservations, asserts zero usage, destroys crypto keys, child/properties/clones/delegation ZAPs, removes the child entry from the parent, and frees the dsl_dir object.

## Inconsistent Dataset Cleanup

`dsl_destroy_inconsistent()` is a `dmu_objset_find()` callback that destroys datasets marked inconsistent unless they still contain resumable receive state. It always returns 0 so the scan continues even if one dataset cannot be processed.

## Research Notes

Destroy paths are intentionally conservative and history is logged before namespace changes. The most delicate sections are deadlist key collapse, remap obsolete movement, async destroy feature activation, and clone/deferred-origin cleanup. This file assumes sync context and pool config writer lock for the major on-disk rewrites.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_destroy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dir.c

## Role

`dsl_dir.c` implements ZFS DSL directory objects: the hierarchical dataset namespace nodes that contain head datasets, children, properties, delegation metadata, clone origin metadata, quota/reservation state, usage accounting, filesystem/snapshot count limits, rename logic, and zapified extensible fields.

It is the parent accounting layer for `dsl_dataset.c` and the namespace layer used by create, destroy, rename, quota, reservation, limit, and stats operations.

## Directory Lifetime And Naming

`dsl_dir_hold_obj()` opens a dsl_dir object, validates bonus type/size, allocates and initializes `dsl_dir_t` if needed, loads encryption key object metadata and errata state, initializes properties and locks, holds the parent, resolves `dd_myname`, computes clone origin txg without recursively opening the origin dataset, installs the dbuf user, and holds the SPA for both open-to-close and instantiate-to-evict lifetime.

`dsl_dir_evict_async()` asserts no dirty/tempreserved/towrite state remains, releases the parent asynchronously, closes the SPA reference, finalizes properties, destroys the lock, and frees memory.

`dsl_dir_name()` recursively builds full dataset names, using `dd_lock` around `dd_myname`. `dsl_dir_namelen()` computes equivalent length without string concatenation. `getcomponent()` parses dataset path components and validates separators and length. `dsl_dir_hold()` resolves a full name under a specific pool, optionally returning a tail component that may be missing or be a snapshot suffix.

## Filesystem And Snapshot Limits

The header comment explains the feature-backed count/limit system. Filesystem and snapshot counts are stored as extensible ZAP properties only once the `SPA_FEATURE_FS_SS_LIMIT` feature is active. Counts are initialized lazily down a subtree when a limit is first set.

`dsl_dir_init_fs_ss_count()` recursively initializes `DD_FIELD_FILESYSTEM_COUNT` and `DD_FIELD_SNAPSHOT_COUNT`, skipping hidden `$` datasets and temporary `%` datasets/snapshots.

`dsl_dir_activate_fs_ss_limit()` runs a sync task that verifies feature support, activates the feature if needed, and initializes counts for the target subtree.

`dsl_fs_ss_limit_check()` checks whether adding filesystems or snapshots would exceed initialized limits while walking ancestors up to an optional common ancestor. It skips temporary snapshots when cred is NULL and stops at uninitialized nodes.

`dsl_fs_ss_count_adjust()` updates filesystem/snapshot counts on a dsl_dir and initialized ancestors, again skipping hidden/temp filesystem counts.

`dsl_enforce_ds_ss_limits()` decides whether limits should be enforced, not enforced, or enforced only above the current dataset based on global-zone privilege and delegated permission to modify the relevant limit property.

## Creation, Clone Detection, Stats

`dsl_dir_create_sync()` allocates a dsl_dir object, links it into the parent child ZAP or root pool directory, initializes parent object, child/property ZAPs, creation time, filesystem count, and used-breakdown flags.

`dsl_dir_is_clone()` checks for a non-origin-snap origin object. Accessors return used, compressed, quota, reservation, ratios, logical used, used-by-snap/head/refreservation/child, origin name, filesystem count, snapshot count, and last remap txg.

`dsl_dir_stats()` exports quota/reservation/logical-used, used breakdown when supported, filesystem/snapshot count, remap txg, and clone origin.

`dsl_dir_update_last_remap_txg()` zapifies the dir and monotonically updates `DD_FIELD_LAST_REMAP_TXG` through a sync task.

## Space Accounting And Reservations

`dsl_dir_dirty()` adds a dsl_dir to the pool dirty list and holds the dbuf until sync. `dsl_dir_sync()` clears current-txg temporary towrite accounting and releases that dirty hold.

The directory-level `parent_delta()` computes how much usage change should propagate to a parent when a reservation may already cover part of the usage.

`dsl_dir_space_available()` recursively combines parent availability, quotas, reservations, pool adjusted size at the root, optional pending writes, and a hypothetical ancestor delta.

Temporary reservation flow:
- `dsl_dir_tempreserve_space()` reserves ARC memory first, then dsl_dir space.
- `dsl_dir_tempreserve_impl()` checks refquota through `dsl_dataset_check_quota()` on the first iteration, checks dsl_dir quota or pool availability, updates `dd_tempreserved`, records reservations in a list, and recurses to parents with adjusted reservation pressure.
- `dsl_dir_tempreserve_clear()` releases both dsl_dir temp reservations and ARC temp reservations.

Actual usage flow:
- `dsl_dir_willuse_space()` records estimated positive space to write and recursively propagates parent deltas.
- `dsl_dir_diduse_space()` updates used/compressed/uncompressed bytes and used-breakdown buckets in syncing context, then propagates accounted deltas and reservation transfers to parents.
- `dsl_dir_transfer_space()` moves used bytes between breakdown categories without changing total usage.

## Quota And Reservation Properties

`dsl_dir_set_quota_check()` predicts the new quota property and rejects values below reservation or used-plus-pending-space when syncing or no pending writes exist. `dsl_dir_set_quota_sync()` writes the property, handles old-pool history logging, and updates cached `dd_quota`.

`dsl_dir_set_reservation_check()` predicts the new reservation, skips precise open-context checks, computes availability at parent/root, and rejects values that cannot fit or exceed quota. `dsl_dir_set_reservation_sync_impl()` updates `dd_reserved` and propagates the reservation delta to ancestors. `dsl_dir_set_reservation_sync()` writes the property and applies the implementation.

## Rename And Transfer Checks

`closest_common_ancestor()` and `would_change()` support movement between branches. `dsl_valid_rename()` validates descendant name lengths and nesting depth after a rename.

`dsl_dir_rename_check()` ensures the source exists, target parent exists, target name is free, pool is unchanged, descendants remain within name/nesting limits, count properties are initialized if filesystem/snapshot limits are active, encryption rules allow the move, the target is not inside the source subtree, and target branch has enough space and limit headroom.

`dsl_dir_rename_sync()` logs before mutation, adjusts filesystem/snapshot counts when moving between parents, transfers used and reserved-child accounting, removes the old parent ZAP entry, changes `dd_myname` and parent object/reference, adds the new parent ZAP entry, notifies property callbacks, and releases holds.

`dsl_dir_transfer_possible()` is the reusable check for moving usage/counts from one branch to another. It computes the common ancestor, adjusts source-side availability impact, checks target space, and checks filesystem/snapshot limits.

## Miscellaneous

`dsl_dir_snap_cmtime()` and `dsl_dir_snap_cmtime_update()` maintain snapshot namespace change time in memory. `dsl_dir_zapify()` converts the dsl_dir object to zapified metadata. `dsl_dir_is_zapified()` detects whether the backing object is zapified.

## Research Notes

This file is the hierarchical accounting authority. Dataset operations depend on it to correctly distinguish head, child, snapshot, refreservation, and child-reservation usage. Rename is especially sensitive because it must move namespace links, space accounting, count-limit state, parent references, and property notifications atomically in syncing context.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dir.c -->