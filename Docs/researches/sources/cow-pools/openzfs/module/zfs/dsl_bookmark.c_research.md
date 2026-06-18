# File Research: sources/cow-pools/openzfs/module/zfs/dsl_bookmark.c

## Purpose

`dsl_bookmark.c` implements ZFS bookmarks and redaction-list support. Bookmarks are named references to snapshot or bookmark creation points stored per head dataset. The file manages bookmark validation, lookup, creation, copying, redacted bookmark creation, listing properties, destruction, in-memory AVL caching, deadlist/FBN maintenance, and redaction-list traversal.

## Lookup And Validation

`dsl_bookmark_hold_ds()` splits a full bookmark name at `#`, validates the bookmark component, holds the containing dataset, and returns the short bookmark name.

`dsl_bookmark_lookup_impl()` looks up a bookmark by short name in the dataset bookmark ZAP. It zeroes the output `zfs_bookmark_phys_t` first so older v1 bookmarks have v2 fields zeroed. It uses `zap_lookup_norm()` so case-insensitive datasets are honored.

`dsl_bookmark_lookup()` resolves a full bookmark name and optionally verifies that the bookmark is an earlier point in another dataset’s timeline, returning `EXDEV` when the bookmark exists but is not an ancestor.

`dsl_bookmark_create_nvl_validate()` validates the user nvlist schema `{ newbookmark -> source }`: each destination is a bookmark path, each source is a snapshot or bookmark path, all destinations are in one pool, and destination names are unique.

## Creation

`dsl_bookmark_create_check_impl()` verifies that the destination bookmark does not exist and that the source snapshot/bookmark exists and is an ancestor of the destination dataset timeline. Snapshot sources use `dsl_dataset_is_before()`. Bookmark sources use `dsl_bookmark_lookup()` and translate `EXDEV` to `ZFS_ERR_BOOKMARK_SOURCE_NOT_ANCESTOR`.

`dsl_bookmark_set_phys()` fills `zfs_bookmark_phys_t` from a source snapshot: guid, creation txg/time, optional encryption IV set guid, and optional bookmark-written fields. When `SPA_FEATURE_BOOKMARK_WRITTEN` is enabled, it records referenced/compressed/uncompressed bytes and freed-before-next-snapshot values.

`dsl_bookmark_node_add()` creates the dataset bookmark ZAP if needed, adds the node to the dataset AVL, writes the smallest compatible on-disk record size, and increments feature counters for bookmarks and v2 bookmarks when needed.

`dsl_bookmark_create_sync_impl_snap()` creates a bookmark from a snapshot. It also supports redacted bookmarks. If a redaction list is requested, or the source snapshot is itself redacted, it allocates a redaction-list object, possibly uses a spill block if the bonus buffer is too small, initializes redaction-list metadata, increments redaction feature counters, adds the bookmark, and logs history.

`dsl_bookmark_create_sync_impl_book()` creates a bookmark from an existing bookmark by copying the physical fields, but intentionally clears `zbm_redaction_obj`. Copying a redaction bookmark creates a normal bookmark to avoid shared redaction-object lifetime problems.

`dsl_bookmark_create()` wraps checking and syncing in `dsl_sync_task()` for ordinary bookmark creation. `dsl_bookmark_create_redacted()` does the same for redacted bookmarks with explicit snap GUID lists.

## Property Fetching And Listing

`dsl_bookmark_fetch_props()` serializes bookmark properties into an nvlist. It supports guid, createtxg, creation time, ivset guid, referenced/logical referenced/refratio for bookmarks with FBN data, and redaction metadata such as `redact_snaps` and `redact_complete`.

`dsl_get_bookmarks_impl()` emits all bookmarks for a held head dataset from the in-memory AVL. `dsl_get_bookmarks()` handles pool and dataset holds by name. `dsl_get_bookmark_props()` retrieves all properties for one bookmark.

## In-Memory AVL Cache

Bookmarks are cached in `ds->ds_bookmarks`. `dsl_bookmark_compare()` sorts by creation txg, then by `ZBM_FLAG_HAS_FBN`, then name. This ordering is required by destroy and deadlist-maintenance logic so all bookmarks at the same txg with FBN data are adjacent.

`dsl_bookmark_init_ds()` initializes the AVL for a head dataset, reads the bookmark ZAP reference from the dataset ZAP, iterates bookmark ZAP entries, performs lookup for each bookmark, and adds nodes to the AVL. `dsl_bookmark_fini_ds()` destroys the AVL and frees all bookmark nodes.

## Destruction

`dsl_bookmark_destroy_check()` validates a batch destroy. Missing datasets or missing bookmarks are treated as already destroyed. Redaction bookmarks cannot be destroyed while their redaction list has long holds.

`dsl_bookmark_destroy_sync_impl()` removes a bookmark from ZAP and AVL, decrements v2/bookmark-written/redaction feature counters as appropriate, frees redaction-list objects, and updates deadlist/clones keys when the last FBN bookmark at a txg disappears and no snapshot still requires that key.

`dsl_bookmark_destroy_sync()` destroys all successfully checked bookmarks and, when a dataset’s bookmark ZAP becomes empty, destroys the ZAP, clears `ds_bookmarks_obj`, decrements the bookmarks feature counter, and removes `DS_FIELD_BOOKMARK_NAMES`.

`dsl_bookmark_destroy()` runs the destroy batch as a reserved-space sync task.

## Snapshot, Deadlist, And FBN Maintenance

The file keeps bookmark “freed before next snapshot” values consistent as snapshots are created, destroyed, promoted, or blocks die.

`dsl_bookmark_ds_destroyed()` is called when a snapshot is destroyed. It updates FBN values for bookmarks between the previous and destroyed snapshot, clears `ZBM_FLAG_SNAPSHOT_EXISTS` for bookmarks at the destroyed snapshot txg, and returns whether any FBN bookmark still requires the deadlist key.

`dsl_bookmark_snapshotted()` is called when a snapshot is created. It adds deadlist keys for FBN bookmarks newer than the previous snapshot because they now precede a snapshot.

`dsl_bookmark_next_changed()` recomputes FBN values for bookmarks at an origin snapshot when the next snapshot changes due to promote or clone swap.

`dsl_bookmark_block_killed()` updates in-memory FBN counters for affected bookmarks when a block is killed from the head dataset. It does not update the ZAP immediately because it may be called from zio interrupt context. Instead it marks bookmark nodes dirty.

`dsl_bookmark_sync_done()` writes dirty bookmark nodes to ZAP once per txg and clears their dirty flags.

`dsl_bookmark_latest_txg()` returns the newest bookmark txg for a dataset.

## Redaction Lists

`dsl_redaction_list_hold_obj()` holds a redaction-list object, creates a `redaction_list_t` user object on the bonus buffer when absent, detects spill storage, initializes long-hold refcounting, and attaches eviction cleanup.

`dsl_redaction_list_long_hold()`, `dsl_redaction_list_long_rele()`, and `dsl_redaction_list_long_held()` protect long-running users such as redacted sends from concurrent destruction. `dsl_redaction_list_rele()` releases bonus/spill dbufs.

`dsl_redaction_list_traverse()` verifies the redaction list is complete, optionally binary-searches to a resume bookmark, reads redaction entries block-by-block, adjusts the first entry for mid-range resume, and invokes a callback for each redaction block range.

## Feature Interactions

This file manages or consumes:

- `SPA_FEATURE_BOOKMARKS`
- `SPA_FEATURE_BOOKMARK_V2`
- `SPA_FEATURE_BOOKMARK_WRITTEN`
- `SPA_FEATURE_REDACTION_BOOKMARKS`
- `SPA_FEATURE_REDACTION_LIST_SPILL`
- `SPA_FEATURE_REDACTED_DATASETS`

It also interacts with encryption through bookmark v2 IV set GUIDs, which are needed for raw send correctness.

## Concurrency Notes

Most operations run under DSL config locks or syncing context. Bookmark nodes have `dbn_lock` for interrupt-context FBN updates in `dsl_bookmark_block_killed()`. Redaction lists use long-hold refcounts to block destruction while sends/traversals depend on them.
