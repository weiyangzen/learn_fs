<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_cmp_inline.h -->
# sources/storage-engines/wiredtiger/src/include/btree_cmp_inline.h

## Purpose
Defines hot-path comparison helpers for WiredTiger B-tree searches, cursor bounds checks, and row-key comparisons. It provides bytewise lexicographic comparison, prefix-skipping comparison, optional application collator dispatch, and a short-key fast path.

## Important APIs, Types, and Functions
`__wt_lex_compare` compares two `WT_ITEM` byte strings and returns the usual negative/zero/positive ordering. It uses x86 SSE or ARM NEON 16-byte chunks when available, then finishes with scalar byte comparison and length tie-breaking.

`__wt_compare` wraps `__wt_lex_compare` unless a `WT_COLLATOR` is configured, in which case it calls `collator->compare`.

`__wt_compare_bounds` checks a cursor key or column-store record number against upper or lower cursor bounds. Row-store bounds use `__wt_compare`; column-store bounds unpack a record number with `__wt_struct_unpack`.

`__wt_lex_compare_skip` compares after an already-known common prefix tracked by `matchp`, updating `matchp` as additional equal bytes are observed. Diagnostic builds can recompute the full comparison under `WT_TIMING_STRESS_PREFIX_COMPARE`.

`__wt_compare_skip` combines the skip optimization with optional collator dispatch. Collated comparisons cannot use the prefix-skip optimization and delegate the full comparison.

`__wt_lex_compare_short` is an unrolled switch for keys up to `WT_COMPARE_SHORT_MAXLEN` (9 bytes), matching packed record-number key sizes.

## Control Flow
Large comparisons first align to vector-sized chunks: x86 uses aligned or unaligned loads depending on both pointer addresses; ARM NEON scans 16-byte vectors. Both variants stop at the first unequal vector and let scalar code identify the exact byte difference. Small comparisons skip vectorization and go straight to the scalar loop.

Bounds checks split on `upper`. For row-store, the comparison result is interpreted according to inclusive or exclusive cursor-bound flags. For column-store, the packed bound buffer is decoded into a `uint64_t recno` before the same inclusive/exclusive logic is applied.

## State and Persistence Behavior
This file does not own persistent state. It reads cursor bound buffers and B-tree collator configuration, increments `cursor_bounds_comparisons`, and updates the caller-owned `matchp` and `key_out_of_bounds` outputs. The correctness of `matchp` depends on callers only passing a prefix length known to match both keys.

## Dependencies and Integration Points
The helpers depend on `WT_ITEM`, `WT_SESSION_IMPL`, `WT_CURSOR`, `WT_COLLATOR`, `CUR2BT`, cursor bound flags, stat macros, vector intrinsics, and WiredTiger var-struct unpacking. They integrate with B-tree search/descent, cursor next/prev bound enforcement, row-store prefix-compressed key handling, and any table using a custom collator.

## Risks and Edge Cases
The vector paths must not read past `min(user_size, tree_size)`, so the code strips a remainder before vector scanning and restores it for scalar finish. `__wt_lex_compare_skip` computes `WT_MIN(usz, tsz) - *matchp`; callers must ensure `matchp` is no larger than the shorter key. Collator paths ignore `matchp`, so prefix optimization cannot be assumed for user-defined ordering. Column bounds rely on the raw bound buffer containing a valid packed `q` record number.

## Test Signals
Relevant test signals include row-store and column-store cursor-bound tests, custom-collator ordering tests, prefix-compressed row search tests, and architecture builds that exercise x86 intrinsics, ARM NEON, and scalar fallback. Diagnostic timing stress for prefix comparison is a direct consistency check between skip and full comparison paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_cmp_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_inline.h -->
# sources/storage-engines/wiredtiger/src/include/btree_inline.h

## Purpose
Collects performance-critical inline B-tree helpers for page state, dirty tracking, cache accounting, row-key access, address copying, eviction eligibility, hazard-pointer release, skiplist depth selection, page-index navigation, and disaggregated-storage accounting. This header sits in the core execution path for reads, writes, checkpoint, reconciliation, eviction, and cursor traversal.

## Important APIs, Types, and Functions
Bulk and page-state helpers include `__wt_btree_disable_bulk`, `__wt_page_is_empty`, `__wt_page_evict_clean`, `__wt_page_is_modified`, `__wt_page_is_reconciling`, `__wt_page_dirty_and_evict_soon`, and `__wt_btree_block_free`.

Cache accounting helpers include `__wt_btree_bytes_inuse`, `__wt_btree_bytes_evictable`, dirty/update byte accessors, `__wt_cache_page_inmem_incr`, `__wt_cache_page_inmem_decr`, `__wt_cache_dirty_incr_size`, `__wt_cache_dirty_decr_size`, `__wt_cache_dirty_decr`, image accounting, and shared disk image accounting. The decrement helpers `__wt_cache_decr_check_size` and `__wt_cache_decr_check_uint64` clamp underflow to zero, log the accounting bug, and abort in diagnostic builds.

Dirty-state APIs include `__wt_page_modify_init`, `__wt_page_only_modify_set`, `__wt_tree_modify_set`, `__wt_page_modify_clear`, `__wt_page_modify_set`, and `__wt_page_parent_modify_set`. They coordinate page dirty state, tree/connection modified flags, cache dirty counters, first dirty transaction tracking, and checkpoint ordering.

Row-store and reference key APIs include `__wt_ref_key`, `__wt_ref_key_onpage_set`, `__wt_ref_key_instantiated`, `__wt_ref_key_clear`, `__wt_row_leaf_key_info`, `__wt_row_leaf_key_set`, `__wt_row_leaf_value_set`, `__wt_row_leaf_key_free`, `__wt_row_leaf_key`, `__wt_row_leaf_key_instantiate`, `__wt_row_leaf_value_is_encoded`, `__wt_row_leaf_value`, and `__wt_row_leaf_value_cell`. These use pointer bit encodings to avoid unpacking common on-page keys and simple values.

Address, deletion, and eviction helpers include `__wt_ref_addr_copy`, `__wt_get_page_modify_ta`, `__wt_ref_block_free`, `__wt_page_del_visible_all`, `__wt_page_del_visible`, `__wt_page_del_committed_set`, `__wt_leaf_page_can_split`, `__wt_page_evict_retry`, `__wt_materialization_check`, `__wt_btree_can_discard`, `__wt_btree_disagg_checkpointed`, `__wt_page_can_evict`, and `__wt_page_release`.

Traversal helpers include `__wt_skip_choose_depth`, `__wt_split_descent_race`, `__wt_page_swap_func`, `__wt_btcur_bounds_early_exit`, `__wt_btcur_skip_page`, `__wt_ref_index_slot`, and `__wt_ref_ascend`.

## Control Flow
Modification starts by allocating `page->modify`, marks the tree dirty, atomically transitions the page from clean to dirty, updates cache counters only for the first dirty transition, records first dirty transaction state, and marks the tree dirty again to cover checkpoint races. The metadata and history-store special case can pre-increment dirty counters for low dirty-leaf counts to avoid temporary negative cache accounting under low isolation.

Memory accounting increments and decrements per-connection cache totals, per-btree totals, page footprint, internal-page totals, dirty bytes, update bytes, image bytes, and disaggregated ingest/stable sub-counters. Decrement paths use guarded subtraction and tolerate races by limiting dirty/update byte decrements to the observed page-local amount.

Row-key access first decodes the pointer tag. Internal keys use a one-bit tag distinguishing allocated `WT_IKEY` from encoded on-page offset/length. Leaf keys use two low bits to distinguish direct cell offsets, encoded key metadata, encoded key/value metadata, and instantiated keys. `__wt_row_leaf_key` returns direct on-page data when possible, builds keys from a page-level prefix group when possible, and falls back to `__wt_row_leaf_key_work` for overflow or complex prefix-compressed cells.

Eviction eligibility is a sequence of blockers and fast exits: prefetched refs, read-only trees, disaggregated materialization frontier, uncommitted fast truncation, checkpoint-related overflow-key constraints, possible in-memory split, clean disaggregated pages ahead of materialization, dirty pages during another session's checkpoint, dirty internal disaggregated pages, current disaggregated checkpoint generation, active split generations for internal pages, and metadata pages with recently modified data. `__wt_page_release` uses that result either to queue urgent eviction, attempt release-and-evict, or clear the hazard pointer.

Tree traversal helpers detect non-atomic internal split races by comparing saved parent page indexes, ensure page-in/page-release coupling does not leak hazard pointers, and search parent indexes from ref hints with backoff until split updates stabilize.

## State and Persistence Behavior
The header mutates in-memory `WT_BTREE`, `WT_PAGE`, `WT_PAGE_MODIFY`, `WT_REF`, `WT_CACHE`, and connection flags/counters. It affects persistence indirectly by controlling when pages and trees are marked dirty, when disk blocks are freed, which address cookies are copied, and whether checkpoint/eviction can reconcile or discard content. Disaggregated storage adds materialization-frontier state, checkpoint generation state, stable/ingest cache buckets, and shared disk-image byte tracking.

## Dependencies and Integration Points
This file depends on atomic primitives, hazard pointers, generation tracking, transaction visibility, timestamps, reconciliation state, cache structures, eviction functions, block manager callbacks, salvage tracking, cursor bounds comparison, row/column page macros, overflow handling through cell unpacking, and disaggregated/layered table manager state. It is integrated with update insertion, checkpoint, eviction server/app eviction, B-tree search, cursor next/prev, truncate, page split, reconciliation, block free, and cache pressure calculations.

## Risks and Edge Cases
The dirty-state ordering is delicate: page content must become visible before page/tree dirty markers, and tree dirty markers must not race checkpoint into losing dirty pages. Cache accounting races are expected; underflow guards prevent wraparound but can leave cache usage conservative. Pointer-tag encodings assume allocated memory alignment and page-size bit budgets; unusual page sizes or misaligned allocations would break fast-path decoding. `__wt_ref_addr_copy` requires a split generation and uses ordered reads to avoid pairing a new home page with an old on-page address. Eviction blockers are correctness-sensitive for checkpoint, disaggregated materialization, uncommitted truncation, overflow-key history, and internal split generations.

## Test Signals
Strong signals include eviction and checkpoint stress tests, dirty/clean page accounting tests, metadata/history-store update tests, disaggregated storage materialization and checkpoint tests, in-memory split tests, row-store prefix compression and overflow-key tests, hazard-pointer traversal tests, truncate visibility tests, cache accounting diagnostics, and stress flags for release eviction, checkpoint eviction races, and skiplist depth.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/buf_inline.h -->
# sources/storage-engines/wiredtiger/src/include/buf_inline.h

## Purpose
Provides inline buffer management helpers for `WT_ITEM` objects and session scratch buffers. The functions normalize allocation, growth, content assignment, initialization, and release while preserving WiredTiger's convention that `WT_ITEM.data` can point either inside owned memory or at external data before a grow operation copies it locally.

## Important APIs, Types, and Functions
`__wt_buf_grow` ensures the buffer owns enough memory and accounts for `data` pointing at an offset inside `mem`. It delegates allocation/copying to `__wt_buf_grow_worker`.

`__wt_buf_extend` grows exponentially for repeated appends or extension-style workloads.

`__wt_buf_init` creates an empty buffer of at least a requested size without copying external data. `__wt_buf_initsize` also sets the logical data size.

`__wt_buf_set`, `__wt_buf_set_and_grow`, and `__wt_buf_setstr` set the logical contents before forcing ownership and capacity.

`__wt_buf_free` frees owned memory and clears the item. `__wt_scr_free` returns scratch buffers to the session cache or frees oversized scratch memory when the session scratch budget would be exceeded.

## Control Flow
The grow helpers set up `WT_ITEM` metadata so the worker can determine whether to allocate, reallocate, or copy referenced data. `__wt_buf_extend` doubles the current memory size when possible. Scratch free clears `*bufp`, then either releases the backing memory or accumulates its memory size in `session->scratch_cached`, clears active data fields, and removes `WT_ITEM_INUSE`.

## State and Persistence Behavior
All state is transient process memory. The file mutates `WT_ITEM.mem`, `memsize`, `data`, `size`, flags, and `session->scratch_cached`. No filesystem state is persisted, but these helpers are used when constructing disk images, keys, values, config strings, and temporary decode buffers elsewhere.

## Dependencies and Integration Points
Depends on `WT_ITEM`, `WT_SESSION_IMPL`, `WT_DATA_IN_ITEM`, `WT_PTRDIFF`, `WT_MAX`, `__wt_buf_grow_worker`, `__wt_free`, and session scratch-cache limits. It integrates broadly with cell packing/unpacking, row-key construction, schema/config handling, reconciliation image building, and cursor key/value buffers.

## Risks and Edge Cases
Callers must understand whether `WT_ITEM.data` references external memory or owned memory. `__wt_buf_grow` includes offset data in its capacity test, preventing callers from underallocating when appending to a slice inside the buffer. `__wt_buf_setstr` includes the trailing NUL in `size`, which is intended for string buffers but not arbitrary binary values. Scratch caching relies on `WT_ITEM_INUSE` discipline; freeing a buffer still in use would create aliasing bugs.

## Test Signals
Indirect coverage comes from tests that grow cursor buffers, decode prefix-compressed keys, build reconciliation images, process configuration strings, and exercise session scratch reuse under memory pressure. Memory sanitizer or diagnostic runs should catch use-after-free and stale scratch-buffer reuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/buf_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache.h -->
# sources/storage-engines/wiredtiger/src/include/cache.h

## Purpose
Defines WiredTiger's core cache data structures, cache-operation enum, cache eviction controls, disaggregated shared disk image cache, and cache pool metadata. It is the shared state model consumed by inline accounting helpers, eviction, reconciliation, cache pool management, history-store logic, and disaggregated storage code.

## Important APIs, Types, and Functions
`WT_CACHE_OP` enumerates sync/cache operation modes: checkpoint, close, discard, and write-leaves.

`WT_CACHE_EVICTION_CONTROLS` stores application eviction tuning, including tolerance, minimum fill ratio, and atomic flags `WT_CACHE_EVICT_INCREMENTAL_APP`, `WT_CACHE_PREFER_SCRUB_EVICTION`, and `WT_CACHE_SKIP_UPDATE_OBSOLETE_CHECK`.

`WT_SHARED_DSK_ITEM` represents one shared disk image entry with hash linkage, data pointer/size, reference count, block metadata, file ID, and variable-length address cookie.

`WT_SHARED_DSK_CACHE_DEFAULT_HASH_SIZE` computes a best-effort bucket count from cache size. `WT_DSK_CACHE_STATE` and macros `WT_DSK_CACHE_CAN_READ`/`WT_DSK_CACHE_CAN_WRITE` gate disaggregated shared disk cache access.

`WT_SHARED_DSK_CACHE` stores the state byte, read-only transition time, hash table, lock array, sizing, and diagnostic maxima.

`WT_CACHE` is the central per-connection cache accounting structure. It tracks bytes and pages for dirty internal/leaf content, images, in-memory data, internal pages, reads/writes, updates, history-store usage, ingest/stable disaggregated buckets, cache pool state, and shared disk cache state.

`WT_CACHE_POOL` represents a shared cache across connections with lock/condition variable, size/chunk/quota/current usage, references, connection queue, manager flag, and active flag.

## Control Flow
This header is declarative. Runtime control flow lives in users of these fields: cache accounting increments/decrements counters, eviction reads thresholds and flags, shared disk cache operations check state before hash-table access, and cache pool management updates quotas and connection queues under `cache_pool_lock`.

## State and Persistence Behavior
All fields are in-memory state for a WiredTiger process. They influence persistence indirectly by controlling eviction, checkpoint write pressure, history-store cache pressure, and disaggregated shared disk image reuse. Shared disk cache entries hold disk-image bytes and block metadata in memory only; reference counts decide hash-table lifetime.

## Dependencies and Integration Points
The structures depend on WiredTiger queue macros, spin locks, condition variables, thread IDs, page block metadata, B-tree flags, file IDs, and connection cache size. Integration points include eviction server/app eviction, cache pool manager, history store, reconciliation, block/image accounting, disaggregated standby/leader step-up behavior, and per-btree cache accounting from `btree_inline.h`.

## Risks and Edge Cases
Most counters are approximate under concurrency but must not become nonsensical. Disaggregated cache state transitions are sensitive: active standby permits reads and writes, stepped-up leader is read-only, drained leader is dead. Shared disk cache reference counts require lock protection; misuse can leak image entries or free still-shared data. Ingest/stable counter buckets must stay aligned with B-tree flags or cache pressure calculations become misleading.

## Test Signals
Useful signals include cache eviction threshold tests, cache pool quota tests, history-store pressure tests, disaggregated shared disk cache read/write/step-up tests, diagnostic reference-count checks, and workload tests that compare cache statistics against expected page/image/update movements.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache_inline.h -->
# sources/storage-engines/wiredtiger/src/include/cache_inline.h

## Purpose
Defines read-side inline helpers for cache usage metrics and session wait eligibility. These functions provide consistent cache-overhead adjustment and aggregate counters for total, ingest, stable, dirty, update, image, and "other" cache usage.

## Important APIs, Types, and Functions
Page-count accessors include `__wt_cache_pages_inuse`, `__wt_cache_pages_inuse_leaf`, `__wt_cache_pages_inuse_ingest`, and `__wt_cache_pages_inuse_stable`.

Byte accessors include `__wt_cache_bytes_plus_overhead`, `__wt_cache_bytes_inuse`, `__wt_cache_bytes_inuse_ingest`, `__wt_cache_bytes_inuse_stable`, `__wt_cache_dirty_inuse`, dirty internal/leaf variants, update byte variants, image byte variants, and `__wt_cache_bytes_other`.

`__wt_session_can_wait` checks whether a session may perform slow operations and excludes sessions ignoring cache size or holding the schema lock.

`__wt_cache_full` compares overhead-adjusted cache bytes in use with the connection cache size.

## Control Flow
Most functions perform relaxed atomic loads from `WT_CACHE`, combine related counters, apply `overhead_pct`, and return the derived value. `__wt_cache_bytes_other` protects against racing counter reads by using `__wt_safe_sub` when subtracting image bytes from total in-memory bytes. `__wt_session_can_wait` is a short flag-gated predicate. `__wt_cache_full` fetches the connection cache and compares in-use bytes to `conn->cache_size`.

## State and Persistence Behavior
The helpers do not mutate state. They read in-memory cache counters and session flags. Their results influence eviction, throttling, block-manager flush decisions, and application backpressure, which indirectly affects when data is reconciled and persisted.

## Dependencies and Integration Points
Depends on `WT_CACHE`, `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, atomic load wrappers, `F_ISSET`, lock flag fields, `__wt_safe_sub`, and connection cache size. Integrated with eviction decisions, statistics, cache pressure calculations, block manager behavior, and disaggregated ingest/stable cache accounting.

## Risks and Edge Cases
Relaxed counter reads can observe temporarily inconsistent combinations; callers must treat results as approximate. `overhead_pct` applies uniformly to derived byte categories, so changing that field affects every cache pressure calculation. `__wt_cache_bytes_other` explicitly handles underflow from racing reads; similar external calculations should not subtract raw counters without protection.

## Test Signals
Signals include cache-stat tests for bytes/pages in use, cache overhead configuration tests, eviction-trigger tests around full-cache thresholds, schema-lock/session flag tests for wait eligibility, and concurrent stress tests that ensure derived counters do not underflow or wrap.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/capacity.h -->
# sources/storage-engines/wiredtiger/src/include/capacity.h

## Purpose
Defines capacity-throttling types, constants, subsystem percentages, and reservation state for limiting WiredTiger read/write throughput. It centralizes the shared budget model for checkpoint, eviction, log, read, and total capacity scheduling.

## Important APIs, Types, and Functions
`WT_THROTTLE_TYPE` classifies throttled operations as checkpoint, eviction, logging, or read.

Constants define minimum configured capacity (`WT_THROTTLE_MIN`), background fsync thresholds (`WT_CAPACITY_FILE_THRESHOLD`, `WT_CAPACITY_MIN_THRESHOLD`, `WT_CAPACITY_PCT`), small-sleep cutoff (`WT_CAPACITY_SLEEP_CUTOFF_US`), and subsystem percentage allocation (`WT_CAP_CKPT`, `WT_CAP_EVICT`, `WT_CAP_LOG`, `WT_CAP_READ`) via `WT_CAPACITY_SYS`.

`WT_THROTTLE` stores per-subsystem bytes-per-second budgets, total capacity, threshold period, bytes written in the current period, signal state, and atomic next-reservation timestamps for each subsystem plus the total stream.

## Control Flow
This header is declarative. Runtime throttling code will compute subsystem budgets from total capacity, reserve future nanosecond slots in the relevant subsystem and total reservation fields, and sleep when the reservation lies in the future. Very short sleeps below the cutoff can be ignored to reduce overhead at the cost of temporary burstiness.

## State and Persistence Behavior
Capacity state is in-memory and shared across threads. It does not persist data itself, but it regulates the rate at which checkpoint, eviction, log, and read I/O reach the filesystem or storage service. `written` and reservation fields are volatile/shared counters for the active period.

## Dependencies and Integration Points
Depends on common size constants, atomic/shared-field conventions, and the capacity server/throttling implementation elsewhere. Integration points are checkpoint writes, eviction writes, logging, reads, background fsync signaling, and any stats or configuration code that exposes capacity limits.

## Risks and Edge Cases
Subsystem percentages intentionally sum over 100 because not all subsystems peak simultaneously; total capacity must still be enforced separately. Ignoring sleeps shorter than `WT_CAPACITY_SLEEP_CUTOFF_US` can create bursty I/O. Reservation timestamps must be updated atomically to avoid overbooking under concurrency. Thresholds that are too small can cause excessive wakeups or poor smoothing.

## Test Signals
Relevant tests should configure capacity limits and verify throttled checkpoint/log/read/eviction throughput, total-budget enforcement when subsystems overlap, no-throttle behavior below minimum/disabled settings, small-sleep cutoff behavior, and background fsync signaling thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/capacity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell.h -->
# sources/storage-engines/wiredtiger/src/include/cell.h

## Purpose
Defines WiredTiger's variable-length on-page cell format and unpacked cell structures. Cells encode row/column keys, values, overflow references, deleted placeholders, internal-page addresses, timestamp/transaction visibility windows, fast-truncate metadata, dictionary copies, and delta-page merge state.

## Important APIs, Types, and Functions
Descriptor-bit macros define short key/value encodings, associated 64-bit value presence, secondary descriptor presence, time-window flags, raw cell types, cell type masking, and size adjustment for non-short cells.

`WT_CELL` is the packed on-page header buffer, sized pessimistically for all optional metadata.

`WT_CELL_COMMON_FIELDS` defines the common unpack fields: original cell pointer, RLE/recno `v`, data pointer and size, cell length, prefix byte, raw/type fields, and flags.

`WT_CELL_UNPACK_ADDR` adds a `WT_TIME_AGGREGATE` and `WT_PAGE_DELETED` for internal address cells and fast truncation. `WT_CELL_UNPACK_KV` adds a `WT_TIME_WINDOW` for key/value cells.

Delta structures include `WT_CELL_UNPACK_DELTA_INT`, `WT_CELL_UNPACK_DELTA_LEAF_KV`, `WT_CELL_KV`, `WTI_DELTA_INT_MERGE_STATE`, and `WTI_BASE_INT_MERGE_STATE`.

## Control Flow
The packed format starts with a descriptor byte. Short cells store type and length entirely in that byte. Non-short cells may include a prefix byte, a second descriptor byte with timestamp/transaction flags, an associated packed 64-bit value such as RLE or recno, fast-delete fields, a packed data length, and then data bytes or an address cookie. Unpack structures normalize those variants so higher-level code can operate on typed fields.

## State and Persistence Behavior
Unlike most inline headers, this file defines a persistent on-disk format. The descriptor values, field order, delta encoding assumptions, and size adjustment are compatibility-sensitive. `WT_CELL_ADDR_DEL` and `WT_CELL_ADDR_DEL_VISIBLE_ALL` preserve fast-truncate state, while time windows and aggregates preserve MVCC visibility across restart.

## Dependencies and Integration Points
The format depends on WiredTiger timestamp, transaction, page delete, page header, item, and block metadata types. It integrates with reconciliation, page read, overflow management, row/column accessors, truncate, history store visibility, disaggregated delta leaf/internal pages, and verification.

## Risks and Edge Cases
Changing descriptor bits or field ordering is an on-disk compatibility change. `WT_CELL_VALUE_COPY` means an unpacked value may refer to an earlier cell while keeping the current cell's visibility/RLE metadata. Prepared transaction metadata reuses timestamp flag slots in specialized ways when preserving prepared IDs. Fast-truncate address cells carry page-delete metadata only when the page image advertises `WT_PAGE_FT_UPDATE`.

## Test Signals
Coverage should include page image format compatibility, verify on malformed cells, timestamped and non-timestamped visibility windows, prepared updates with and without preserve-prepared, overflow cells, dictionary values, fast truncate, row prefix compression, column RLE, and delta page merge tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell_inline.h -->
# sources/storage-engines/wiredtiger/src/include/cell_inline.h

## Purpose
Implements inline packing, unpacking, validation, cleanup, data-reference, and iteration helpers for the cell format defined in `cell.h`. It is the main bridge between in-memory MVCC/page structures and bytes stored in WiredTiger page images.

## Important APIs, Types, and Functions
Validation and packing helpers include `__cell_check_value_validity`, `__cell_assert_tw_has_ts_for_garbage_collection_table`, `__cell_pack_value_validity`, `__wt_check_addr_validity`, `__cell_pack_addr_validity`, `__wt_cell_pack_addr`, `__wt_cell_pack_value`, `__wt_cell_pack_copy`, `__wt_cell_pack_del`, `__wt_cell_pack_int_key`, `__wt_cell_pack_leaf_key`, and `__wt_cell_pack_ovfl`.

Prefix and image-building helpers include `__wt_cell_compress_prefix_key`, `__wt_cell_decompress_prefix_key`, `__wt_cell_pack_leaf_kv`, `__wt_cell_build_addr_kv`, `__cell_build_int_key_from_kv`, `__wt_cell_kv_copy`, `__wt_cell_pack_internal_key_addr`, and `__wt_cell_build_addr`.

Type and length helpers include `__wt_cell_rle`, `__wt_cell_total_len`, `__wt_cell_type`, `__wt_delta_cell_type_visible_all`, `__wt_cell_type_raw`, `__wt_cell_type_reset`, and `__wt_cell_leaf_value_parse`.

Unpack helpers include `__wt_cell_unpack_safe`, `__wt_cell_unpack_addr`, `__wt_cell_unpack_kv`, `__wt_cell_unpack_delta_leaf_value`, plus internal address/value window decoders and cleanup helpers.

Data access helpers include `__wt_cell_get_ta`, `__wt_cell_get_tw`, `__wt_dsk_cell_data_ref_addr`, `__wt_dsk_cell_data_ref_kv`, and `__wt_page_cell_data_ref_kv`. Iterator macros include delta leaf, delta internal, base internal, address, and key/value foreach forms.

## Control Flow
Packing starts with a zero descriptor byte, optionally emits validity/aggregate metadata through a second descriptor byte, optionally emits RLE or recno, emits packed data length when needed, and returns the header length. Short key/value cells avoid the length varint when size fits in six descriptor bits.

Value-window packing stores timestamps and transaction IDs compactly, often as deltas from the start timestamp or transaction. Prepared starts/stops are encoded into timestamp/durable fields, with additional prepared ID storage when `WT_CONN_PRESERVE_PREPARED` is enabled. Address aggregate packing follows similar delta encoding and can mark prepared fast truncation.

Unpacking normalizes raw cell variants into common fields. It handles short cells directly, decodes optional prefix bytes and second-descriptor windows, reads RLE/recno, resolves `WT_CELL_VALUE_COPY` by jumping backward to the source cell while preserving the current cell's RLE/window/length, and computes the full cell length for iteration. Safe unpacking can enforce an end pointer for verification.

Restart cleanup checks page write generations against the btree base write generation and clears persisted transaction IDs while preserving timestamp semantics. This cleanup applies to both key/value windows and address aggregates, including fast-truncate page delete metadata.

Data-reference helpers either point at on-page data or read overflow items through `__wt_ovfl_read`. The disk-only KV accessor asserts it is not asked to read removed overflow cells; the page-aware accessor can use page context for lookaside/cached overflow handling.

## State and Persistence Behavior
The functions produce and interpret persistent page bytes, including transaction/timestamp visibility and fast-truncate state. They also mutate unpacked in-memory structures during restart cleanup by clearing transaction IDs and setting `WT_CELL_UNPACK_TIME_WINDOW_CLEARED` so reconciliation can rebuild cells. Image-building helpers append bytes to caller-owned `WT_ITEM` buffers and update delta merge state such as entry counts and last key.

## Dependencies and Integration Points
Depends on timestamp/window validators, varint packing/unpacking, `WT_TIME_WINDOW`, `WT_TIME_AGGREGATE`, `WT_PAGE_DELETED`, `WT_PAGE_HEADER`, `WT_CELL_KV`, `WT_ITEM`, buffer helpers, overflow read, structured unpacking, B-tree flags, write generations, and disaggregated merge state. It integrates with reconciliation, page read/verify, row/column cell iteration, delta page merge, truncate, prepared transaction recovery, dictionary compression, overflow item handling, and garbage-collection tables.

## Risks and Edge Cases
This file is format-critical. Incorrect flag ordering, delta arithmetic, or prepared ID placement can make existing page images unreadable or corrupt MVCC visibility. The comments call out `FIXME-WT-14887` around pointer memory safety in `__wt_cell_kv_copy` and `FIXME-WT-17663` for passing correct prepared-fast-truncate state in internal key/address packing. `WT_CELL_VALUE_COPY` requires careful length preservation or page iteration will desynchronize. Restart cleanup must not erase timestamp semantics while clearing non-persistent transaction IDs. Verification paths rely on `WT_CELL_LEN_CHK` to prevent out-of-bounds reads.

## Test Signals
High-value tests include cell pack/unpack round trips, verify with truncated/corrupt cells, timestamp window validation, prepared update recovery with preserve-prepared, fast truncate and prepared fast truncate, overflow read/remove behavior, dictionary value copies, row prefix compression/decompression, delta leaf/internal merge, restart cleanup across write generations, and garbage-collection table timestamp assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/column_inline.h -->
# sources/storage-engines/wiredtiger/src/include/column_inline.h

## Purpose
Defines inline search helpers for column-store insert skiplists and variable-length column-store page slots. These helpers support exact and directional record-number lookups, insert-position stack construction, append detection, and RLE-aware page indexing.

## Important APIs, Types, and Functions
`__col_insert_search_gt` returns the smallest inserted record greater than a target recno. `__col_insert_search_lt` returns the largest inserted record smaller than a target recno. `__col_insert_search_match` returns an exact recno match.

`__col_insert_search` performs the general insert-list search and fills `ins_stack` and `next_stack` for insertion at each skiplist level. It fast-paths appends at or beyond the current last record.

`__col_var_last_recno` computes the last base record on a variable-length column-store page, accounting for run-length encoded repeats but ignoring append-list inserts.

`__col_var_search` maps a recno to a `WT_COL` slot using a binary search over repeat metadata followed by direct offset arithmetic.

## Control Flow
Skiplist searches start from the highest level and move forward while the next record is below or at the target condition, then drop levels. Acquire barriers guard against compiler and weak-memory reordering while reading concurrently updated skiplist links. Directional searches use first/last fast paths to avoid full skiplist traversal when the target lies outside the list.

`__col_insert_search` fills insertion predecessor and successor arrays while descending. On append, it points stack entries at tails or heads and sets `next_stack` to null. On exact match, it fills lower-level stacks from the matched node's next links.

Variable-column search first binary-searches `pg_var_repeats` for an RLE run containing the recno. If no run contains it, it starts after the largest repeat less than the target and computes the slot offset while avoiding arithmetic overflow.

## State and Persistence Behavior
The skiplist helpers read volatile in-memory insert lists (`WT_INSERT_HEAD` and `WT_INSERT`) that represent updates not necessarily present in the base disk image. `__col_var_search` reads in-memory page structures derived from persistent column-store cells and repeat metadata. No persistent state is written here.

## Dependencies and Integration Points
Depends on `WT_INSERT`, `WT_INSERT_HEAD`, skiplist macros, `WT_INSERT_RECNO`, `WT_COL`, `WT_COL_RLE`, page type fields, record-number constants, and memory barrier macros. It integrates with column-store cursor search/next/prev, append handling, update insertion, reconciliation of column pages, and visible update selection.

## Risks and Edge Cases
Concurrent insertions can reorder observations across skiplist levels without barriers; the code explicitly guards against stale lower-level values causing missed records. Directional searches assume the existence checks against first/last remain valid enough under concurrent mutation. Variable-column last-recno and search must handle empty pages, pages with no repeats, repeated runs, appended records outside the base page, and overflow-safe recno arithmetic near `UINT64_MAX`.

## Test Signals
Useful tests include fixed and variable column-store cursor search/next/prev, concurrent append/update workloads, exact and non-exact recno searches, RLE-heavy pages, empty pages, append-list interactions, and sanitizer/TSAN runs around skiplist memory ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/column_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/compact.h -->
# sources/storage-engines/wiredtiger/src/include/compact.h

## Purpose
Defines the small state object used by WiredTiger compaction operations. It records whether the run is estimation-only, how many files have been considered, the target amount of reclaimable space, the configured time limit, and progress timestamps.

## Important APIs, Types, and Functions
`WT_COMPACT_STATE` contains `dryrun`, `file_count`, `free_space_target`, `max_time`, `begin`, and `last_progress`. There are no inline functions or macros beyond the struct definition.

## Control Flow
Runtime compaction code initializes this structure at the start of a compact operation, updates `file_count` as files are inspected or processed, checks elapsed time against `begin` and `max_time`, compares estimated or actual free space against `free_space_target`, and uses `last_progress` to rate-limit progress messages.

## State and Persistence Behavior
The struct is transient operation state. It does not persist data directly, but it guides compaction decisions that may rewrite files and release disk space. In dry-run mode, callers should use it to estimate without performing the rewriting phase.

## Dependencies and Integration Points
Depends only on standard `bool`, integer types, and `struct timespec`. It integrates with compaction command execution, file iteration, progress logging, timeout enforcement, and free-space estimation/recovery logic elsewhere in WiredTiger.

## Risks and Edge Cases
Timeout checks depend on monotonic and consistent time handling by callers. `free_space_target` and dry-run behavior must be interpreted consistently so dry runs do not mutate files. Progress timestamps should be initialized before logging decisions. Large compactions need `file_count` and time accounting to remain accurate across many files.

## Test Signals
Relevant tests include compact dry-run behavior, compact timeout/max-time enforcement, free-space target handling, progress message throttling, and multi-file compact runs that update `file_count`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/compact.h -->
