# subset-b-008964 research

Grouped source research for WiredTiger btree synchronization, verification, walking, column-store modification/search, and row-store key/modification helpers. Each section preserves the source path in its title and is wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_sync.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_sync.c

## Purpose
`bt_sync.c` implements `__wt_sync_file`, the btree-level flushing routine used for write-leaves and checkpoint sync operations. It walks in-memory btree pages, decides which dirty pages must be reconciled, optionally schedules parallel checkpoint work, updates checkpoint progress/statistics, preserves checkpoint consistency constraints, and starts a block-manager sync after write-leaves when configured.

## Important APIs, Types, And Functions
- `__wt_sync_file(WT_SESSION_IMPL *, WT_CACHE_OP)` is the exported entry point. It handles `WT_SYNC_WRITE_LEAVES` and `WT_SYNC_CHECKPOINT`; close/discard are rejected here.
- `__sync_checkpoint_can_skip` decides whether a dirty leaf page can be skipped during checkpoint because its first dirty transaction is newer than the checkpoint snapshot and all multiblock addresses are valid.
- `__sync_dup_hazard_pointer` and `__sync_dup_walk` duplicate walk positions for checkpoint eviction experiments and parallel checkpoint workers.
- `__sync_check_for_multiblock_rec` flags disaggregated leaf pages with pending multiblock split reconciliation for eviction.
- Core types are `WT_BTREE`, `WT_REF`, `WT_PAGE`, `WT_PAGE_MODIFY`, `WT_TXN`, `WT_MULTI`, and `WT_CACHE_OP`.

## Control Flow
For `WT_SYNC_WRITE_LEAVES`, the routine exits early if the btree is not modified, takes `btree->flush_lock`, captures the oldest transaction ID, and walks cached leaf pages using `WT_READ_CACHE | WT_READ_NO_WAIT | WT_READ_SKIP_INTL`. Dirty leaves whose `update_txn` predates the captured oldest ID are reconciled with `WT_REC_CHECKPOINT`; newer hot pages are left for the full checkpoint pass.

For `WT_SYNC_CHECKPOINT`, read-committed sessions first capture a snapshot. The function takes `flush_lock`, sets `session->syncing` and the btree `syncing` state through `WAIT` to `RUNNING`, drains eviction generation, resets obsolete time-window page counters, and derives reconciliation flags. It then walks the cache with no eviction and visible-all semantics, visiting leaves and internal pages. Clean pages contribute max transaction/timestamp state and may be checked for pending multiblock reconciliation. Dirty pages are either skipped via `__sync_checkpoint_can_skip`, reconciled directly, or pushed to parallel checkpoint workers for leaf pages. Internal pages wait for parallel leaf work before evaluating dirtiness.

Cleanup releases walk references, waits for parallel checkpoint workers on error or success, releases snapshots acquired by read-committed paths, updates checkpoint generation, clears syncing state, unlocks `flush_lock`, and optionally starts an async block sync for write-leaves.

## State And Persistence Behavior
Checkpoint sync manipulates durable state indirectly through reconciliation: dirty pages become replacement blocks, multiblock results, or clean pages with persisted addresses. It also updates `btree->rec_max_txn` and `btree->rec_max_timestamp` from clean page modification metadata so later logic can decide whether the tree must remain dirty for a future checkpoint. Skipped dirty pages re-mark the tree modified because the checkpoint itself cleared the modified flag before the final pass. `btree->syncing` and `session->syncing` gate eviction/split behavior so checkpoint does not race with namespace changes or disaggregated checkpoint generation constraints.

## Dependencies And Integration Points
This file depends on tree walking (`__wt_tree_walk`, `__wt_tree_walk_custom_skip`), hazard pointers, reconciliation (`__wt_reconcile`), checkpoint parallelism (`__wt_checkpoint_parallel_*`), transaction snapshots, eviction, block-manager sync, statistics, and disaggregated-storage page metadata. It is called from checkpoint/file-sync paths while higher-level schema/checkpoint coordination is already in place. The history store and disaggregated metadata are special-cased so their dirty content is never skipped.

## Risks
The main risks are concurrency and persistence correctness: skipping an unsafe dirty page can lose checkpoint-visible data; failing to hold/release duplicated hazard pointers can leak or free active pages; clearing `btree->syncing` before updating checkpoint generation could let eviction write pages into the wrong disaggregated checkpoint. Parallel checkpoint paths require strict finish points before internal pages are reconciled. The write-leaves oldest-ID cutoff is a performance/correctness tradeoff: it avoids chasing hot updates but depends on correct `update_txn` maintenance.

## Test Signals
Useful tests include checkpoint visibility with long-running transactions, read-committed metadata checkpoints, recovery/shutdown/rollback-to-stable checkpoints where skipping must be disabled, disaggregated multiblock split checkpoints, parallel checkpoint leaf/internal ordering, and timing-stress checkpoint eviction. Statistics such as `checkpoint_pages_visited_*`, `checkpoint_pages_reconciled`, history-store reconciliation counters, and checkpoint verbose timing are operational signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_sync_obsolete.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_sync_obsolete.c

## Purpose
`bt_sync_obsolete.c` implements the checkpoint-cleanup background thread. It scans eligible btrees after checkpoints, detects obsolete deleted pages and obsolete time-window metadata, marks parents dirty or pages dirty, and encourages eviction so later checkpoints can remove unneeded blocks and shrink checkpoint metadata.

## Important APIs, Types, And Functions
- `__wt_checkpoint_cleanup_create`, `__wt_checkpoint_cleanup_destroy`, and `__wt_checkpoint_cleanup_trigger` manage the server thread and condition variable.
- `__checkpoint_cleanup` is the thread body; `__checkpoint_cleanup_int` iterates eligible file URIs.
- `__checkpoint_cleanup_get_uri` scans metadata forward under read-uncommitted isolation to find the next eligible file URI.
- `__checkpoint_cleanup_eligibility` filters metadata entries using handle availability, logging, checkpoint address presence, durable timestamps, transaction visibility, write generation, history store, and tiered `.wtobj` exclusion.
- `__checkpoint_cleanup_walk_btree` opens a dhandle and walks its btree with `__wt_tree_walk_custom_skip`.
- `__checkpoint_cleanup_page_skip`, `__checkpoint_cleanup_obsolete_cleanup`, and `__sync_obsolete_cleanup_one` decide what to read and what to clean.
- `__sync_obsolete_inmem_evict_or_mark_dirty`, `__sync_obsolete_deleted_cleanup`, and `__sync_obsolete_disk_cleanup` implement page/ref-specific actions.

## Control Flow
Creation sets the checkpoint-cleanup server flag, reads configuration for cleanup method, interval, and per-file wait, opens an internal wait-capable session, allocates a condition variable, and starts the thread. The thread wakes periodically or on signal, skips work if disabled or if a disaggregated follower is not leader, and invokes the full cleanup iteration when enough time has elapsed.

The full iteration starts at `file:` and repeatedly selects the next metadata URI that is eligible. Each selected btree is opened, skipped if read-only, empty, original bulk-load, or unavailable, and walked. The custom skip callback avoids reading pages when cache pressure is high, when deleted/on-disk pages cannot produce cleanup benefit, or when non-aggressive cleanup should not reclaim logged-table space. Internal pages are traversed under a page-index generation and each child ref is inspected. Leaf pages already in memory are checked for obsolete stop times and obsolete time windows.

On-disk leaf-no-overflow pages whose stop time is globally visible are converted from disk to deleted by dirtying the parent and unlocking the ref in `WT_REF_DELETED`. Deleted refs with globally visible page-delete information dirty their parent so reconciliation can remove them. Clean in-memory pages with obsolete whole-page deletes are evicted soon; pages with overflow items are dirtied first so overflow blocks can be freed by reconciliation.

## State And Persistence Behavior
Cleanup does not directly free blocks. It changes in-memory btree/ref/page state so ordinary reconciliation and checkpoint persistence can remove obsolete references and overflow blocks safely. It increments `btree->checkpoint_cleanup_obsolete_tw_pages` and the connection-level obsolete btree counter to limit work. It may set `ref->dirty_state` for delta-enabled btrees when a disk ref becomes deleted. It marks parent pages dirty via `__wt_page_parent_modify_set`, marks page modify structures dirty via `__wt_page_modify_set`, and schedules eviction via `__wt_evict_page_soon`.

## Dependencies And Integration Points
The module integrates with metadata cursors, dhandle lookup/open/release, transaction visibility (`__wt_txn_visible_all`, `__wt_txn_has_newest_and_visible_all`), time aggregates, eviction pressure checks, the tree walker custom skip API, page-index/split generations, server flags, connection heuristic controls, logging configuration, history store URI handling, disaggregated leader state, and statistics/verbose logging.

## Risks
Eligibility and visibility mistakes can either retain too much obsolete data or dirty/delete pages too aggressively. The code intentionally uses best-effort races: ref state is checked before locking and may change, so callers must tolerate skips. Reading disk pages for cleanup can increase cache pressure; the skip callback contains several guardrails. Metadata scanning under read-uncommitted isolation must advance strictly forward to avoid looping or revisiting keys while metadata changes. Thread lifecycle must signal and join before closing the internal session.

## Test Signals
Tests should cover obsolete fast-deleted pages, pages with overflow items, obsolete time-window cleanup limits, logged-table reclaim-space mode, history store eligibility, tiered `.wtobj` exclusion, disaggregated follower skip behavior, cache-pressure skip behavior, and races with deleted/disk/memory ref transitions. Useful counters include `checkpoint_cleanup_pages_removed`, `checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_obsolete_tw`, `checkpoint_cleanup_pages_walk_skipped`, duration, handles processed, and success count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_sync_obsolete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_vrfy.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_vrfy.c

## Purpose
`bt_vrfy.c` implements logical btree verification for WiredTiger files and checkpoints. It coordinates block-manager verification, loads each checkpoint root, recursively validates tree structure and page relationships, verifies row/column key ordering, validates time aggregates and time windows, checks overflow references, optionally verifies history-store consistency, and includes disaggregated-storage checks for checkpoint size and page discard.

## Important APIs, Types, And Functions
- `__wt_verify(WT_SESSION_IMPL *, const char *cfg[])` is the main verify entry point.
- `WT_VSTUFF` carries verification configuration, scratch buffers, progress counters, layout counters, stable timestamp, and deferred read-corrupt errors.
- `__verify_config` and `__verify_config_offsets` parse verify/dump options.
- `__verify_tree` recursively verifies logical tree consistency after physical disk-image verification has loaded a page.
- `__verify_page_content_int` and `__verify_page_content_leaf` validate cells, timestamps, overflow items, and history-store ranges.
- `__verify_row_int_key_order` and `__verify_row_leaf_key_order` enforce row-store ordering across depth-first traversal.
- `__wt_verify_disagg_database_size`, `__verify_disagg_accumulate_size`, and `__verify_page_discard` validate disaggregated metadata invariants.
- `__verify_unique_btree_ids` checks stable constituent files in metadata for duplicate btree IDs.

## Control Flow
`__wt_verify` asserts checkpoint and schema locks are held, allocates scratch buffers, parses configuration, optionally dumps requested block offsets, and checks stable-file btree ID uniqueness. It obtains the checkpoint list and starts block-manager verification. For each non-fake checkpoint, it resets per-checkpoint state, loads the checkpoint root address, opens the checkpoint tree if non-empty, prints dump information when requested, and releases the file-exclusive eviction lock while doing recursive verification.

`__verify_tree` is depth-first. It logs page metadata, tracks tree shape, optionally dumps disk/page details, validates that page type matches btree type, checks column record-number ordering or row leaf ordering, validates child write generations, verifies page content, checks parent address-cell type versus page type, and descends into internal children. Child descent unpacks address cells, validates timestamp aggregates, accumulates disaggregated block sizes, reads the child with `__wt_page_in`, optionally continues after read failures under `read_corrupt`, recursively verifies, releases the child page, and asks the block manager to verify the address.

After the most recent checkpoint, verify may check disaggregated page discard and history-store consistency. The checkpoint is unloaded, eviction exclusivity is restored, and the loaded tree is discarded before moving to the next checkpoint.

## State And Persistence Behavior
Verify is mostly read-only, but it temporarily swaps checkpoint roots into the btree handle and uses eviction/file-discard operations to clean that in-memory state between checkpoints. It accumulates `records_so_far`, largest row key/address, tree-depth counters, and disaggregated block-size totals per checkpoint. With `read_corrupt`, it records the first read error in `vs->verify_err` and continues traversal where possible, returning the deferred error after cleanup.

## Dependencies And Integration Points
This verifier depends on block-manager verify hooks (`verify_start`, `verify_addr`, `verify_end`, checkpoint load/unload, page-id enumeration), metadata checkpoint list APIs, page read/build paths, disk-image physical verification from `bt_vrfy_dsk.c`, row key helpers, time-window validation, history-store verification, verbose/debug dump utilities, eviction exclusivity, and disaggregated-storage metadata. It is a central consumer of btree page layout invariants produced by reconciliation.

## Risks
Verification runs in a sensitive mode: it has an exclusive handle but repeatedly loads and unloads checkpoint roots while allowing eviction for memory pressure. Missing an eviction exclusivity transition can expose invalid roots. Key ordering logic depends on correct handling of internal 0th keys, corrupted first leaves, custom collators, and prefix/overflow keys. Stable timestamp checks are optional but strict when enabled. The disaggregated checkpoint-size comparison is currently disabled behind `if (false)` because known reconciliation edge cases can produce mismatch noise.

## Test Signals
Strong tests include corrupted child write generation, illegal page type for btree type, row internal and leaf key-order violations, column record-number ordering violations, invalid timestamp aggregates/time windows, bad overflow references, stable timestamp violations, duplicate stable btree IDs, history-store mismatch, read-corrupt traversal behavior, disaggregated page discard mismatch, and dump-mode diagnostic builds. The unit hook `__ut_verify_compare_page_id_lists` directly exercises page-id list comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_vrfy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_vrfy_dsk.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_vrfy_dsk.c

## Purpose
`bt_vrfy_dsk.c` performs physical disk-image verification for individual btree pages. It checks page headers, flags, versions, record-number rules, trailing bytes, page/cell type compatibility, safe cell unpacking, key ordering, prefix compression, timestamp validity, address validity, fast-delete metadata, column-store run-length encoding opportunities, and overflow/data chunk boundaries.

## Important APIs, Types, And Functions
- `__wt_verify_dsk_image` verifies one disk image with optional parent address/time aggregate context and flags.
- `__wt_verify_dsk` is a convenience wrapper for a `WT_ITEM` buffer using continue-on-failure behavior.
- `WT_VERIFY_INFO` carries the session, page tag, disk header, optional address, page size, current cell number, and verify flags.
- `__verify_dsk_row_int`, `__verify_dsk_row_leaf`, `__verify_dsk_col_int`, `__verify_dsk_col_var`, and `__verify_dsk_chunk` are page-type-specific validators.
- `__verify_dsk_addr_validity`, `__verify_dsk_value_validity`, and `__verify_dsk_addr_page_del` validate time aggregates/windows and fast-delete metadata.
- `__wti_cell_type_check` is exported and shared with logical verification to validate legal cell/page combinations.

## Control Flow
`__wt_verify_dsk_image` initializes `WT_VERIFY_INFO`, validates page type, validates whether `dsk->recno` is required or forbidden for the page type, masks allowed page flags, rejects invalid flag combinations, checks reserved bytes and page version, ensures bytes after `mem_size` are zero when a full size is available, checks non-empty page/data rules, and dispatches to a type-specific scanner.

Each scanner walks cells using `WT_CELL_FOREACH_VRFY`, a verify-specific loop that does not trust cells until `__wt_cell_unpack_safe` succeeds within the page boundary. Row internal pages enforce alternating key/address cells, no prefix or recno/rle fields, key count equal to half physical entries, address validity, block-manager address validity, optional fast-delete metadata validation, and sorted internal keys except for the special 0th key. Row leaf pages enforce key/value ordering, value time-window validity, overflow address validity, prefix-compression reconstruction, sorted keys, and empty-value flag consistency. Column internal pages validate address cells and their referenced addresses. Column variable pages validate values, overflow addresses, and detect adjacent identical values/deletes that should have been run-length encoded. Chunk pages validate `datalen` and zero trailing bytes.

## State And Persistence Behavior
This code is read-only and does not modify btree state. Its persistence relevance is that it validates the exact serialized on-disk representation before in-memory page construction or during verify. It treats block-manager `addr_invalid` returning `EINVAL` as corruption/nonexistent file page evidence. `WT_SESSION_QUIET_CORRUPT_FILE` suppresses error printing but not validation failure.

## Dependencies And Integration Points
The module integrates with low-level cell unpacking, page headers, btree collators, block-manager address validation, time aggregate/value validation, scratch buffers for printable key diagnostics, and diagnostic breakpoint/error reporting. Logical verification in `bt_vrfy.c` relies on the physical validation boundary so it can assume the in-memory page was built from a structurally safe disk image.

## Risks
The code intentionally handles untrusted bytes; any unchecked cell length or pointer arithmetic error can turn corruption into memory unsafety. Error policy differs between ordinary verification, salvage, quiet corrupt file mode, and continue-on-failure flags. Row key ordering must reconstruct prefix-compressed keys exactly, including mixed overflow and prefix-compressed keys. Fast-delete timestamp validation must combine page-delete data with the cell aggregate correctly or it may reject valid truncates or miss invalid ones.

## Test Signals
Test cases should cover invalid page types/versions/flags, wrong record-number presence, non-zero reserved/trailing bytes, empty page rejection and allowed empty pages, cell unpack boundary failures, illegal cell/page combinations, row adjacent key/value ordering errors, prefix compression count overflow, unsorted keys under custom collators, invalid block addresses, fast-delete metadata inconsistencies, invalid timestamp windows, column RLE missed opportunities, and overflow chunk length overrun.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_vrfy_dsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_walk.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_walk.c

## Purpose
`bt_walk.c` implements WiredTiger's generic in-memory btree traversal primitive. It moves a caller's `WT_REF *` forward or backward through the tree, optionally skipping internal/deleted/cache-miss pages, invoking custom skip callbacks, counting visited refs, and protecting traversal with hazard pointers and page-index generations while concurrent splits and eviction occur.

## Important APIs, Types, And Functions
- `__wt_tree_walk` moves to the next or previous page.
- `__wt_tree_walk_count` also reports a reference-visit count.
- `__wt_tree_walk_custom_skip` lets callers provide a skip function such as checkpoint cleanup.
- `__wti_tree_walk_skip` skips a requested number of leaf pages.
- `__tree_walk_internal` is the shared traversal engine.
- `__split_prev_race` detects split races that can cause backward walks to skip namespaces.
- Key types are `WT_REF`, `WT_PAGE_INDEX`, `WT_REF_STATE`, and read flags such as `WT_READ_PREV`, `WT_READ_CACHE`, `WT_READ_SKIP_INTL`, `WT_READ_NO_WAIT`, `WT_READ_TRUNCATE`, `WT_READ_VISIBLE_ALL`, and `WT_READ_SEE_DELETED`.

## Control Flow
The shared walker asserts it can reason about visibility, derives default deleted-page skipping unless rollback-to-stable or explicit see-deleted is active, saves the original ref, enters the page-index generation, and starts from the root if no ref is active. It then uses slot arithmetic to descend to the next leaf or ascend/post-order-return internal pages depending on direction and flags.

When descending, it checks current ref state, cache-only/no-wait restrictions, truncate deletion opportunities, visibility of deleted pages, and caller skip callbacks. It swaps hazard pointers with `__wt_page_swap`, returning leaves immediately and coupling through internal pages. On `WT_NOTFOUND`, it treats cache misses/deleted races as expected. On `WT_RESTART`, it releases coupled pages and restarts from the original position/root. On backward walks, `__split_prev_race` validates parent/child page-index consistency and restarts when internal splits could otherwise make the traversal choose the wrong predecessor.

At completion or error, it logs very slow walks, releases the coupled page and original ref, leaves the page-index generation, and returns the resulting page in `*refp` or `NULL` at end-of-walk.

## State And Persistence Behavior
The walker is in-memory only, but it controls access to pages that persistence operations depend on. Hazard pointers prevent eviction of the returned page and coupled ancestors during movement. It may mark empty internal pages for eviction and may invoke fast-delete logic in truncate mode. It updates `pindex_hint` opportunistically to speed later slot lookup.

## Dependencies And Integration Points
Tree walking is used by checkpoint sync, eviction, verification, checkpoint cleanup, compaction, truncate, and cursor scans. It depends on page-swap/read code, hazard pointer release, page-index generation macros, split race helpers, delete-page visibility helpers, prefetch, eviction scheduling, transaction visibility flags, and read-generation flags.

## Risks
The highest-risk behavior is concurrent split handling. Forward walks and backward walks have different safety properties, and the backward path has explicit race detection to avoid skipped namespaces. Misused flags can accidentally read pages into cache, skip deleted pages needed by rollback/truncate, or return internal pages to callers that expect leaves only. Error cleanup must release both the original and coupled refs exactly once.

## Test Signals
Tests should exercise forward and backward cursor walks across internal splits, append workloads, cache-only checkpoint walks, truncate walks that fast-delete pages, rollback-to-stable walks that see deleted refs, custom skip callbacks, leaf-skip counting, empty internal page eviction hints, and long-walk warning behavior. Concurrency stress with page splits and eviction is especially important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_walk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/col_modify.c -->
# sources/storage-engines/wiredtiger/src/btree/col_modify.c

## Purpose
`col_modify.c` implements column-store insert, update, delete, reserve, tombstone, append, and update-chain restoration on a pinned column-store leaf page. It creates or prepends `WT_UPDATE` chains, allocates column `WT_INSERT` skiplist nodes, serializes insertion into page modification structures, and records successful cursor writes in the transaction operation log.

## Important APIs, Types, And Functions
- `__wt_col_modify` is the column-store modification entry point.
- `__col_insert_alloc` allocates a record-number keyed `WT_INSERT` with skiplist next pointers.
- Important structures include `WT_CURSOR_BTREE`, `WT_PAGE`, `WT_PAGE_MODIFY`, `WT_INSERT_HEAD`, `WT_INSERT`, `WT_UPDATE`, and transaction/session state.
- It calls shared serialization APIs: `__wt_update_serial`, `__wt_insert_serial`, and `__wt_col_append_serial`.

## Control Flow
The function validates that the caller supplied either a value to allocate an update, an existing update/list, or a reserve/tombstone request. It ensures the page has a modify structure. If no update list is supplied, it detects append operations when the recno is out of band or beyond the leaf's last record and clears cursor insert/search state.

If the search found an existing insert for the exact record, the code allocates or prepends updates, checks transaction modify conflicts, records a transaction update, links the new update to the old chain, and serializes the update-chain head swap. If no exact insert exists, it chooses the append list or per-slot update list, allocates an insert head if necessary, allocates a skiplist node, creates or attaches the update chain, initializes skiplist next pointers from cursor search stacks, and serializes either append or normal insertion.

After the update is linked, cursor-originated non-reserve changes are logged with `__wt_txn_log_op`, and append operations record the assigned recno in the transaction operation for prepared transaction lookup.

## State And Persistence Behavior
This file mutates in-memory update chains and insert lists; persistence happens later via reconciliation and logging. It updates page memory through serialized insertion functions and transaction state through `__wt_txn_modify`. Append insertion may allocate the final record number in `__wt_col_append_serial`, then stores it in transaction state. `prev_durable_ts` on new updates records conflict-check history for timestamp rules.

## Dependencies And Integration Points
Column modify depends on prior column search state (`cbt->compare`, `cbt->slot`, `cbt->ins`, `cbt->ins_head`, search stacks), page modify allocation, update allocation, transaction conflict checks, transaction logging, skiplist depth selection, and rollback cleanup. It is used by cursor operations, range truncate patterns, update restore eviction, and internal update-list restoration.

## Risks
The tricky paths are append detection, updating a record inside a run-length encoded on-page cell where `ins_head` exists but `ins` does not, and error ownership after updates are linked into page memory. Once an update is inserted into the chain, rollback logic owns cleanup; freeing it locally would corrupt page state. Restoration paths assert that existing chains are empty or contain only allowed prepared-restored content. Concurrent insert/update races depend on the serialization functions and correctly initialized search stacks.

## Test Signals
Tests should cover appends with `WT_RECNO_OOB`, updates beyond the last on-page record, updates inside RLE cells, tombstone/reserve writes, restore of full update chains, conflict detection against existing updates, transaction log failure after linking, exclusive versus non-exclusive insert serialization, and rollback cleanup after partial failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/col_modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/col_srch.c -->
# sources/storage-engines/wiredtiger/src/btree/col_srch.c

## Purpose
`col_srch.c` searches variable-length column-store btrees by record number. It descends internal column pages, pins the target leaf, searches on-page variable-column cells and update/append skiplists, and positions `WT_CURSOR_BTREE` fields so reads and modifications know whether the match is on-page, inserted, before-page, or past-end.

## Important APIs, Types, And Functions
- `__wt_col_search` is the exported search routine.
- `__check_leaf_key_range` is a fast parent-range check when repositioning on a known leaf.
- It uses `__col_var_search`, `__col_var_last_recno`, `__col_insert_search`, `WT_COL_UPDATE_SLOT`, and `WT_COL_APPEND`.
- Key state lives in `WT_CURSOR_BTREE`: `ref`, `recno`, `slot`, `compare`, `ins_head`, `ins`, insert stacks, and flags such as `WT_CBT_VAR_ONPAGE_MATCH`, `WT_CBT_READ_ONCE`.

## Control Flow
The search clears cursor position state and maps `WT_RECNO_OOB` append searches to `UINT64_MAX` for descent. If the caller supplied a leaf, it may check the leaf's range using the ref's starting recno and the parent's next child starting recno; failure returns without a full tree search.

Full-tree search starts at the root and repeatedly binary-searches `WT_PAGE_COL_INT` page indexes to choose the child whose starting recno is the greatest lower bound of the target. The last slot has an append fast path with split-race detection. Child descent uses `__wt_page_swap` with restart support, and a split restart begins again at the root because the namespace may have moved above the current page.

On the leaf, `WT_RECNO_OOB` returns compare -1 without searching because allocation happens in modify. For normal recnos before the leaf start, it positions at slot 0 and compare 1. For on-page matches, it sets recno, slot, compare 0, marks `WT_CBT_VAR_ONPAGE_MATCH`, and then looks for an exact update-list insert. For past-end searches, it checks the append list first, then the last per-slot update list, and sets compare relative to the closest insert if found.

## State And Persistence Behavior
The routine does not persist data. It pins the selected leaf via page-swap/hazard-pointer behavior and prepares cursor state used by later reads or writes. It updates `btree->maximum_depth` when a deeper descent is observed.

## Dependencies And Integration Points
Column search integrates with internal page-index split generation, page swap/read code, variable-column on-page search helpers, column insert skiplist search, cursor flags, and column modification. Modification correctness depends on search stacks and compare values initialized here, especially for appends and per-slot update insertion.

## Risks
Split races during descent can misplace a search unless `WT_RESTART` and the last-slot descent race are handled correctly. Leaf-only repositioning depends on parent page-index hints that may be stale, so it validates the hint before using the next slot. Past-end behavior is subtle because append-list entries are closer than on-page last-record state, and cursor flags must indicate when an on-page value exists under an update list.

## Test Signals
Tests should search exact on-page records, exact update-list records, records before a leaf, records past a leaf/table end, append out-of-band recnos, leaf-only repositioning with safe and unsafe leaves, parent split races, stale `pindex_hint`, and read-once descent behavior. Follow-on modify tests are good signals because incorrect search stacks usually surface as insert serialization failures or misplaced updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/col_srch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/row_key.c -->
# sources/storage-engines/wiredtiger/src/btree/row_key.c

## Purpose
`row_key.c` reconstructs and optionally instantiates row-store leaf keys. Row-store pages may store keys directly, as overflow references, as instantiated `WT_IKEY` copies, or prefix-compressed against earlier keys. This file supplies the slow-path logic used when the fast inline key accessor cannot directly return a complete key.

## Important APIs, Types, And Functions
- `__wt_row_leaf_key_copy` returns a stable copied key.
- `__wt_row_leaf_key_work` reconstructs a key and optionally installs an instantiated copy in the page.
- `__wt_row_ikey_alloc`, `__wti_row_ikey_incr`, and `__wti_row_ikey` allocate/install `WT_IKEY` objects.
- Key structures and helpers include `WT_ROW`, `WT_IKEY`, `WT_CELL_UNPACK_KV`, `WT_ROW_KEY_COPY`, `__wt_row_leaf_key_info`, and `__wt_dsk_cell_data_ref_kv`.

## Control Flow
The slow path starts at the requested row slot and rolls backward looking for a usable uncompressed or instantiated non-overflow key. If it finds a direct non-prefix key or non-overflow instantiated key, it may switch to forward reconstruction. Overflow keys cannot provide a prefix base for other keys, so they are skipped as bases. If the requested key itself is overflow, the code reads it under `btree->ovfl_lock` and retries if reconciliation changed the cell to removed-overflow while the page had an instantiated replacement.

For prefix-compressed keys, the code may use the page's prefix group root (`prefix_start`/`prefix_stop`) to reconstruct directly. Otherwise it records a backward jump point where prefixes shrink, then rolls forward from a base key, repeatedly truncating the buffer to the prefix length and appending suffix bytes until it reaches the target slot.

If `instantiate` is requested, the reconstructed key is copied into a new `WT_IKEY` and installed with an atomic compare-and-swap into the row slot. On success, the page memory footprint is increased; on race loss, the allocated key is freed.

## State And Persistence Behavior
The file changes only in-memory page state by optionally replacing row key references with instantiated `WT_IKEY` objects and increasing cache memory accounting. It reads overflow key data from disk/block cache when needed but does not alter persisted content.

## Dependencies And Integration Points
Row key reconstruction is used by row search, verification, debugging, and modification paths that need full keys from a leaf. It depends on row page memory layout, cell unpacking, overflow locking, block-cache cell data reads, atomic pointer updates, and cache accounting. Diagnostic builds assert that instantiated keys are not overwritten and are not installed after a ref has split.

## Risks
Prefix-compressed reconstruction is easy to get wrong around overflow keys, mixed instantiated/on-page keys, and concurrent overflow removal. The code explicitly copies row key references because they may change underfoot. Installing instantiated keys must account for races with other threads and page splits. Buffer management must preserve prefixes while growing and appending suffixes.

## Test Signals
Tests should cover direct on-page keys, copied keys, prefix-compressed keys requiring backward then forward reconstruction, prefix group reconstruction, overflow requested keys, overflow keys used as non-bases, concurrent overflow removal/retry, repeated random search instantiation, reverse cursor instantiation behavior, and races where another thread instantiates the key first.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/row_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/row_modify.c -->
# sources/storage-engines/wiredtiger/src/btree/row_modify.c

## Purpose
`row_modify.c` implements row-store page modification and update-chain cleanup. It allocates page modify structures, inserts or updates row-store `WT_INSERT` skiplists and `WT_UPDATE` chains, logs cursor-originated transaction operations, and scans long update chains for obsolete globally visible suffixes that can be freed or should trigger forced eviction.

## Important APIs, Types, And Functions
- `__wt_page_modify_alloc` allocates and atomically installs `WT_PAGE_MODIFY`.
- `__wt_row_modify` is the row-store insert/update/delete/reserve/tombstone entry point.
- `__wt_update_obsolete_check` truncates obsolete update chains and schedules eviction for very long chains.
- `__row_insert_alloc` creates row-keyed `WT_INSERT` nodes.
- Major collaborators are `__wt_update_serial`, `__wt_insert_serial`, `__wt_txn_modify_check`, `__wt_txn_modify`, `__wt_txn_log_op`, `__wt_txn_op_set_key`, and `__wt_free_obsolete_updates`.

## Control Flow
`__wt_page_modify_alloc` initializes the page modification spinlock and installs the modify structure with CAS, charging page memory only for the winner.

`__wt_row_modify` validates its input mode, ensures a modify structure, then branches on `cbt->compare`. For exact matches, it targets either the on-page update array slot or the existing insert's update pointer. Cursor-originated writes check conflicts, allocate a new update, assign a transaction ID, and save the value into `cbt->modify_update`. Internal restore paths measure and prepend an existing update list, with special assertions for history-store and prepared/disaggregated cases. The new update is linked to the old chain and serialized into place.

For inserts, the code allocates the row insert-head array with an extra smallest-key slot, chooses the slot from `WT_CBT_SEARCH_SMALLEST` or the search slot, optionally runs diagnostic lower-bound checks against the parent separator, allocates the insert head, skiplist node, and update, initializes skiplist next pointers from the search stack, and serializes insertion.

After linking, cursor-originated non-reserve writes are logged and the key is copied into transaction operation state. Error cleanup frees only objects that have not been inserted into page memory; linked updates are left for rollback.

`__wt_update_obsolete_check` try-locks the page, scans an update chain for a globally visible data update after which older updates can be freed, avoids truncating chains requiring history-store cleanup, schedules eviction if the chain exceeds 1000 updates, and records transaction/timestamp state to avoid repeated scans of long chains.

## State And Persistence Behavior
This file mutates in-memory row modification state and transaction state. Durable effects occur later through write-ahead logging and reconciliation. Page memory accounting is updated for modify allocation and serialized insert/update functions. Transaction modify/log state ensures rollback, prepare, and recovery can find the corresponding key/update. Obsolete update removal changes in-memory chains only when a globally visible value safely terminates history needed by readers.

## Dependencies And Integration Points
Row modify depends on row search state (`compare`, `slot`, `ins`, search stacks, `WT_CBT_SEARCH_SMALLEST`), transaction conflict/visibility machinery, history-store special rules, prepared update preservation, disaggregated restore behavior, skiplist serialization, page locks, cache accounting, and eviction scheduling. It is a high-traffic path for `WT_CURSOR.insert/update/remove/reserve` on row-store tables.

## Risks
Ownership after partial failure is the major risk: after an update is linked into page memory, local cleanup must not free it. The smallest-key insert slot can corrupt tree ordering if used on a non-leftmost child with a key below the parent separator, hence the diagnostic check. Restore paths have strict assumptions about existing update chains. Obsolete-chain truncation must not discard updates needed for history-store deletion or active readers, and long chains can cause performance regressions if eviction is not triggered.

## Test Signals
Tests should cover on-page updates, insert-list updates, new inserts before first key and between keys, smallest-slot lower-bound diagnostics, tombstone/reserve operations, internal update-list restoration, history-store-specific assertions, prepared update preservation, transaction log/key recording failure after linking, rollback cleanup, obsolete update truncation, long-chain forced eviction, and concurrent modify allocation races.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/row_modify.c -->
