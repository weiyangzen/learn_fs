# subset-b-008963 Research

Grouped source research for WiredTiger btree random cursor sampling, page read/return paths, salvage, split machinery, and btree statistics. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_random.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_random.c

## Purpose

`sources/storage-engines/wiredtiger/src/btree/bt_random.c` implements random row-store cursor positioning and random page descent. It supports `WT_CURSOR.next_random`, random page selection for cache eviction, and the heuristics used to avoid pathological behavior on pages with many deleted records, insert-list-only pages, or unbalanced trees. The source was read as a complete 634-line file.

## Important APIs, Types, and Functions

The public entry point is `__wt_btcur_next_random(WT_CURSOR_BTREE *cbt)`, which validates row-store support, initializes cursor state, chooses either a random leaf descent or a skip-sampling walk, and returns a key/value through `__cursor_kv_return`.

`__wt_random_descent(WT_SESSION_IMPL *session, WT_REF **refp, uint32_t flags, WT_RAND_STATE *rnd)` descends from the btree root to a random leaf. It has two personalities: ordinary sampling can read disk pages and avoids deleted/empty pages; eviction sampling, indicated by `WT_READ_CACHE`, only wants cache-resident pages and treats read failures/restarts as nonfatal.

Leaf selection is split across helpers:

- `__random_leaf` chooses a random record from the selected row-store leaf.
- `__random_leaf_disk` samples on-disk row slots and checks visibility.
- `__random_leaf_insert` searches for large insert lists worth sampling.
- `__random_leaf_skip` samples an insert skip list, with local retries around the selected node.
- `__random_skip_entries` estimates skip-list size by counting a high skip-list level and scaling by `WT_SKIP_PROBABILITY`.
- `__random_insert_valid` and `__random_slot_valid` temporarily set cursor position fields and delegate visibility/value checks to `__wti_cursor_valid`.
- `__random_root_inmem_ref` reservoir-samples in-memory children of the root when eviction sampling is configured to sample root children.

Important constants encode performance heuristics: `WT_RANDOM_SKIP_EVICT_SOON`, `WT_RANDOM_SKIP_PREDICT`, `WT_RANDOM_SKIP_LOCAL`, `WT_RANDOM_SKIP_RETRY`, `WT_RANDOM_SKIP_INSERT_ENOUGH`, `WT_RANDOM_SKIP_INSERT_SMALLEST_ENOUGH`, `WT_RANDOM_DISK_RETRY`, `WT_RANDOM_CURSOR_MOVE`, and `WT_RANDOM_DISK_ENOUGH`.

## Control Flow

`__wt_btcur_next_random` first rejects non-row-store btrees with `ENOTSUP`, increments cursor statistics, clears interface cursor key/value flags, and disables diagnostic cursor-order checking because it may call normal next/prev internally. If the cursor has no page or random sampling is disabled, it initializes cursor function state and calls `__wt_random_descent` under `WT_WITH_PAGE_INDEX`. A successful descent is followed by `__random_leaf`.

`__wt_random_descent` starts at the root and repeatedly chooses a child from each internal page. Eviction mode chooses a random child directly; regular sampling tries random children first and then a linear pass to avoid deleted or unusable pages. If all choices are unusable, it restarts from the root up to a retry budget. Page movement uses `__wt_page_swap`, so split races can restart the descent and other errors are returned after releasing what the swap path owns. Eviction mode avoids returning the root page; if it keeps finding only root, it may retry with in-memory root-child sampling enabled.

Once a leaf is selected, `__random_leaf` prefers large on-disk populations, then large insert lists, then a second disk retry for moderately populated or unmodified disk-backed pages. If these paths cannot find a visible record, it falls back to cursor movement from the start of the page, moving next or previous a random number of records and avoiding the immediately previous key once. This fallback is deliberately slower but handles pages with many deleted entries.

When random descent fails with `WT_NOTFOUND`, `__wt_btcur_next_random` does not immediately report not-found because the tree may contain valid records that random selection missed. It falls back to a tree walk using `__wti_tree_walk_skip`, where `next_random_leaf_skip` is estimated from file size, allocation size, and `next_random_sample_size`. If that also cannot find a ref, it falls back to `__wt_btcur_next`.

## State and Persistence Behavior

This file does not own persistent storage, but it manipulates cursor state (`cbt->ref`, `slot`, `ins_head`, `ins`, `compare`, `tmp`, `next_random_sample_size`, `next_random_leaf_skip`, `rnd`) and may acquire/release page references. It reads btree block-manager size metadata to estimate leaf skipping. It can schedule a page for eviction with `__wt_evict_page_soon` when a large insert skip list would make repeated random sampling expensive.

Returned key/value state is internal cursor state, not copied to durable storage. The fallback path stores the previous random key in `cbt->tmp` so the next call can avoid returning the same key once. Pages read with `WT_READ_WONT_NEED` semantics are made eviction-friendly through the lower page-read path.

## Dependencies and Integration Points

The file depends on core btree/session/page abstractions from `wt_internal.h`: `WT_CURSOR_BTREE`, `WT_BTREE`, `WT_PAGE`, `WT_REF`, `WT_PAGE_INDEX`, row-store page arrays, insert skip lists, visibility checks, page swap/release, and normal cursor next/prev.

Key integration points include `__wti_cursor_valid` for visibility and update resolution, `__cursor_kv_return` for cursor return formatting, `__wt_row_leaf_key` for materializing row keys, `__wt_btcur_next`/`__wt_btcur_prev` for fallback movement, `__wti_tree_walk_skip` for sampling forward through leaves, block-manager `size`, eviction stats, and `WT_WITH_PAGE_INDEX` split-generation protection.

## Risks and Edge Cases

Randomness is approximate rather than statistically exact. Large insert lists, page-local disk entries, and file-size-based leaf skipping can bias samples, but the code trades precision for speed and resilience in unbalanced trees.

Skip-list entry estimates assume `WT_SKIP_PROBABILITY == UINT32_MAX >> 2`; changing skip-list probability without updating this logic would misestimate list size. The `--i == 0` loop in `__random_leaf_skip` also depends on unsigned wrap behavior being avoided by the selection range and local retry design.

Concurrent splits, eviction, and page state transitions are expected. `__wt_random_descent` handles `WT_RESTART` and eviction-mode `WT_NOTFOUND`, but incorrect page-index generation use would risk stale `WT_REF` traversal.

The fallback path uses `cbt->tmp` to detect duplicate keys and includes a guard for `WT_DATA_IN_ITEM` because temporary buffers can point into pages that were later freed. Mistakes here can create use-after-free or false duplicate suppression.

Empty trees, all-deleted trees, and tiny trees are intentionally hard cases. The code avoids returning `WT_NOTFOUND` until normal traversal confirms emptiness, but in tiny datasets random quality remains limited.

## Test Signals

Useful tests include `next_random` on row-store tables with empty trees, single/two-record trees, many deleted records, large append-only insert lists, large on-disk pages, and mixed on-disk plus insert-list pages. Concurrency tests should combine random cursors with eviction, splits, checkpoints, and updates. Statistical tests should verify broad distribution on balanced and intentionally unbalanced row-store trees without requiring exact uniformity. Diagnostics should cover split-generation races, duplicate-avoidance behavior, and the `ENOTSUP` path for column-store objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_read.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_read.c

## Purpose

`sources/storage-engines/wiredtiger/src/btree/bt_read.c` implements the btree page acquisition path: turning a `WT_REF` in disk/deleted/memory/locked/split state into a safely hazard-protected in-memory page for a caller. It also handles disk reads, page-delta reconstruction, shared disk-image cache interaction, fast-delete instantiation, eviction pressure assistance, forced eviction of oversized pages, and read-related statistics. The source was read as a complete 819-line file.

## Important APIs, Types, and Functions

`__wt_page_in_func` is the main exported page-in function. In diagnostic builds it also records caller function and line for hazard-pointer debugging. It loops on `WT_REF` state until it either returns a usable page, returns `WT_NOTFOUND`/`WT_RESTART`, or propagates an error.

`__page_read` is the disk materialization path. It locks `WT_REF_DISK` or `WT_REF_DELETED` refs, reads or reconstructs the disk image, invokes `__wti_page_inmem`, instantiates updates when required, handles page-delete metadata, and finally publishes `WT_REF_MEM`.

`__page_read_build_full_disk_image` reconstructs a full disk image from a base image plus delta pages. It delegates row leaf deltas to `__wti_page_merge_deltas_with_base_image_leaf` and internal deltas to `__wti_page_merge_deltas_with_base_image_int`, records latency histograms, and increments delta read statistics.

`__evict_force_check` decides whether a large modified leaf page should be split or forcibly evicted before being returned to a reader. `__wt_page_release_evict` releases the caller's hazard pointer and immediately calls eviction while preserving correct `WT_REF` state transitions.

The file also defines histogram increment functions for internal and leaf page reconstruction latency via `WT_STAT_USECS_HIST_INCR_FUNC`.

## Control Flow

`__wt_page_in_func` updates cache/page-request statistics, honors session `WT_SESSION_IGNORE_CACHE_SIZE`, and then loops on the target ref state. `WT_REF_DELETED` may be skipped with `WT_READ_SKIP_DELETED`, returned as not-found for cache-only/no-wait reads, or sent to `__page_read`. `WT_REF_DISK` is read unless `WT_READ_CACHE` forbids disk I/O. `WT_REF_LOCKED` causes no-wait callers to return not-found and other callers to stall. `WT_REF_SPLIT` returns `WT_RESTART`. `WT_REF_MEM` attempts hazard acquisition unless eviction is disabled for the btree.

Before reading from disk, the function may ask application threads to assist eviction with `__wt_evict_app_assist_worker_check`. After a read, it marks the page as recently read but possibly `wont_need` so `__wt_evict_touch_page` can make it easy to evict. For in-memory pages, it may force eviction if the page has grown too large, provided the session is not resolving a transaction, not in no-split/no-reconcile modes that would make eviction futile, not checkpointing, and not operating on ingest/garbage-collect btrees.

`__page_read` first CAS-locks disk/deleted refs and sets `WT_REF_FLAG_READING` for normal disk reads so parent reconciliation can avoid examining the page in detail. If a deleted ref has no address, it creates a new leaf page. If a fast-delete is globally visible and the tree is not disaggregated/salvage/verify, it can avoid reading the old disk image by creating a fresh instantiated leaf page with `modify->instantiated`.

If a shared disk cache can satisfy the address, `__page_read` builds the in-memory page from the cached image. Otherwise it reads through `__wt_blkcache_read_multi`. A multi-item result means base plus deltas; the code allocates a large reconstruction buffer, merges deltas, verifies the reconstructed image in diagnostic builds, right-sizes the buffer, frees delta buffers, and uses the reconstructed image for page instantiation. If the shared cache can accept writes, it stores or deduplicates the disk image before `__wti_page_inmem`.

After page instantiation, the code copies disaggregated block metadata to `page->disagg_info`, optionally calls `__wti_page_inmem_updates`, instantiates fast-delete pages with `__wti_delete_page_instantiate`, tracks page-history read state, asserts readonly cleanliness, clears `WT_REF_FLAG_READING`, and publishes `WT_REF_MEM`.

On failure, `__page_read` carefully discards partially built pages, releases shared disk-cache references, frees buffers, clears reading state, and restores the previous ref state.

## State and Persistence Behavior

The primary state machine is `WT_REF` state: `WT_REF_DISK`, `WT_REF_DELETED`, `WT_REF_LOCKED`, `WT_REF_SPLIT`, and `WT_REF_MEM`. Disk reads temporarily own the transition through `WT_REF_LOCKED`; successful reads publish `WT_REF_MEM`; failures restore the prior state. `WT_REF_FLAG_READING` communicates to parent reconciliation that a page is being read from its on-disk form.

Persistent inputs are block-manager addresses and optional page-delta chains. Persistent outputs are not written here, but reconstructed disk images may be cached in the shared disk cache, and fast-delete instantiation affects future reconciliation semantics by setting `modify->instantiated`. Disaggregated storage metadata (`block_meta`, `old_rec_lsn_max`, `rec_lsn_max`) is copied into the in-memory page so later reconciliation/materialization can preserve storage ordering.

Cache state is also mutated: page memory footprint and read generation are touched via eviction helpers; large pages may be marked for urgent eviction; cache stuck/progress behavior is controlled by flags such as `WT_PAGE_EVICT_NO_PROGRESS`, `WT_PAGE_PREFETCH`, and `WT_READ_WONT_NEED`.

## Dependencies and Integration Points

The file integrates with the block cache (`__wt_blkcache_read`, `__wt_blkcache_read_multi`), shared disk-image cache (`__wt_shared_dsk_cache_get`/`put`/`release`), page image parser (`__wti_page_inmem`), update instantiation (`__wti_page_inmem_updates`), fast-delete logic (`__wti_delete_page_skip`, `__wti_delete_page_instantiate`, `__wt_page_del_visible_all`), transaction oldest updates, eviction (`__wt_evict_app_assist_worker_check`, `__wt_page_can_evict`, `__wt_evict`, `__wt_evict_touch_page`), hazard pointers, page history, and statistics.

Delta reconstruction depends on reconciliation/format code that emits page deltas and on verification code that validates reconstructed disk images. History-store cursor caching is pulled in before dirty eviction so page eviction can write historical content when necessary, but this is skipped for clean/checkpoint pages.

## Risks and Edge Cases

The read path is highly concurrent. Incorrect ordering around `WT_REF_FLAG_READING`, CAS state changes, or hazard pointer clearing could allow parent reconciliation, eviction, or readers to observe inconsistent state.

Fast-delete optimization must not run when obsolete values are needed. The code explicitly excludes disaggregated, salvage, and verify btrees because avoiding the read can lose page IDs or data needed by those modes.

Delta reconstruction allocates based on page sizing heuristics. Underestimating buffer needs, mishandling ownership after right-sizing, or failing to free delta buffers would cause memory corruption or leaks. Diagnostic verification is important because reconstructed images are later parsed as authoritative page images.

Shared disk-cache insertion has ownership-sensitive behavior: when the cache takes ownership the local buffer is nulled; when another thread wins the insert, the local buffer is freed and the shared item is used. Bugs here can double-free or leave pages referencing freed memory.

Forced eviction before returning a page can be counterproductive or deadlock-prone in special contexts. The code avoids checkpoint transactions, no-reconcile sessions, history store cases that cannot evict, ingest btrees, and sessions resolving transactions; regressions in these guards could stall reads or corrupt checkpoint semantics.

Stall/backoff behavior must balance CPU burn and latency. The function yields first, then assists eviction, then sleeps with warning messages after many waits.

## Test Signals

Important test coverage includes reading disk and deleted refs, cache-only/no-wait reads, skip-deleted reads, split restart propagation, fast-delete visible and not-visible pages, disaggregated pages, shared disk-cache hits/collisions, page-delta reconstruction for internal and leaf pages, and diagnostic verification failures. Concurrency tests should combine page reads with eviction, reconciliation, checkpoints, parent-page reconciliation, and forced eviction of oversized modified pages. Stress flags and failpoints should exercise locked-page waiting, hazard busy loops, and cleanup after errors during page build or shared-cache insertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_ret.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_ret.c

## Purpose

`sources/storage-engines/wiredtiger/src/btree/bt_ret.c` contains helpers that turn a positioned btree cursor into the key/value/time-window data exposed through the public cursor interface. It handles row-store keys, variable column-store record numbers, on-page values, update-chain values, and cell time-window extraction. The source was read as a complete 263-line file.

## Important APIs, Types, and Functions

`__wt_key_return(WT_CURSOR_BTREE *cbt)` publishes the current key to the interface cursor and sets `WT_CURSTD_KEY_INT`. It delegates the actual key selection to the internal `__key_return`.

`__wt_value_return(WT_CURSOR_BTREE *cbt, WT_UPDATE_VALUE *upd_value)` publishes a visible standard update value to the interface cursor and sets `WT_CURSTD_VALUE_INT`.

`__wt_value_return_buf(WT_CURSOR_BTREE *cbt, WT_REF *ref, WT_ITEM *buf, WT_TIME_WINDOW *tw)` references an original on-page value into a supplied buffer and optionally returns its time window. It handles both row leaf and variable column leaf pages.

`__wt_read_cell_time_window(WT_CURSOR_BTREE *cbt, WT_TIME_WINDOW *tw)` reads the time window of the current on-page cell when the cursor position maps to an original cell. `__wti_read_row_time_window` is a row-store-specific helper used here and elsewhere. `__read_col_time_window` is the local column-store cell helper.

`__read_page_cell_data_ref_kv` centralizes unpacked-cell data referencing and converts an overflow-removed race into `WT_RESTART`.

## Control Flow

`__key_return` first checks the page type. On row leaves, an insert-list position returns the key directly from `WT_INSERT`. An exact row-store search match swaps `cbt->row_key` and `cbt->tmp` so the cursor can safely own the generated search key instead of returning the temporary buffer that future searches may overwrite. Otherwise it materializes the key from the page's row slot with `__wt_row_leaf_key`. On variable column-store pages, the interface cursor record number is set from `cbt->recno`.

`__wt_key_return` clears the external key flag and avoids rebuilding a key if `WT_CURSTD_KEY_INT` is already set. This is important for operations such as search followed by update, where the cursor already has the correct internal key and may not be in a state that supports another return copy.

`__wt_value_return_buf` switches on page type. For row leaves, it first tries the encoded simple-value shortcut `__wt_row_leaf_value`, which also implies a globally visible initialized time window. Otherwise it unpacks the value cell and references data through `__read_page_cell_data_ref_kv`. For variable column-store pages it unpacks the column cell and follows the same data-reference helper.

`__wt_read_cell_time_window` refuses to return a time window when the cursor slot is invalid, when a row-store cursor is on an insert item, or when a variable column-store cursor's insert position does not actually match the on-page slot. It then copies the unpacked time window unless the cell is a delete cell, in which case column-store returns false.

`__wt_value_return` is the update-chain value return path. The caller must already have selected a visible non-deleted full standard update. The function asserts that assumption, points the interface cursor value at the update buffer, and marks it internal.

## State and Persistence Behavior

This file does not write persistent state. It mutates cursor-visible state: `cursor->key`, `cursor->value`, `cursor->recno`, and cursor standard flags. It also swaps `cbt->row_key` and `cbt->tmp` in the exact-match row-store path to preserve buffer lifetime across future searches.

Time-window state is copied from on-page cells into caller-provided `WT_TIME_WINDOW` objects. Simple encoded values synthesize an initialized/global time window because their full cell metadata was optimized during page instantiation.

The functions often return references to internal memory rather than copying data. The validity of those references is tied to cursor/page/update lifetime and the standard WiredTiger cursor rules.

## Dependencies and Integration Points

The file depends on row/column page layouts, cell unpacking, overflow handling, cursor state flags, and update visibility conventions. Important dependencies include `__wt_row_leaf_key`, `__wt_row_leaf_value`, `__wt_row_leaf_value_cell`, `__wt_cell_unpack_kv`, `__wt_page_cell_data_ref_kv`, row/column slot macros, and time-window macros.

Callers include search, next/prev, random cursor movement, and update paths that need to expose key/value data through `WT_CURSOR`. The `WT_RESTART` result for `WT_CELL_VALUE_OVFL_RM` integrates with higher-level retry loops when a checkpoint concurrently removes overflow data.

## Risks and Edge Cases

The biggest risks are lifetime and aliasing mistakes. Returning `cbt->tmp` directly after an exact search would allow a later search to corrupt the returned key; the buffer swap avoids that. Any new caller must respect the distinction between internal and external cursor flags.

The code assumes callers do visibility and delete handling before `__wt_value_return`; it asserts that the update is a full standard value and not marked `skip_buf`. Calling it with modify/tombstone/reserve updates would expose invalid data.

Overflow-removed cells are a race with checkpoint cleanup. `__read_page_cell_data_ref_kv` returns `WT_RESTART` so higher layers can retry rather than reading freed overflow content.

Column-store time-window extraction is only valid for matching on-page slots. Insert-list positions can sit near an on-page slot for a different record number, so `WT_CBT_VAR_ONPAGE_MATCH` is required to avoid returning the wrong cell metadata.

## Test Signals

Useful tests cover row-store insert-list keys, exact-search key buffer swapping, non-exact row page key materialization, variable column-store record-number return, simple encoded row values, overflow values, overflow-removed restart, update-chain value return, and cell time-window extraction for row leaves and column variable pages. Regression tests should combine search/update sequences with subsequent searches to catch key buffer lifetime bugs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_ret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_slvg.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_slvg.c

## Purpose

`sources/storage-engines/wiredtiger/src/btree/bt_slvg.c` implements WiredTiger btree salvage: scanning a damaged file for usable leaf and overflow pages, resolving overlapping key ranges, rebuilding a usable internal root, writing merged leaves when necessary, freeing discarded blocks, and installing a new clean checkpoint. The source was read as a complete 2431-line file.

## Important APIs, Types, and Functions

The exported entry points are `__wt_salvage(WT_SESSION_IMPL *session, const char *cfg[])` and `__wt_slvg_reconcile_free(WT_SESSION_IMPL *session, const uint8_t *addr, size_t addr_size)`. `__wt_salvage` drives the whole salvage procedure. `__wt_slvg_reconcile_free` is a callback used during salvage reconciliation to intercept overflow block frees and update salvage tracking instead of freeing immediately.

Core temporary types are:

- `WT_STUFF`, the per-salvage context containing session, tracked leaf pages, tracked overflow pages, a temporary root ref, page type, merge-free flag, scratch buffers, and progress counter.
- `WT_TRACK_SHARED`, shared physical metadata for a tracked page or split chunk: address, time aggregate, size, write generation, and overflow reference lists.
- `WT_TRACK`, a logical tracked key range for a page or page chunk. It references `WT_TRACK_SHARED`, records row or column start/stop ranges, missing column ranges, and flags such as `WT_TRACK_MERGE`, `WT_TRACK_CHECK_START`, `WT_TRACK_CHECK_STOP`, and `WT_TRACK_OVFL_REFD`.

Major helper groups include:

- Scanning/tracking: `__slvg_read`, `__slvg_trk_init`, `__slvg_trk_leaf`, `__slvg_trk_ovfl`, `__slvg_trk_leaf_ovfl`.
- Overflow reconciliation: `__slvg_ovfl_reconcile`, `__slvg_ovfl_discard`, `__slvg_ovfl_ref`, `__slvg_ovfl_ref_all`, `__slvg_ovfl_compare`.
- Range resolution: `__slvg_col_range`, `__slvg_col_range_overlap`, `__slvg_col_range_missing`, `__slvg_col_trk_update_start`, `__slvg_row_range`, `__slvg_row_range_overlap`, `__slvg_row_trk_update_start`.
- Tree rebuild: `__slvg_col_build_internal`, `__slvg_col_build_leaf`, `__slvg_row_build_internal`, `__slvg_row_build_leaf`, `__slvg_col_ovfl`, `__slvg_row_ovfl`.
- Cleanup/checkpoint: `__slvg_checkpoint`, `__slvg_merge_block_free`, `__slvg_cleanup`, `__slvg_trk_free`, `__slvg_trk_free_block`, `__slvg_trk_free_addr`.

Sorting callbacks compare tracked pages by address, key range, and write generation: `__slvg_trk_compare_addr`, `__slvg_trk_compare_key`, and `__slvg_trk_compare_gen`.

## Control Flow

`__wt_salvage` executes an explicit multi-step recovery pipeline. It allocates scratch buffers, tells the block manager salvage is starting, reads all salvageable blocks with quiet corruption handling, reconciles overflow references, discards unused overflow pages, sorts leaf pages by key and generation, resolves overlapping key ranges, fills missing variable-column ranges, builds a new internal root referencing the selected leaves or merged leaves, frees backing blocks from merged/discarded pages only after the new tree is built, writes a post-salvage checkpoint, informs the block manager salvage ended, and releases all temporary state.

`__slvg_read` repeatedly asks the block manager for the next salvage address, reads it through the block cache, reports validity back to the block manager, ignores and frees internal/block-manager pages, verifies candidate disk pages, and tracks row leaf, variable column leaf, and overflow pages. Mixed row and column leaf formats are rejected.

For leaf pages, `__slvg_trk_leaf` records key ranges and time aggregates. Variable column pages derive start from `dsk->recno` and stop from walking RLE cells. Row pages are instantiated into memory so the first and last full keys can be copied despite prefix compression. Both formats scan for overflow references and copy overflow addresses into the track record.

Overflow reconciliation happens before key overlap resolution. `__slvg_ovfl_reconcile` sorts leaf pages by descending generation and overflow pages by address, then gives each overflow page to the newest leaf page that references it. If a leaf references a missing or already-claimed overflow page, the leaf is discarded. `__slvg_ovfl_discard` frees overflow blocks that no selected page references.

Range resolution walks sorted leaf tracks and resolves overlaps by write generation. If one track supersedes another, the older range is deleted, truncated, or split. Column-store uses record-number arithmetic. Row-store uses btree collator comparisons and may reread a page to find the first key greater than a stop key. Tracks that need a rewritten subset are marked `WT_TRACK_MERGE`.

Tree rebuild creates a new root internal page with one `WT_REF` per selected leaf range. Unmodified tracks keep their original disk block address and simply mark their overflow records referenced. Merged tracks are read into memory, sliced with a `WT_SALVAGE_COOKIE`, reconciled into a new on-disk leaf, and then evicted to update the parent ref. Salvage clears `ref->addr` before reconciling merged leaves to avoid freeing original blocks too early.

Finally, `__slvg_checkpoint` builds a fresh checkpoint list instead of relying on old metadata checkpoints, evicts the new root under closing eviction to create a checkpoint, clears metadata checkpoints if no root was produced, or installs the single new checkpoint in metadata.

## State and Persistence Behavior

Salvage is intentionally persistent and destructive only after it has enough information to proceed. It calls block-manager `salvage_start`, `salvage_next`, `salvage_valid`, and `salvage_end`; frees blocks for ignored internal pages, invalid pages, discarded leaves, unused overflow pages, and merged original ranges; writes new merged leaf pages; writes a new internal root; and replaces the metadata checkpoint list with the salvage result.

Temporary state in `WT_STUFF` owns all tracked arrays and scratch buffers. `WT_TRACK_SHARED` reference counting allows one physical page to be split into multiple logical chunks without freeing the underlying blocks until the last chunk is discarded. Overflow reference flags are reused across phases: first to select usable leaves, then to determine which overflow records survive merge reconciliation.

During merged-page reconciliation, `session->salvage_track` points to the active `WT_TRACK` so `__wt_slvg_reconcile_free` can intercept attempts to free overflow blocks. This prevents double frees and preserves original data until salvage succeeds.

## Dependencies and Integration Points

The file integrates deeply with the block manager, block cache, disk verification, page instantiation, row/column page formats, reconciliation, eviction, metadata checkpoint management, time aggregates, collators, overflow block management, and verbose/progress reporting.

Important calls include `bm->salvage_start/next/valid/end`, `__wt_blkcache_read`, `__wt_verify_dsk`, `__wti_page_inmem`, `__wt_row_leaf_key_copy`, `__wt_reconcile`, `__wt_evict`, `__wt_btree_block_free`, `__wt_meta_block_metadata`, `__wt_meta_ckptlist_set`, and `__wt_meta_checkpoint_clear`.

The row/column overlap algorithms are intentionally parallel; comments warn that changes to one should be reviewed against the other.

## Risks and Edge Cases

Salvage prioritizes recovering a coherent tree from possibly corrupt data, not preserving every historical operation. It can resurrect deleted pages because page deletion may not write leaf pages and old leaf images may still exist.

Overflow handling is conservative. A leaf that references a missing or already claimed overflow page is discarded even if some keys on the page might otherwise be usable. This avoids complex per-key recovery but can lose good ranges.

Range splitting can create multiple logical tracks sharing one physical page. Reference counting and delayed block freeing are essential; freeing a source block before the salvage checkpoint succeeds could overwrite data needed by a later salvage attempt if the current run fails.

Row-store key handling depends on collator ordering and rereading pages to find adjusted start keys. Collator errors are difficult because sorting callbacks cannot propagate errors cleanly; the code uses `WT_IGNORE_RET` in qsort comparison.

Variable column RLE ranges can be split in the middle of an RLE unit. If an overflow RLE unit is already used by another chunk, the later chunk may have to delete that row by converting the overflow value cell to `WT_CELL_DEL`.

Metadata checkpoint replacement must be ordered carefully. Clearing old metadata before producing the new checkpoint could make a crash look like a newly created empty file.

## Test Signals

Tests should cover salvage of row-store and variable column-store files with valid leaves, invalid blocks, internal pages, mixed page formats, missing overflow pages, duplicate overflow references, overlapping ranges with newer and older generations, range splits into prefix/middle/suffix chunks, VLCS missing ranges, RLE splits, merged leaves with overflow values, and the no-leaf case that clears checkpoints. Fault-injection tests should fail during block reads, page instantiation, merge reconciliation, root eviction, and metadata checkpoint update to verify cleanup and delayed-free behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_slvg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_split.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_split.c

## Purpose

`sources/storage-engines/wiredtiger/src/btree/bt_split.c` implements WiredTiger's in-memory and reconciled btree split machinery. It converts reconciliation `WT_MULTI` results into new refs/pages, splits insert-heavy leaf pages in memory, replaces parent page indexes, deepens the root, splits oversized internal pages, removes empty pages through reverse splits, and rewrites problematic leaf pages in place after failed eviction. The source was read as a complete 2573-line file.

## Important APIs, Types, and Functions

Exported entry points are:

- `__wt_split_insert(WT_SESSION_IMPL *session, WT_REF *ref)` for in-memory split of a leaf page's last insert-list item into a new right page.
- `__wt_split_multi(WT_SESSION_IMPL *session, WT_REF *ref, int closing)` for splitting a reconciled page into multiple `WT_MULTI` outputs and replacing the old ref in its parent.
- `__wt_split_reverse(WT_SESSION_IMPL *session, WT_REF *ref)` for removing an empty page from its parent.
- `__wt_split_rewrite(WT_SESSION_IMPL *session, WT_REF *ref, WT_MULTI *multi, bool change_ref_state)` for one-for-one in-memory page rewrite.
- `__wt_multi_to_ref(...)` for converting a `WT_MULTI` reconciliation result into a populated `WT_REF`, optionally with a re-instantiated in-memory page.

Core internal functions include `__split_root`, `__split_internal`, `__split_parent`, `__split_parent_climb`, `__split_internal_lock`, `__split_ref_move`, `__split_ref_prepare`, `__split_ref_final`, `__split_multi_inmem`, `__split_multi_inmem_final`, `__split_multi_inmem_fail`, and `__split_safe_free`.

`WT_SPLIT_ERROR_PHASE` documents the error model: allocation/setup errors can return normally, errors after tree mutation are fatal/panic, and errors after a complete split are mostly ignored because the tree is already correct.

## Control Flow

All split paths protect page-index readers with `WT_WITH_PAGE_INDEX`, split generations, release/acquire barriers, and deferred frees through the stash mechanism. A split typically allocates replacement indexes/pages/refs first, switches to fatal error mode before making live tree changes, swaps a page index to publish the split, records a split generation, safely frees old indexes/refs after readers drain, updates memory accounting, and finally advances the split generation.

`__split_parent` is the central parent-index rewrite. It locks/uses the parent page, optionally filters globally deleted child refs, calculates the result index size, builds a new `WT_PAGE_INDEX`, replaces the target ref with new refs, publishes the new index, marks dirty state for delta-enabled internal pages, discards the replaced/deleted refs by setting them `WT_REF_SPLIT`, safely frees the old index, adjusts parent memory, and handles empty-parent/EBUSY cases.

`__split_root` deepens the tree by replacing the root's index with refs to newly allocated internal child pages. It chunks the old root refs among new children, moves refs with `__split_ref_move`, prepares child refs with `__split_ref_prepare`, swaps the root index, sets split generation, unlocks children, verifies key order when diagnostics are enabled, and stashes the old root index.

`__split_internal` performs a right split of a non-root internal page. The original page keeps the first chunk of refs via a replacement index; additional chunks become new internal children inserted into the parent through `__split_parent`. After the parent is updated, the original page's index is swapped to the first chunk and old index memory is deferred.

`__split_parent_climb` propagates internal-page splits upward. After a leaf split inserts new refs into a parent, it checks whether that parent should split based on memory footprint or key count. If it reaches the root, it deepens the tree; otherwise it lock-couples up the tree with parent page locks. It avoids internal splits during btree sync/checkpoint.

`__split_multi` converts reconciliation's `mod_multi` array into refs using `__wt_multi_to_ref`, calls `__split_parent`, finalizes moved update lists, clears and discards the original page. The `closing` path assumes exclusive access and requires disk addresses without update restoration.

`__split_insert` is a leaf-only in-memory split for pages with large insert lists. It creates a replacement ref for the original page, allocates a new right page/ref, moves the last skip-list insert to the right page, updates memory accounting and dirty transaction state, then replaces the old ref with two refs in the parent. On failure it restores the moved insert and original address.

`__split_multi_inmem` recreates an in-memory page from a reconciled disk image and restores unresolved update chains. It instantiates the new page, optionally instantiates updates from the disk image, inherits eviction/page state, truncates update chains that were safely written, handles prepared updates and tombstones carefully, searches the new page with a temporary btree cursor, reapplies updates with row/column modify helpers, and marks the restored page dirty with `first_dirty_txn = WT_TXN_FIRST`.

`__wt_split_rewrite` reuses the multi-inmem restore machinery for one-for-one rewrite after reconciliation could not evict a page. It swaps the new page into the existing ref, optionally changes ref state to `WT_REF_MEM`, and marks no-progress eviction when appropriate.

## State and Persistence Behavior

The file mutates the live in-memory btree topology. Persistent disk addresses produced by reconciliation are copied into new `WT_ADDR` objects in `WT_REF`s; disk images may be consumed to instantiate new in-memory pages; unresolved updates are moved or restored onto new pages. Parent page indexes are replaced atomically from the perspective of tree walkers, and old indexes/refs/keys are freed only when split generations make it safe.

Split generation state (`WT_GEN_SPLIT`, `pg_intl_split_gen`, `WT_SPLIT_PAGE_SAVE_STATE`, `__wt_gen_next`) protects readers that may still hold old page indexes. `__split_safe_free` either overwrites/frees immediately under exclusive access or stashes memory for later generation-based reclamation.

Dirty and cache state are updated throughout: pages are marked modified before topology changes; internal delta dirty state may be set; `WT_PAGE_INTL_PINDEX_UPDATE` disables delta building after parent index changes; memory footprint increments/decrements track moved refs, keys, indexes, insert items, and update chains.

The split code also owns special state transitions for discarded refs. Replaced refs and deleted refs are set to `WT_REF_SPLIT` so readers restart using the new parent index. Reverse split uses the same parent machinery with zero replacement refs.

## Dependencies and Integration Points

This file sits between reconciliation, eviction, update chains, page allocation, row/column search and modify, hazard/split generation machinery, page indexes, checkpoint, prefetch, disaggregated storage, and statistics.

Important dependencies include `__wt_page_alloc`, `__wt_page_modify_init`, `__wt_reconcile` outputs (`WT_MULTI`, `WT_SAVE_UPD`), `__wti_page_inmem`, `__wti_page_inmem_updates`, `__wt_row_search`, `__wt_col_search`, `__wt_row_modify`, `__wt_col_modify`, `__wt_ref_block_free`, overflow discard, cache accounting helpers, diagnostic key-order verification, timing stress hooks, and btree sync/checkpoint state.

Disaggregated storage integration appears in `__split_multi_inmem` and `__wt_multi_to_ref`, where block metadata and materialization-frontier checks preserve correctness for pages that may be pushed to `WT_REF_DISK`.

## Risks and Edge Cases

This is one of the highest-risk concurrency files in the btree layer. Once a page index is swapped, rollback is impossible because other threads may already be using the new topology. The `WT_SPLIT_ERROR_PHASE` transitions must stay correct or recoverable errors can become silent corruption.

Memory lifetime is delicate. Moved refs may still be visible through old indexes; instantiated row keys and addresses may point into disk images being discarded; page indexes cannot be freed until all readers leave the old split generation. `__split_ref_move` uses barriers and CAS when converting on-page addresses to off-page `WT_ADDR` structures to avoid races with reconciliation/eviction.

Checkpoint interactions are subtle. Internal splits are avoided during sync because checkpoint traversal can miss pages if topology changes while it is walking internal pages. Insert splits explicitly mark first dirty transaction as `WT_TXN_FIRST` so checkpoints include either the original page or both split pages.

Update restoration is complex for prepared transactions and modify chains. The code must retain enough older updates for rollback and future reconciliation while freeing updates written to data/history stores only after the new page is successfully installed.

Deleting globally deleted refs during parent splits can conflict with sync free-list calculation, VLCS leftmost namespace behavior, and prefetch queue lifetime; the code guards all three. Removing a prefetch-queued ref would let the prefetch thread dereference freed memory.

Overflow keys on internal row pages require cleanup when refs move or are discarded. Running cleanup twice can leak or double free blocks, so `cell_offset` is zeroed after handling.

## Test Signals

Key tests include multi-block leaf splits from eviction, in-memory insert splits for row and variable-column pages, reverse splits, root deepening, internal page splitting and climb propagation, split failures before and after publication, concurrent readers walking old page indexes, checkpoint plus insert split, no internal split during sync, globally deleted child cleanup, prefetch-flagged refs, overflow internal keys, prepared update restoration, modify-chain restoration, disaggregated split/materialization checks, and diagnostic key-order verification. Timing stress flags `WT_TIMING_STRESS_SPLIT_*` and failpoint `WT_TIMING_STRESS_FAILPOINT_EVICTION_SPLIT` are direct signals for this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_split.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_stat.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_stat.c

## Purpose

`sources/storage-engines/wiredtiger/src/btree/bt_stat.c` initializes and gathers btree data-source statistics, including static btree configuration, cache footprint metrics, reconciliation delta averages, optional cache-walk statistics, and optional full tree-walk page/content counts. The source was read as a complete 347-line file.

## Important APIs, Types, and Functions

`__wt_btree_stat_init(WT_SESSION_IMPL *session, WT_CURSOR_STAT *cst)` is the exported initializer called by statistics cursors. It asks the block manager for storage-level stats, sets btree configuration and cache metrics, computes average internal/leaf delta chain lengths, and optionally triggers cache-walk and tree-walk statistics.

`__stat_tree_walk` traverses the btree and resets/increments tree-derived counters. `__stat_page` dispatches per-page counting by page type.

Page-specific helpers are `__stat_page_col_var`, `__stat_page_row_int`, and `__stat_page_row_leaf`. They count column variable pages, row internal pages, row leaf pages, entries, deleted records, RLE expansion, overflow cells, and zero-length row values.

## Control Flow

`__wt_btree_stat_init` gets the btree, block manager, and data-source stats array. It first calls `bm->stat`, then sets configuration values such as fixed column length, maximum depth, max page/key/value sizes, and reconciliation multiblock maximum. It records dirty and total cache bytes using btree cache helpers and cache overhead calculation. It sets pre-compression max page sizes, computes average delta chain lengths only when the denominators are nonzero, then conditionally performs cache walk and tree walk based on `WT_STAT_TYPE_CACHE_WALK` and `WT_STAT_TYPE_TREE_WALK`.

`__stat_tree_walk` zeroes counters that it will rebuild, then walks the tree with `__wt_tree_walk` using `WT_READ_INTERNAL_OP | WT_READ_VISIBLE_ALL | WT_READ_WONT_NEED`. Each visited page is analyzed inside `WT_WITH_PAGE_INDEX`. On exit it releases the final walked page and normalizes `WT_NOTFOUND` to success.

`__stat_page_col_var` counts base page cells, RLE repetitions, overflow values, and adjusts entry/deleted counts according to update lists attached to each column cell and the append list. A cell delete or a time-window stop marks original content deleted; standard/modify updates can convert deleted originals back to live entries, and tombstones can convert live originals to deleted.

`__stat_page_row_int` increments row internal page count and, if a disk image is available, scans address cells to count overflow keys.

`__stat_page_row_leaf` counts insert-list entries before the first disk key, on-page row entries adjusted for update tombstones/reserves and time-window stops, insert lists after each on-page key, overflow values that have not been updated, overflow keys in the disk image, and empty values inferred from adjacent key cells or trailing keys.

## State and Persistence Behavior

This file does not mutate btree contents or persistent metadata. It writes statistic counters in `WT_DSRC_STATS` and may read pages into cache for tree-walk statistics. Tree-walk reads are marked `WT_READ_WONT_NEED` and internal-op/visible-all so statistics collection minimizes cache pollution and sees a broad internal view.

The statistics are snapshots and may race with concurrent updates. Update-chain inspection is best-effort for counts rather than a transactional user-visible result.

## Dependencies and Integration Points

Dependencies include block-manager stats, btree cache accounting, eviction cache stat walk, tree walking/page-in, page-index generation protection, row/column page macros, cell unpacking, time-window macros, insert skip lists, and update types.

The function is called by statistics cursor paths and fills data-source statistic slots through `WT_STATP_DSRC_SET`, `WT_STATP_DSRC_INCR`, and `WT_STATP_DSRC_INCRV`. It shares page read behavior with other internal operations by using `__wt_tree_walk` flags that keep statistics pages eviction-friendly.

## Risks and Edge Cases

Counts are approximations under concurrent modification. Insert lists and update chains can change while stats are being gathered, so these counters should not be treated as a fully isolated snapshot.

Column variable RLE plus partial updates is inherently approximate. The helper adjusts counts per update list but cannot perfectly classify future overflow status for updated values.

Overflow key counting depends on the disk image being present; if `page->dsk == NULL`, row internal overflow key and row leaf empty-value scans cannot inspect original cell layout.

Row leaf entry counts decrement for stopped time windows only when no update overrides the on-page value. Mistakes in update-type filtering (`RESERVE`, `TOMBSTONE`, `MODIFY`, `STANDARD`) would skew visible entry counts.

The tree walk reads pages and must release the last page on all exits. Regressions here can leak hazard pointers or pollute cache if `WT_READ_WONT_NEED` is dropped.

## Test Signals

Tests should cover statistics with and without `WT_STAT_TYPE_TREE_WALK`, row and column btrees, VLCS RLE and tombstones, row insert lists before/after disk keys, on-page stopped time windows, reserve updates, standard/modify updates, append lists, overflow keys/values, empty row values encoded in disk images, page-delta average calculations with zero and nonzero denominators, and tree-walk cleanup under `WT_NOTFOUND` and injected page-read errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_stat.c -->
