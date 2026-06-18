# subset-b-008962 research

Grouped research report for WiredTiger B-tree sources. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_debug.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_debug.c

Purpose: diagnostic-only B-tree and disk-page dumping code guarded by `HAVE_DIAGNOSTIC`. It exposes debugger-friendly helpers for printing block addresses, disk pages, in-memory page trees, cursor pages, and history-store state while respecting redaction controls unless explicit unredaction is requested.

Important APIs/types/functions: `WT_DBG` is the local output context with session, scratch buffers, optional history-store cursor, output file/event handler, formats, and flags. Public/debugger entry points include `__wt_debug_set_verbose`, `__wt_debug_addr_print`, `__wt_debug_addr`, `__wti_debug_offset_blind`, `__wt_debug_disagg_page_id`, `__wt_debug_offset`, `__wti_debug_disk`, `__wt_debug_tree_shape`, `__wt_debug_tree_all`, `__wt_debug_tree`, `__wti_debug_page`, `__wt_debug_btree_cursor_page`, and `__wt_debug_btree_cursor_tree_hs`. Internal printers cover cells, refs, update chains, skip lists, modify updates, time windows, and page metadata.

Control flow: setup flows through `__debug_config`, which allocates scratch buffers, opens an output file or buffered event-handler message stream, optionally opens a history-store cursor, and copies B-tree key/value formats. Disk dump entry points read through the block/cache layer, then call `__wti_debug_disk`, which prints page headers and walks address or key/value cells by page type. In-memory dumps start from a supplied ref or `S2BT(session)->root`, print metadata through `__debug_page_metadata`, and optionally recurse through internal refs under `WT_WITH_PAGE_INDEX`. Cursor entry points temporarily set checkpoint HS context when needed.

State and persistence behavior: this file does not mutate table data, but it opens cursors, allocates scratch storage, reads disk images, and may decompress disaggregated base pages for display. Redaction state is controlled by `WT_DEBUG_UNREDACT_ALL` and `WT_DEBUG_UNREDACT_KEYS`; default paths redact application data. It exposes transaction IDs, timestamps, fast-truncate `page_del`, update flags, disaggregated page metadata, and history-store records for diagnostics.

Dependencies and integration points: depends on block manager reads, block cache, disaggregated block/page-log debug APIs, compressor hooks, history-store cursor APIs, B-tree cursor/page macros, time-window formatting, key/value formatting, and event/file output. It is primarily used by `wt` debugging commands, debugger-visible functions, diagnostics, and cursor debug helpers.

Risks: because it introspects live in-memory structures, races are mitigated with page-index guards but still rely on diagnostic usage discipline. Incorrect redaction flags can expose user data. Disaggregated page dumping validates block magic/checksum and rejects encrypted pages without decryption support; incomplete delta decoding is explicitly raw-dumped. History-store dumping changes cursor read flags and must clean up resources on all exits.

Test signals: diagnostic builds should cover row/column/internal/leaf dumps, file and event-handler output, redaction modes, history-store visibility, checkpoint cursor HS dumps, disaggregated page-id debug reads, corrupt checksum/magic handling, compressed-page decompression, and tree-shape recursion under page-index protection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_delete.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_delete.c

Purpose: implements WiredTiger fast-delete/fast-truncate support, allowing page ranges to be deleted by changing `WT_REF` state without first materializing all records. It also handles rollback, visibility-based skipping, recovery cleanup, and later instantiation of deleted pages as per-record tombstone updates.

Important APIs/types/functions: `__wti_delete_page` attempts the fast path; `__wt_delete_page_rollback` reverses unresolved fast truncates; `__wt_delete_redo_window_cleanup` repairs loaded delete metadata after recovery; `__wti_delete_page_skip` decides whether cursor/tree walks can skip a deleted ref; `__wti_delete_page_instantiate` recreates deleted page contents with tombstones. Static helpers allocate tombstone updates and instantiate row or variable-length column-store pages.

Control flow: `__wti_delete_page` first evicts a clean in-memory page if possible, locks a disk ref by CAS to `WT_REF_LOCKED`, rejects pages with unsuitable address type, overflow content, prepared updates, or invisible aggregate timestamps, dirties the parent, optionally allocates `ref->page_del`, records the transaction operation, marks delta-internal dirty state, then sets `WT_REF_DELETED`. Rollback locks the ref, either restores `WT_REF_DISK` and frees `page_del`, or aborts instantiated tombstone updates recorded in `WT_PAGE_MODIFY.inst_updates`. Skip checks lock deleted refs, test transaction visibility with prepared transactions hidden, and frees globally visible `page_del` metadata. Instantiation builds a modify structure and installs tombstone updates into row update arrays or VLCS update lists via cursor modify paths.

State and persistence behavior: the core persistent state is encoded in `WT_REF` state and, when needed, `WT_PAGE_DELETED` metadata containing transaction/timestamp/prepare information. Deleted-address cells can later be unpacked from disk and reconstructed by page-read code. Instantiated pages are intentionally clean after tombstones are restored because their delete information already exists in the data store or parent state. Rollback may set update txn IDs to `WT_TXN_ABORTED` and save rollback timestamps for prepared cases.

Dependencies and integration points: integrates with truncation tree walks, eviction, transaction operation logging, timestamp visibility, history-store rules, reconciliation, rollback-to-stable, recovery, page read/materialization, row/column modify paths, and stats. Comments document special VLCS leftmost-child constraints shared with split, reverse split, verify, and page-load code.

Risks: correctness depends on atomic ref-state transitions and not freeing `page_del` while another thread can inspect it. Visibility checks must distinguish visible-to-session and globally visible deletes, especially for prepared transactions and history-store truncation. Instantiation can create many tombstones and must preserve rollback reachability even after page splits. Rejecting overflow/prepared/invisible pages is necessary to avoid data loss.

Test signals: exercise fast truncate eligibility and slow fallback, rollback before and after instantiation, prepared fast truncates, read of deleted pages by old snapshots, globally visible skip and `page_del` discard, recovery redo-window cleanup, VLCS namespace-gap behavior, history-store truncation paths, and interaction with delta-internal dirty state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_discard.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_discard.c

Purpose: owns teardown of in-memory B-tree pages, refs, update chains, insert lists, modification metadata, and safe freeing of ref address memory. It is the central memory ownership cleanup path used by eviction, close/discard, split error handling, and obsolete update cleanup.

Important APIs/types/functions: exported helpers include `__wt_ref_out`, `__wt_page_out`, `__wti_ref_addr_safe_free`, `__wt_ref_addr_free`, `__wti_free_ref`, `__wti_free_ref_index`, `__wt_free_update_list`, and `__wt_free_obsolete_updates`. Static cleanup helpers free page modify structures, column leaf repeat metadata, internal-page ref indexes, row leaf instantiated keys, skip arrays/lists, and update arrays.

Control flow: `__wt_ref_out` asserts the ref is not the eviction thread target, verifies hazard-pointer absence in diagnostic mode, then delegates to `__wt_page_out`. `__wt_page_out` nulls the caller pointer, handles disaggregated materialization-frontier stats, clears dirty state only for dead handles or connection close, asserts the page is clean/not reconciling/not queued, recursively frees root-split pages, updates page history and cache accounting, releases mapped/shared disk images, optionally leaks memory on process-exit configuration, frees modify metadata and page-type-specific structures, releases disk images, and overwrites the page. Ref cleanup frees optional child pages, instantiated row keys, off-page addresses, fast-truncate metadata, and the ref itself.

State and persistence behavior: this file frees only in-memory state; it must not discard dirty or reconciling pages except during dead-handle/closing cleanup where dirty state is explicitly cleared. Ref address freeing is generation-protected using `WT_GEN_SPLIT` stash so concurrent readers inside a split generation cannot observe freed address cookies. `__wt_free_obsolete_updates` trims update chains after a globally visible update while updating cache footprint.

Dependencies and integration points: tightly coupled to eviction/cache accounting, hazard pointers, split generations, reconciliation result structures (`WT_PM_REC_*`), overflow reuse/discard tracking, shared disk cache, disaggregated metadata, page history diagnostics, and row/column page layout macros.

Risks: cleanup order is critical. Freeing a dirty page, a page queued for eviction, a reconciling page, or a ref address still visible through a page index would corrupt readers. Failed split paths can set `WT_PAGE_UPDATE_IGNORE`, requiring update chains to be retained instead of freed. Shared disk cache accounting must avoid double-decrementing disk image bytes.

Test signals: cover page-out by page type, root split cleanup, multiblock/replace reconciliation cleanup, shared disk cache release, mapped image discard, leak-memory mode, ref address races under split-generation stress, free-ref-index error paths, obsolete update chain trimming, and assertions for dirty/reconciling/hazard-protected pages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_discard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_handle.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_handle.c

Purpose: manages the lifecycle and configuration of a `WT_BTREE` handle: open, close, discard, root initialization, empty-tree creation, page-size validation, encryption/compression configuration, checkpoint/root loading, stable history-store pinning, and tiered object switching.

Important APIs/types/functions: public/internal entry points include `__wt_btree_open`, `__wt_btree_close`, `__wt_btree_discard`, `__wt_btree_config_encryptor`, `__wt_root_ref_init`, `__wti_btree_tree_open`, `__wti_btree_new_leaf_page`, `__wt_btree_release_hs_dhandle`, and `__wt_btree_switch_object`. Static helpers include `__btree_conf`, `__btree_page_sizes`, `__btree_preload`, `__btree_get_last_recno`, `__btree_tree_open_empty`, and stable-HS pin helpers.

Control flow: `__wt_btree_open` clears prior open state, determines read-only/checkpoint/disaggregated names, obtains checkpoint metadata, rejects bulk load on non-new files, configures the B-tree, opens the block cache/block manager, loads the root checkpoint or creates an empty root, preloads second-level pages for non-disaggregated trees, computes column-store last recno, and configures eviction exclusion for special trees. `__btree_conf` parses metadata configuration into B-tree fields: formats, collator, logging, in-memory mode, metadata/history-store/disaggregated flags, page log, page sizes, compression/encryption, write generations, page IDs, and timestamps. Close releases stable HS pins, disables exclusive eviction if needed, unloads checkpoint state, and closes the block manager.

State and persistence behavior: open initializes runtime write generations from checkpoint and connection state, records checkpoint order, sets `btree->modified` for imports, initializes root refs/pages, and pins stable history-store checkpoint handles when reading stable disaggregated checkpoints. Empty trees are represented as an internal root with one deleted leaf ref; bulk-load creates a real dirty leaf. Page-size configuration constrains persistent layout and overflow eligibility.

Dependencies and integration points: integrates with metadata checkpoint APIs, schema/checkpoint locks, block cache/manager, encryption/compression/collator configuration, live restore metadata, eviction, history store, disaggregated page logs, tiered storage, import, salvage/verify, bulk load, and page materialization in `bt_page.c`.

Risks: open error paths must close partially initialized handles to release pinned HS dhandles and block-manager resources. Write-generation choices affect recovery/rollback transaction ID cleanup. Empty-tree deleted refs interact with fast-delete and VLCS search behavior. Disaggregated stable and ingest flags must remain mutually consistent. Page-size validation prevents impossible cache/eviction configurations.

Test signals: cover normal opens, checkpoint opens, stable disaggregated checkpoint opens with HS pin/release, metadata corruption messaging, encrypted/compressed table opens, empty tree creation for row/VLCS and bulk load, readonly/cache-resident/no-evict behavior, import write-generation marking, tiered object switching, and close/discard idempotence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_import.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_import.c

Purpose: reconstructs metadata for importing an existing WiredTiger file into a database. It reads the file's stored metadata and final checkpoint information through the block manager, validates encryption compatibility, rewrites metadata fields that must be local to the destination database, and returns a collapsed metadata config string.

Important APIs/types/functions: the file contains `__wt_import_repair`. It uses `WT_BM` checkpoint methods, `WT_CKPT` lists, scratch `WT_ITEM`s, `WT_KEYED_ENCRYPTOR`, metadata config collapse/update helpers, block modification reset, file ID generation, shared-table detection, and connection stats.

Control flow: the function opens the target URI in `WT_SESSION_IMPORT_REPAIR` mode with a conservative allocation size so the descriptor block can be read, asks the block manager for the last checkpoint metadata and checkpoint list, then closes the block manager. It checks whether stored block metadata encryption matches the current database encryptor, strips quote wrappers, optionally hex-decodes and decrypts the metadata, and builds a config stack with reset incremental-backup metadata, empty `checkpoint_lsn`, and a newly generated file ID. It rejects shared-table imports. It then reopens the block manager using the reconstructed allocation size/config, fetches the final checkpoint again, updates the last checkpoint entry in the checkpoint list with corrected raw checkpoint bytes, collapses the final metadata config, stores it in `*configp`, and increments import-repair stats.

State and persistence behavior: no metadata is written directly here; it returns allocated metadata text for the caller to install. It deliberately resets block modification/incremental backup state, strips checkpoint LSNs because imported files are not associated with local logs, and assigns a destination-unique file ID. Session import-repair state is set only around block-manager repair reads and is cleared on all exits.

Dependencies and integration points: integrates with block manager import/repair support, encryption config from `bt_handle.c`, metadata checkpoint-list serialization, schema lock file ID generation, backup metadata reset, and table-create import flows.

Risks: encryption mismatch detection is essential because encrypted metadata may otherwise be decoded incorrectly. The two-pass block-manager open is subtle: the first pass reads enough metadata with a guessed allocation size, and the second pass rereads checkpoint bytes with corrected configuration. Shared table import is intentionally unsupported to avoid file ID collisions. Error cleanup must not leak returned config on failure.

Test signals: import encrypted and unencrypted files, encryption mismatch failures, files with missing checkpoint information, allocation-size-sensitive checkpoints, metadata quote stripping, reset of backup/checkpoint LSN fields, generated file ID uniqueness, shared-table rejection, and cleanup when either block-manager pass fails.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_import.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_misc.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_misc.c

Purpose: small B-tree utility formatting helpers used by diagnostics, verbose output, and debugger-visible code. It converts addresses, cell types, keys, and page types into stable printable strings.

Important APIs/types/functions: `__wt_addr_string` formats a block-manager address or returns sentinel strings for no-address/error cases. `__wti_cell_type_string` maps `WT_CELL_*` raw types to readable names. `__wt_key_string` formats keys according to a WiredTiger key format, with diagnostic raw-dump support. `__wt_page_type_string` maps `WT_PAGE_*` constants and is exported with default visibility.

Control flow: address formatting obtains `S2BT_SAFE(session)`, delegates to `btree->bm->addr_string` when possible, and falls back to `WT_NO_ADDR_STRING` or `WT_ERR_STRING`. Key formatting special-cases string format `S` by building a null-terminated temporary if needed, then calls printable-format helpers; diagnostic `session->dump_raw` bypasses format rendering. Cell/page type helpers are direct switches with `"unknown"` fallback.

State and persistence behavior: no persistent state is changed. The functions write into caller-provided `WT_ITEM` buffers or return string literals. `__wt_key_string` may allocate a temporary `WT_ITEM` internally and frees it before returning; callers must provide a persistent output buffer for the returned string data.

Dependencies and integration points: used heavily by `bt_debug.c`, verification/dump code, logging, error messages, and any code that needs to display B-tree page/cell/address identity. It depends on block-manager address formatting, struct-format printable conversion, scratch buffer management, and diagnostic raw-dump session state.

Risks: callers must pass valid buffers; `__wt_addr_string` asserts this. `__wt_key_string` assumes nonzero size when checking the final byte for `S` string keys, so callers should not pass malformed zero-length string keys. Type string switches must stay updated when new page or cell types are introduced to avoid vague diagnostics.

Test signals: formatting null/empty addresses, missing block manager fallbacks, valid block-manager address strings, all known cell/page types, unknown type fallback, string keys with and without trailing NUL, raw dump mode, and formatted binary/structured keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_npos.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_npos.c

Purpose: computes and consumes approximate normalized page positions in a B-tree. Normalized positions are doubles in `[0, 1]` used mainly by eviction to resume tree walks without holding hazard pointers too long, and by read paths to seek near a fractional point in a dataset.

Important APIs/types/functions: `__wt_page_npos` computes a page's normalized position and optional path string. `__wt_page_from_npos` finds a page near a normalized position. Convenience wrappers `__wt_page_from_npos_for_eviction` and `__wt_page_from_npos_for_read` add the right read/walk flags. Static helpers `__page_from_npos_internal` and `__find_closest_leaf` implement descent and leaf cleanup.

Control flow: position calculation starts with a caller-provided intra-page `start` value, enters the page-index generation, ascends through parent refs, and folds each `(slot + npos) / entries` into a root-relative position, clamping the result. Lookup starts at the root under page-index protection, repeatedly multiplies the local fraction by child count to choose a child index, then either descends with `__wt_page_swap` or stops early depending on ref state and flags. Eviction mode never reads disk pages; read mode may wait/restart on locked refs unless `WT_READ_NO_WAIT` is set. After the internal descent, `__find_closest_leaf` tree-walks to a suitable leaf if the initial result is internal, deleted, or otherwise unsuitable.

State and persistence behavior: no disk state is changed. Runtime effects are hazard/page references acquired and released during page swaps and walks, stats increments distinguishing eviction/read max-walk cases, and optional diagnostic path-string output. Returned positions are approximate and can shift after splits.

Dependencies and integration points: integrates with eviction walk state, tree walk flags, hazard pointer/page-swap machinery, page-index generations, ref parent/index lookup, and stats. It relies on balanced-tree assumptions only for quality, not for safety.

Risks: precision is approximate, especially in unbalanced in-memory trees or after splits; callers must tolerate skipped or repeated pages. Eviction-specific behavior may return `NULL` when the root would otherwise be returned, signaling restart/end. Incorrect flag combinations could load pages during eviction or wait in contexts that need no-wait behavior. Path string writing depends on caller-provided buffer length.

Test signals: round-trip a page through `__wt_page_npos(..., 0.5)` and `__wt_page_from_npos`, boundary values below 0 and above 1, forward/backward adjacent-page iteration via out-of-range starts, eviction mode with disk/locked/deleted refs, read mode restart on splits, path string formatting, and stats for read versus eviction walks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_npos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_ovfl.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_ovfl.c

Purpose: handles overflow item reads and removal/discard coordination. Overflow keys/values are stored as separate disk pages when too large for normal leaf cells; this file reads them safely and marks/free backs overflow blocks after reconciliation.

Important APIs/types/functions: static `__ovfl_read` performs the physical block-cache read and exposes the overflow payload. `__wt_ovfl_read` is the public read helper with removed-cell protection. `__wt_ovfl_remove` queues an overflow value for later discard. `__wt_ovfl_discard` flips on-page cell type to removed and frees backing blocks.

Control flow: reads go through `__wt_blkcache_read`, interpret the returned `WT_PAGE_HEADER`, and point the caller's `WT_ITEM` at `WT_PAGE_HEADER_BYTE`. If a page is supplied, `__wt_ovfl_read` takes the B-tree overflow read lock and returns a sentinel string rather than reading when the cell has already been reset to `WT_CELL_VALUE_OVFL_RM`. Removal during reconciliation is queued via `__wt_ovfl_discard_add`; after successful reconciliation, `__wt_ovfl_discard` unpacks the cell, takes the overflow write lock, atomically resets key/value overflow cell types to removed variants, releases the lock, and frees the blocks with `__wt_btree_block_free`.

State and persistence behavior: overflow removal mutates the in-memory disk image cell type so concurrent readers can detect removed overflow blocks. The backing disk blocks are freed only after reconciliation has safely copied required values to the history store when needed. Read statistics count overflow cache reads.

Dependencies and integration points: depends on block cache reads, B-tree overflow lock initialized in `bt_handle.c`, cell unpack/reset helpers, reconciliation's overflow discard queues, history-store preservation of old overflow values, and block-free APIs.

Risks: the main race is a reader reading an on-page overflow address while checkpoint/reconciliation frees and reuses the backing blocks. The per-B-tree overflow lock and cell-type transition are the protection. Returning `"WT_CELL_VALUE_OVFL_RM"` is a defensive path for a value that should not be read. Only key/value overflow raw types are legal in discard; anything else indicates corruption or caller error.

Test signals: synchronous overflow reads, read after value cell marked removed, reconciliation queue plus discard, key and value overflow type reset, block-free invocation, race tests with concurrent readers/checkpoint, and illegal cell type handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_ovfl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_page.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_page.c

Purpose: constructs `WT_PAGE` objects from disk images, allocates new pages, restores prepared updates, and merges disaggregated/page-delta images into full disk images. It is the main bridge between persistent B-tree page format and in-cache page structures.

Important APIs/types/functions: exported helpers include `__wti_page_merge_deltas_with_base_image_leaf`, `__wti_page_merge_deltas_with_base_image_int`, `__wt_page_block_meta_assign`, `__wt_page_alloc`, `__wti_page_inmem_updates`, and `__wti_page_inmem`. Static helpers unpack base/delta merge streams, clear obsolete time-window fields, allocate/free merge state, count row-leaf entries, and initialize column/row internal/leaf in-memory indexes.

Control flow: delta merge functions progressively unpack sorted base and delta streams, choose the smallest key with newer deltas winning duplicates, skip deleted delta entries, pack cells into a new image, aggregate time metadata in diagnostic builds, and finalize page headers. `__wt_page_alloc` sizes and allocates `WT_PAGE`, optional disaggregated info, internal page indexes and refs, then updates cache/page counters. `__wti_page_inmem` determines allocation counts from disk page type/flags, allocates the page, attaches the disk image, updates image accounting, calls page-type-specific builders, links parent refs, and handles shared disk cache metadata. Prepared updates are restored by scanning leaf cells with prepare time windows and inserting update/tombstone chains via row/column modify paths.

State and persistence behavior: page allocation and materialization update cache memory footprint, page counts, leaf/stable/ingest counters, disk image accounting, and per-page disaggregated block metadata. Internal page loading reconstructs child refs, deleted-address cells, fast-truncate `page_del`, overflow key flags, and VLCS left-gap deleted refs. Leaf loading builds row key/value indexes, VLCS repeat arrays, prefix-compression acceleration metadata, and flags whether prepare updates need instantiation.

Dependencies and integration points: integrates with cell packing/unpacking, collators, transaction timestamp visibility, cache accounting, row/column search and modify, fast-delete state from `bt_delete.c`, disaggregated shared disk cache/page IDs, block metadata, reconciliation delta writing, overflow handling, and B-tree configuration from `bt_handle.c`.

Risks: merge logic must preserve sorted order and latest-delta-wins semantics while consuming base duplicates exactly once. Materialization must balance cache accounting on both success and error, especially for shared disk pages. Prepared update restoration must not mark durable state incorrectly or rollback may fail to rewrite prepared cells. Internal deleted refs must be reconstructed with correct `page_del` metadata and dirty-parent behavior. Prefix-compressed row keys and VLCS RLE counts are easy places for off-by-one bugs.

Test signals: delta merge with duplicate keys/deletes/multiple streams, time-window obsolete clearing, internal and leaf page materialization for all page types, VLCS left-gap deleted ref creation, deleted-address fast-truncate reconstruction, row prefix-compression groups, prepared start/stop update restoration, shared disk image accounting, disaggregated page ID assignment, and error-path page-out accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_prefetch.c -->
# sources/storage-engines/wiredtiger/src/btree/bt_prefetch.c

Purpose: implements B-tree prefetch queuing and worker-side page-in for pages likely to be read soon. It attempts to warm the block cache/cache with nearby leaf pages while avoiding repeated prefetch from the same parent and avoiding disk reads in unsuitable states.

Important APIs/types/functions: `__wti_btree_prefetch` scans sibling refs under a parent and queues disk leaf pages. `__wt_prefetch_page_in` runs from a prefetch queue entry and performs the actual page read/release side effect. It uses session prefetch state (`session->pf`), `WT_PREFETCH_QUEUE_ENTRY`, connection prefetch queue counters, ref flags, and split-generation protection.

Control flow: prefetch first verifies it can safely traverse the parent page: leaf refs are allowed, otherwise the session must already be in a split generation. It suppresses repeated prefetches from the same parent until enough skips have occurred. It then scans `ref->home` children and, while queue capacity and per-trigger limits allow, queues refs that are disk-resident leaf pages, not fast-deleted, and not already flagged for prefetch. The worker validates the dhandle/ref, skips refs no longer on disk, enters the split generation, copies the ref address, calls `__wt_page_in` with `WT_READ_PREFETCH | WT_READ_SKIP_DELETED`, releases the page, and leaves the generation.

State and persistence behavior: no persistent data changes. Runtime state includes setting/observing prefetch flags through the queue, session bookkeeping for previous parent and skip count, queue depth, page reads into cache, immediate hazard release, and prefetch success/failure/skip statistics.

Dependencies and integration points: integrates with cursor/read path prefetch triggers, connection prefetch queue, page-in/page-release, split-generation safety, ref state flags, fast-delete visibility skipping, dhandle lifetime management, and stats/verbose logging.

Risks: scanning an internal page without split-generation protection can race with splits. Queueing the same parent repeatedly can waste work; the skip counter throttles this. Queued refs may move to another parent or leave disk state before the worker runs, so the worker revalidates. Fast-deleted pages are skipped to avoid warming data readers can ignore.

Test signals: queue capacity and per-trigger limits, same-parent throttling, split-generation skip for unsafe internal traversal, worker handling of changed home refs, no-valid-dhandle/internal-page assertions, refs no longer on disk, deleted-page skipping, page read/release side effects, and stats for queued/read/fail/skipped pages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/bt_prefetch.c -->
