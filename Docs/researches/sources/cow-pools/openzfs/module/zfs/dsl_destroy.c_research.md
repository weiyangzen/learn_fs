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
