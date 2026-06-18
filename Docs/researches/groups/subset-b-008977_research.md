# Research Group: subset-b-008977

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_walk.c -->
# sources/storage-engines/wiredtiger/src/evict/evict_walk.c

## Purpose
This file implements the eviction server's tree walk logic. Its job is to choose a btree handle, traverse pages from a remembered or randomized point, score pages, and place ordinary or urgent candidates on eviction queues. It is the bridge between global cache pressure signals and per-page eviction decisions.

## Important APIs, Types, And Functions
The exported entry point is `__wti_evict_walk`, which fills a `WTI_EVICT_QUEUE` by selecting handles from the connection dhandle list and calling `__evict_walk_tree`. `__wti_evict_push_candidate` atomically marks a `WT_PAGE` with `WT_PAGE_EVICT_LRU`, initializes the queue entry, and computes its score through `__evict_entry_priority`. Exclusive-eviction paths use `__wti_evict_clear_all_walks_and_saved_tree` and `__wti_evict_clear_walk_and_saved_tree_if_current_locked` to drop pinned walk points. The main internal helpers are `__evict_walk_choose_dhandle`, `__evict_btree_dominating_cache`, `__evict_walk_target`, `__evict_get_target_pages`, `__evict_walk_prepare`, `__evict_try_restore_walk_position`, `__evict_should_give_up_walk`, `__evict_skip_dirty_candidate`, and `__evict_try_queue_page`.

## Control Flow
`__wti_evict_walk` determines how many queue slots to fill, caps the work to avoid monopolizing all candidates, then loops over dhandles while holding and releasing `dhandle_lock` around handle selection. It skips closed, non-btree, eviction-disabled, readonly, checkpointing, disaggregated checkpointed, sticky, inactive, or in-memory clean-only handles. Once a handle is chosen, it stores it as the saved walk tree, releases the dhandle list lock, obtains `evict_walk_lock`, and calls `__evict_walk_tree`.

`__evict_walk_tree` computes the target number of pages for the tree from clean, dirty, and update bytes. It prepares the starting ref using an existing hard pointer, a soft normalized position, the root, or a random descent. It then walks refs using `__wt_tree_walk_count`, updates visit statistics, skips roots and already queued pages, and asks `__evict_try_queue_page` whether each page matches the current eviction mode. It stops after enough candidates, two end-of-tree restarts, or a poor candidate-to-page ratio.

## State And Persistence Behavior
The key persistent-in-memory state is stored on `WT_BTREE`: `evict_ref`, `evict_pos`, `evict_saved_ref_check`, `evict_start_type`, `evict_walk_target`, `evict_walk_progress`, `evict_walk_period`, `evict_walk_skips`, `last_evict_walk_flags`, and `evict_priority`. Pages are not written here, but this file selects dirty pages whose later eviction may reconcile pages and update disk/history-store state. When normalized positions are enabled, `__evict_clear_walk` converts a held ref into a soft tree position and releases the hazard pointer so exclusive file operations can proceed.

## Dependencies And Integration Points
The file depends heavily on `btree.h` normalized positions and eviction walk types, `btmem.h` read flags, page/ref states, read generations, modification metadata, and update-candidate helpers. It integrates with the eviction subsystem through `WT_EVICT`, `WTI_EVICT_QUEUE`, urgent queueing, cache pressure flags, and connection statistics. It coordinates with transaction visibility through snapshots and `last_running`, with checkpoint state through `WT_BTREE_SYNCING` and precise checkpoint checks, and with disaggregated storage through garbage-collect btrees, stable checkpointed trees, prune timestamps, HS-dirty prioritization, and page-delta LSN state.

## Risks
The main correctness risks are stale walk refs, leaked hazard pointers, queueing the same page twice, evicting pages whose updates are not visible enough to reconcile, starving trees because `evict_walk_period` grows too aggressively, and bad interactions with checkpoints or disaggregated trees. The soft-position path is sensitive to tree splits because a restored position may not identify the original ref. The dirty-page skip heuristics are workload-sensitive: too strict can starve eviction, too loose can thrash reconciliation and history-store growth.

## Test Signals
Useful signals include eviction statistics for skipped trees/pages, walk give-up reasons, restored-position counters, ordinary and urgent queued pages, internal-page queue counts, dirty/update pressure tests, checkpoint plus eviction concurrency, exclusive file close while eviction walks are active, in-memory btree behavior, disaggregated checkpoint follower/leader cases, history-store dirty pressure, and stress tests with many handles and split-heavy trees.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_walk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/history/hs_conn.c -->
# sources/storage-engines/wiredtiger/src/history/hs_conn.c

## Purpose
This file owns history-store lifecycle at connection setup and shutdown. It creates the local history store, optionally creates the shared disaggregated history store, configures the opened history-store btree handles, records the history-store file id in cache state, and clears legacy lookaside storage from upgraded databases.

## Important APIs, Types, And Functions
`__wt_hs_open` is the startup entry point. It opens an internal session, drops `file:WiredTigerLAS.wt` if present, creates `WT_HS_URI`, creates `WT_HS_URI_SHARED` for disaggregated connections, and delegates to `__wt_hs_config`. `__wt_hs_config` iterates history-store ids with `__wt_curhs_next_hs_id` and calls `__hs_config`. `__hs_config` validates `history_store.file_max`, opens a temporary internal session named `hs_access`, retrieves the btree through `__hs_get_btree`, sets `btree->file_max`, updates `cache_hs_ondisk_max`, records `conn->cache->hs_fileid`, and sets `WT_CONN_HS_OPEN`. `__wt_hs_close` clears the open flag. `__hs_cleanup_las` removes the obsolete lookaside file under the schema lock.

## Control Flow
Startup exits early for readonly or in-memory connections because no writable history store is needed. Otherwise, `__wt_hs_open` uses a dedicated internal session so recovery-time default-session concurrency does not corrupt setup. Creation is idempotent at the schema layer and then configuration uses real history-store cursors to get the btree backing each HS id. The configuration loop is open-ended and terminates on `WT_NOTFOUND`, which allows future local/shared ids without hard-coding a fixed count.

## State And Persistence Behavior
This file persists history-store existence by creating the HS table files and, for disaggregated deployments, the shared HS table with `block_manager=disagg`. It does not write HS records directly. Runtime state changes are connection-global: `WT_CONN_HS_OPEN` advertises HS availability, `conn->cache->hs_fileid` identifies the HS file for cache accounting, and each HS btree's `file_max` enforces configured on-disk bounds. Legacy lookaside cleanup is persistent because it drops an old file if an upgraded home still contains it.

## Dependencies And Integration Points
The code depends on schema operations, internal sessions, history-store cursor helpers, cache statistics, connection flags, and configuration parsing. It integrates with `btmem.h` HS URI/config definitions, `btree.h` file id fields, the cache's HS accounting, and disaggregated storage detection. It must run before any component expects `WT_CONN_HS_OPEN` and before reconciliation or reads rely on history-store cursors.

## Risks
Misconfiguring `history_store.file_max` below `WT_HS_FILE_MIN` is rejected. Failing to close temporary sessions can leak internal resources, so all setup paths use cleanup in `err`. Opening cursors to retrieve btree handles during startup is sensitive to partial creation failure. The `WT_CONN_HS_OPEN` flag must only be set after the btree is actually open; otherwise readers could attempt HS access too early.

## Test Signals
Test startup in normal, readonly, in-memory, and disaggregated modes. Exercise upgrades that still have `WiredTigerLAS.wt`, invalid and valid `history_store.file_max`, shared HS creation, file id assignment, shutdown flag clearing, and injected failures during internal session open, schema create/drop, cursor open, and configuration.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/history/hs_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/history/hs_cursor.c -->
# sources/storage-engines/wiredtiger/src/history/hs_cursor.c

## Purpose
This file provides low-level operations for modifying, reading, reconstructing, and truncating history-store records. It is central to timestamped reads that need older values, rollback/recovery code that manipulates HS content, and cleanup paths that remove all history for a btree id.

## Important APIs, Types, And Functions
`__wt_hs_modify` writes a supplied `WT_UPDATE` into the HS using `__wt_row_modify` directly on a `WT_CURSOR_BTREE`, bypassing the ordinary cursor API because HS updates must be immediately visible and do not follow normal transaction semantics. `__wt_hs_upd_time_window` exposes the `WT_TIME_WINDOW` from a positioned HS cursor's `upd_value`. `__wt_hs_find_upd` searches the HS for the visible historical update for a row key or column-store recno and fills a `WT_UPDATE_VALUE`. `__wt_hs_btree_truncate` deletes the contiguous HS key range for a given btree id using start and stop HS cursors and `WT_SESSION::truncate`.

## Control Flow
`__wt_hs_find_upd` first normalizes the caller's key: row-store passes a `WT_ITEM`, column-store recnos are packed into a temporary item. Checkpoint reads with no HS checkpoint and readonly disaggregated btrees without a matching shared HS checkpoint return a miss. Otherwise, it opens an HS cursor for `btree->id`, chooses a read timestamp from the checkpoint read timestamp or transaction read timestamp, maps `WT_TS_NONE` to `WT_TS_MAX`, and searches backward before that timestamp. On a hit, it reads stop durable timestamp, durable timestamp, update type, and value.

If the HS update is a reverse modify, `__wt_hs_find_upd` sets `WT_CURSTD_HS_READ_COMMITTED`, walks forward through older HS entries until it finds a standard base value or falls back to the datastore base value, then applies modify records in reverse-pop order through `__wt_modify_apply_item`. Callers can set `upd_value->skip_buf` to check existence without reconstructing the value.

`__wt_hs_btree_truncate` positions a start cursor at the first key for `btree_id`, positions a stop cursor at the first key for `btree_id + 1`, steps back to the last key for the target id, and truncates the inclusive range.

## State And Persistence Behavior
This file directly changes persisted HS content through `__wt_hs_modify` and range truncation. Reads build transient `WT_UPDATE_VALUE` state: `buf`, `tw.durable_start_ts`, `tw.start_txn = WT_TXN_NONE`, and `type`. Modify reconstruction uses temporary scratch buffers and a `WT_UPDATE_VECTOR` to avoid exposing partial state. HS records no longer contain tombstones, and the code asserts that invariant.

## Dependencies And Integration Points
The code depends on HS cursor helpers, btree ids, transaction timestamps, checkpoint metadata, row/column key packing, update allocation, modify application, scratch buffers, and session cursor truncation. It integrates with the read path that restores historical updates, reconciliation/RTS paths that write HS records, and metadata/disaggregated checkpoint selection.

## Risks
The timestamp ordering and search direction are subtle because HS keys include timestamp and counter. Mapping no-timestamp reads to `WT_TS_MAX` prevents hiding newer records. Reverse-modify reconstruction is risky if the base datastore value does not match the expected chain, if `skip_buf` leaks across calls, or if cursor visibility flags are wrong. Truncation relies on HS key ordering by btree id; an incorrect stop cursor could delete another tree's history.

## Test Signals
Tests should cover row and column keys, no-timestamp reads, checkpoint reads with and without HS checkpoints, disaggregated readonly stable handles, standard and modify HS updates, fallback to datastore base values, `skip_buf`, truncating empty and non-empty btree ranges, diagnostic checks for stop cursor positioning, and resource cleanup on all error paths.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/history/hs_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/history/hs_verify.c -->
# sources/storage-engines/wiredtiger/src/history/hs_verify.c

## Purpose
This file verifies history-store consistency. Its core invariant is that there must not be a history-store entry for a key unless the corresponding key exists in the data store. It supports verifying one btree with exclusive access and verifying all history-store ids across the connection.

## Important APIs, Types, And Functions
`__wt_hs_verify_one` verifies a single btree id. It opens an HS cursor, positions to the first record for that btree id, opens a raw btree cursor directly with `__wt_btcur_init` and `__wt_btcur_open`, then delegates to `__hs_verify_id`. `__wt_hs_verify` is the public all-HS entry point; it iterates ids via `__wt_curhs_next_hs_id` and calls `__hs_verify`. `__hs_verify` scans the selected HS table, resolves btree ids to data-store URIs, opens the corresponding data-store cursor, and calls `__hs_verify_id` for each id run. `__hs_verify_id` walks HS keys for a single btree id and searches the data store for each distinct key.

## Control Flow
`__hs_verify_id` assumes the HS cursor is already positioned. For each HS record with the target btree id, it compares the key with the previously checked key and skips duplicate versions. For row-store it calls `__wt_row_search`; for column-store it unpacks the recno and calls `__wt_col_search`, both under `WT_WITH_PAGE_INDEX`. If the data-store cursor comparison says the key was not found, it marks `WT_CONN_DATA_CORRUPTION` and panics with a formatted key message. It resets the data-store cursor between keys and leaves the HS cursor either at the next btree id or EOF.

`__hs_verify` handles whole-HS traversal. On disaggregated followers it opens shared stable history-store and data-store checkpoints rather than live stable handles, because followers cannot dirty pages and live reads can trigger leader-only assertions when stop-timestamp records are reinstantiated.

## State And Persistence Behavior
Verification is read-only unless corruption is detected, in which case it sets `WT_CONN_DATA_CORRUPTION` and panics. It sets cursor flags such as `WT_CURSTD_HS_READ_COMMITTED`, `WT_CURSTD_IGNORE_TOMBSTONE`, and `WT_CURSOR_RAW_OK` to make verification see the necessary physical content. No HS records are added or removed.

## Dependencies And Integration Points
The file depends on HS cursor APIs, metadata btree-id-to-URI lookup, row and column btree search, checkpoint metadata lookup, raw cursor behavior, page-index generation protection, and connection disaggregation state. It complements the generic verify command by checking the cross-file invariant between HS entries and data-store keys.

## Risks
The verifier intentionally panics on mismatches, so false positives are severe. Duplicate HS versions for one key must be skipped correctly to avoid redundant work. Column-store key unpacking must match HS key encoding. Disaggregated follower logic must choose checkpoints consistently; otherwise verification may compare HS and data-store snapshots from different generations. Cursor ownership is error-prone because `__hs_verify_id` moves the HS cursor for its caller.

## Test Signals
Test one-tree and all-HS verification, empty HS tables, duplicate HS versions per key, missing datastore keys, row-store and column-store keys, metadata id lookup failures, disaggregated leader and follower checkpoint paths, no-checkpoint follower early returns, and cleanup of data/HS cursors after corruption and normal EOF.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/history/hs_verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/api.h -->
# sources/storage-engines/wiredtiger/src/include/api.h

## Purpose
This header defines the macro framework used by WiredTiger public connection, session, and cursor APIs. The macros standardize entry/exit bookkeeping, configuration validation, error-state handling, operation timing, transaction wrapping, retry-on-rollback behavior, overload rejection, and cursor-specific invariants.

## Important APIs, Types, And Functions
The base stack macros are `API_SESSION_PUSH`, `API_SESSION_POP`, and `API_SESSION_INIT`. `API_CALL`, `API_CALL_NOCONF`, and `API_CALL_NOCONF_NOERRCLEAR` wrap general entry points, while `API_END` unwinds the session and reconciles the return value with `session->err_info`. `TXN_API_CALL`, `TXN_API_CALL_NOCONF`, and `TXN_API_END` add autocommit transaction handling and optional rollback retry. Convenience wrappers cover connection calls, session calls that allow or reject prepare context, cursor calls, cursor update/remove calls, API stats, not-found mapping, retryable readonly APIs, cursor reposition windows, and compiled configuration setup.

## Control Flow
An API function enters by pushing the current dhandle/name, incrementing `api_call_counter`, setting `lastop`, checking panic state, starting single-thread and operation tracking, resetting wait/error state for outermost calls, clearing the global error log for external calls, and optionally validating configuration. Exit through `API_END` ends operation tracking, stops single-thread checks, optionally records transaction errors, normalizes `err_info`, stops operation timers, checks that too many HS cursors are not left open, and pops the saved session fields.

Transactional wrappers mark autocommit/update state when the caller is not already in a transaction. `TXN_API_END` either retries rollback, commits successful implicit transactions, or rolls back and resets cursors on error. Cursor update wrappers also check write overload and in-memory cache-full behavior. Read cursor wrappers can reject user reads under load control.

## State And Persistence Behavior
The macros mutate session runtime state: `dhandle`, `name`, `lastop`, `api_call_counter`, `cache_wait_us`, `err_info`, transaction flags, operation timers, cursor cached/reposition flags, and load-control statistics. They do not directly persist data, but they decide whether API operations commit, roll back, retry, return `WT_ROLLBACK`, map `WT_NOTFOUND` to `ENOENT`, or report errors into transaction state.

## Dependencies And Integration Points
This header depends on session, transaction, config, stats, load-control, cursor, and error-log helpers. It is included by API implementation files and defines the control skeleton those functions rely on. Because the macros open `do { ... } while` scopes and introduce local variables such as `__set_err`, `__autotxn`, and `__update`, callers must structure labels and `goto err` paths exactly around them.

## Risks
Macro ordering is the main risk. Code before `API_SESSION_INIT` or after `API_END` can break error handling. Missing an exit macro leaves counters, dhandles, timers, or transaction flags inconsistent. Nested API calls make `api_call_counter` behavior subtle, especially for error reset, operation timers, HS cursor assertions, and retry loops. Since these are macros, local variable name collisions and control-flow surprises are possible.

## Test Signals
API tests should cover nested calls, successful and failing config validation, panic checks, `WT_NOTFOUND` mapping, err_info synchronization, autocommit commit/rollback/retry, prepare-context rejection, load-control read/write rejection, cursor cache reuse, cursor reposition flags, in-memory cache-full updates, and leak checks for API counters and cursor/session state after errors.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/bitstring.h -->
# sources/storage-engines/wiredtiger/src/include/bitstring.h

## Purpose
This small public-domain-derived header defines the byte and mask layout macros for compact bitstrings. WiredTiger keeps these preprocessor macros separate from inline functions so layout calculations can be reused without pulling in the full helper implementation.

## Important APIs, Types, And Functions
`__bit_byte(bit)` maps a bit index to its containing byte by shifting right three bits. `__bit_mask(bit)` creates the mask for the bit within that byte using the low three bits. `__bitstr_size(nbits)` returns the number of bytes needed to store `nbits`, rounded up to the next byte.

## Control Flow
There is no runtime control flow in this file. All three definitions are arithmetic macros expanded at call sites. The inline header builds allocation, set, clear, range, and first-bit search operations on top of these definitions.

## State And Persistence Behavior
The file defines the memory layout contract for bitstrings: bits are packed little-bit-endian within each byte, with bit zero in mask `1 << 0`. It does not allocate or mutate memory itself. Any persistent behavior is indirect when other components use bitstrings for tracking on-disk or verification state.

## Dependencies And Integration Points
The companion file `bitstring_inline.h` depends on these macros. Other low-level structures can use `__bitstr_size` to size allocations without duplicating rounding logic. The block manager verification code is one likely consumer because it uses byte arrays to track file/checkpoint fragments.

## Risks
The macros do not validate bounds, integer width, or side effects. Passing expressions with side effects can evaluate more than once in some use contexts outside this file. Changing bit order or size rounding would silently corrupt all users that share bitstring memory with existing assumptions.

## Test Signals
Test byte sizing at zero, one, seven, eight, and boundary values; bit set/test/clear behavior through the inline helpers; range operations across one and multiple bytes; and any consumer that serializes or reports bitstring-backed state.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/bitstring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/bitstring_inline.h -->
# sources/storage-engines/wiredtiger/src/include/bitstring_inline.h

## Purpose
This header implements inline bitstring allocation and manipulation helpers using the layout macros from `bitstring.h`. It provides fast, dependency-light primitives for compact boolean arrays inside the storage engine.

## Important APIs, Types, And Functions
`__bit_alloc` allocates a zeroed byte array large enough for `nbits`. `__bit_test`, `__bit_set`, and `__bit_clear` operate on one bit. `__bit_nclr` and `__bit_nset` clear or set inclusive ranges. `__bit_ffc` finds the first clear bit, and `__bit_ffs` finds the first set bit, returning `0` on success and `-1` when no matching bit exists.

## Control Flow
Single-bit helpers compute byte and mask and update the target byte directly. Range helpers compute start and stop bytes; if the range is within one byte they combine masks, otherwise they update the partial start byte, full middle bytes, and partial stop byte. First-bit search helpers scan bytes from zero to `__bit_byte(nbits - 1)` and then scan the low bits of the first byte that is not all-set or not all-clear, rejecting matches beyond `nbits` in the final partial byte.

## State And Persistence Behavior
The helpers mutate caller-owned `uint8_t` buffers. `__bit_alloc` uses WiredTiger allocation through `__wt_calloc`, so memory is session-accounted and zero-initialized. There is no locking or atomicity; concurrent users must synchronize externally. The bit layout is stable because it is inherited from `bitstring.h`.

## Dependencies And Integration Points
The implementation depends on `WT_SESSION_IMPL`, `WT_INLINE`, `__wt_calloc`, and the `__bit_*` macros. It is suitable for hot paths because functions are inlined and avoid function pointer dispatch. Consumers include low-level tracking arrays such as block verification fragment maps and any component that needs dense bit sets.

## Risks
The API assumes valid buffers and valid inclusive ranges. Passing `start > stop`, out-of-range bit indexes, or a buffer shorter than `__bitstr_size(nbits)` causes memory corruption. `__bit_nclr` and `__bit_nset` rely on 8-bit masks; changes to `uint8_t` assumptions or signed promotion could affect unusual platforms. Search is linear in bytes, so very large bitstrings can become expensive.

## Test Signals
Cover zero-length searches, first and last bits in partial bytes, all-set and all-clear buffers, single-byte and multi-byte range set/clear, alternating patterns, allocation size, and sanitizer/diagnostic tests for callers' boundary calculations.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/bitstring_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/block.h -->
# sources/storage-engines/wiredtiger/src/include/block.h

## Purpose
This header defines the default and disaggregated block-manager data structures, persistent block formats, checkpoint extent metadata, and the `WT_BM` vtable used by btree code to read, write, checkpoint, compact, salvage, verify, and sync pages.

## Important APIs, Types, And Functions
Core types include `WT_EXTLIST`, `WT_EXT`, and `WT_SIZE` for checkpoint allocation/free/discard extent management; `WT_BLOCK_CKPT` for checkpoint cookies and extent lists; `WT_BM` for the block-manager method table; `WT_BLOCK` for local file-backed block handles; `WT_BLOCK_DESC` and `WT_BLOCK_HEADER` for ordinary on-disk headers; `WT_BLOCK_DISAGG`, `WT_BLOCK_DISAGG_HEADER`, and `WT_BLOCK_DISAGG_ADDRESS_COOKIE` for disaggregated page-log storage. Iterator macros such as `WT_EXT_FOREACH`, `WT_EXT_FOREACH_OFF`, and `WT_EXT_FOREACH_FROM_OFFSET_INCL` define extent traversal.

## Control Flow
This file is declarative, but its vtable defines the control surface used throughout the engine. Btree code calls `WT_BM` methods for address validation/stringification, checkpoint start/load/resolve/unload, read/write/read_multiple, free, compaction, salvage, verification, object switching, mapping, stats, sync, and write-size alignment. Extent-list macros drive block allocation and verification code by walking skiplist heads in offset or size order.

## State And Persistence Behavior
Many definitions are persistent format contracts. Offset zero is invalid because the description block lives at the first block. `WT_BLOCK_DESC`, `WT_BLOCK_HEADER`, and `WT_BLOCK_DISAGG_HEADER` sizes and flag values cannot change without disk compatibility impact. `WT_BLOCK_CKPT` models the checkpoint's root address, allocated/available/discarded extents, file size, checkpoint size, and archived checkpoint extents. Disaggregated address cookies persist page id, flags, LSNs, cumulative size, and checksum for base/delta chains.

## Dependencies And Integration Points
The header integrates with `btmem.h` page headers, block manager implementation files, btree reconciliation, checkpoint metadata, compaction, salvage, verification, tiered/multi-handle objects, and disaggregated storage. It depends on skiplist depths, file handles, checksums, time/address metadata, page block metadata, and storage abstractions such as bucket storage or page log through associated structs.

## Risks
Disk-format sensitivity is high. Changing field order, sizes, magic values, header flags, or checkpoint cookie layout can break existing databases. `WT_BLOCK` and `WT_BLOCK_DISAGG` must keep a shared prefix; violating that breaks code that treats them generically. Extent skiplist nodes appear on multiple lists, so incorrect depth/offset handling can corrupt free-space accounting. Multi-handle arrays require locking discipline.

## Test Signals
Use static layout assertions, endian tests, checkpoint round trips, salvage over corrupt blocks, verification of extent overlap/fragment maps, compaction rewrite accounting, multi-object/tier switch tests, disaggregated base/delta checksum chains, and backward-compatibility tests that open older files.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/block_cache.h -->
# sources/storage-engines/wiredtiger/src/include/block_cache.h

## Purpose
This header defines metadata for WiredTiger's optional block cache, which caches disk-identical blocks in a faster medium such as DRAM or NVRAM. It provides the item layout, global cache configuration, hash table state, eviction tuning, and metrics for deciding whether the cache is useful.

## Important APIs, Types, And Functions
`WT_BLKCACHE_DELTA` stores one delta payload associated with a cached block. `WT_BLKCACHE_ITEM` is a hash-bucket entry containing data bytes, optional deltas, reference counts, a frequency/recency counter, returned `WT_PAGE_BLOCK_META`, file id, address-cookie size, and flexible address bytes. `WT_BLKCACHE` owns hash buckets and locks, the eviction thread id, exit flag, aggressive eviction timeout, write/checkpoint population flags, optional memkind NVRAM handle, target sizes, filesystem-cache bypass heuristics, cache type, bytes used/max bytes, reference thresholds, and counters/histograms.

## Control Flow
The file itself has no functions, but its fields define runtime flow for block-cache lookup, insertion, eviction, and bypass. Lookups hash by file id plus address. Cache references increment `num_references` and `freq_rec_counter`; the eviction thread decrements counters and removes low-value blocks. The cache can skip population when filesystem cache is expected to be sufficient or overhead is too high.

## State And Persistence Behavior
The block cache is an in-memory or NVRAM-backed performance layer for blocks identical to on-disk content. It does not define database correctness state: cache misses should fall back to the block manager. `bytes_used`, reference counters, histograms, and overhead metrics are runtime-only. Optional NVRAM configuration points at a filesystem path and memkind allocation kind, but cached entries mirror persistent blocks rather than replacing them.

## Dependencies And Integration Points
The header integrates with block-manager read/write paths, page block metadata, eviction threads, connection configuration, statistics, and optional `ENABLE_MEMKIND`. It interacts with disaggregated/page-delta support through per-item deltas and block metadata.

## Risks
Concurrency risks center on per-bucket locking, item `ref_count`, eviction while readers hold data, and heuristic counters updated without precise synchronization. Flexible-array address storage must match the supplied cookie size. The cache must never return stale data for a reused block address or mismatched file id. NVRAM support adds allocator/device lifecycle risk.

## Test Signals
Test cache hits/misses by address and file id, concurrent lookups/removals, eviction frequency thresholds, byte accounting, histograms, bypass heuristics, cache-on-write/checkpoint toggles, NVRAM allocation when enabled, delta-bearing entries, and fallback correctness after eviction.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/block_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/block_inline.h -->
# sources/storage-engines/wiredtiger/src/include/block_inline.h

## Purpose
This header provides small inline block-manager helpers. It defines latency histogram increment functions, packing/unpacking helpers for extent-list pairs, endian conversion helpers for block headers, and a predicate for sweeping block handles.

## Important APIs, Types, And Functions
`WT_STAT_MSECS_HIST_INCR_FUNC` and `WT_STAT_USECS_HIST_INCR_FUNC` instantiate histogram helpers for normal and disaggregated block-manager read/write latency. `__wt_extlist_write_pair` and `__wt_extlist_read_pair` encode/decode extent offset and size as variable-length packed integers. `__wt_block_header_byteswap_copy` and `__wt_block_header_byteswap` convert `WT_BLOCK_HEADER` fields on big-endian systems. `__wt_block_header` returns `WT_BLOCK_HEADER_SIZE`. `__wt_block_eligible_for_sweep` says a block handle can be swept when it is local and its object id is at or below `bm->max_flushed_objectid`.

## Control Flow
Extent serialization writes offset first and size second; reading mirrors that order and casts unpacked `uint64_t` values to `wt_off_t`. Byteswap helpers copy before swapping when source and target differ. Sweep eligibility deliberately omits the active read-count check because callers perform that elsewhere.

## State And Persistence Behavior
The packing helpers participate in persistent checkpoint extent-list encoding. Header byteswapping preserves the on-disk little-endian format across host endian variants. Sweep eligibility affects lifecycle of block handles after object switching or flushing but does not itself close or free handles.

## Dependencies And Integration Points
The file depends on `block.h` structures, integer packing helpers, stats macros, endian helpers, and block-manager object-id state. It is used by block allocation/checkpoint code, read/write statistics, and multi-object sweeping paths.

## Risks
Encoding order must remain consistent with checkpoint readers. Endian conversion must only swap fields that are part of the fixed header and must preserve flags/padding. Sweep eligibility is only safe when combined with the separate read-reference check; using it alone could remove a handle still in use.

## Test Signals
Test extent pair encode/decode round trips, big-endian header conversion through simulated or platform tests, histogram updates for block IO, and object sweep behavior with remote blocks, old local blocks, and blocks newer than `max_flushed_objectid`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/block_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btmem.h -->
# sources/storage-engines/wiredtiger/src/include/btmem.h

## Purpose
This header is the central in-memory btree/page model. It defines disk page headers, read flags, history-store record formats, reconciliation replacement state, page modification metadata, page/ref/update/insert structures, split-generation protection, and verification context.

## Important APIs, Types, And Functions
Important persistent and runtime types include `WT_PAGE_HEADER`, `WT_ADDR`, `WT_OVFL_REUSE`, `WT_SAVE_UPD`, `WT_PAGE_BLOCK_META`, `WT_PAGE_DISAGG_INFO`, `WT_MULTI`, `WT_OVFL_TRACK`, `WT_PAGE_MODIFY`, `WT_PAGE_INDEX`, `WT_PAGE`, `WT_PAGE_DELETED`, `WT_ADDR_COPY`, `WT_REF`, `WT_ROW`, `WT_COL`, `WT_IKEY`, `WT_UPDATE`, `WT_UPDATE_VALUE`, `WT_UPDATE_VECTOR`, `WT_INSERT`, `WT_INSERT_HEAD`, and `WT_VERIFY_INFO`. Key macros define read flags, HS key/value formats and table configs, page/ref/update states, page flags, update flags, read generations, row/column accessors, insert-list helpers, and split-generation enter/leave wrappers.

## Control Flow
The declarations encode the control model used elsewhere. Readers use `WT_REF` states plus hazard pointers to move pages from disk to memory and protect them. Eviction transitions refs through `WT_REF_LOCKED` and either back to `WT_REF_MEM` or to `WT_REF_DISK`. Internal page splits atomically swap `WT_PAGE_INDEX` pointers, and readers must enter `WT_GEN_SPLIT` before examining indexes. Updates form per-key chains, and visibility code interprets transaction ids, timestamps, durable timestamps, and prepare states. Reconciliation records replacement blocks in `WT_PAGE_MODIFY` as either one address/disk image or multiple `WT_MULTI` entries with unresolved saved updates.

## State And Persistence Behavior
`WT_PAGE_HEADER` is an on-disk format with fixed size, page type, flags, version, recno, write generation, memory size, and entry/data counts. HS format constants define table keys as btree id, key, start timestamp, and counter, and values as stop durable timestamp, durable timestamp, update type, and value. In-memory state includes dirty bytes, update bytes, newest commit timestamp, rec max transaction/timestamp, checkpoint cleanup state, instantiated fast-truncate updates, read generations, cache create/evict pass generations, and disaggregated page metadata. Update and page-delete prepare states require strict memory ordering.

## Dependencies And Integration Points
This header is included across btree search, cursor, reconciliation, eviction, checkpoint, history-store, rollback-to-stable, verify, block manager, and disaggregated storage code. `evict_walk.c` depends on read flags, `WT_REF`, `WT_PAGE`, `WT_PAGE_MODIFY`, read generation constants, and update-candidate state. `hs_cursor.c` depends on HS formats, `WT_UPDATE`, `WT_UPDATE_VALUE`, and update vectors. `block.h` relies on `WT_PAGE_HEADER_SIZE` and page block metadata.

## Risks
The highest risks are ABI/disk-format drift, unsafe direct access to obscured volatile fields, missing generation protection while reading internal indexes, incorrect ref-state transitions, prepare-state memory ordering bugs, dangling fast-truncate `page_del` state, update-chain memory accounting mistakes, and failure to preserve previous reconciliation choices via `WT_UPDATE_SELECT_FOR_DS`. Many fields are deliberately shared and approximate; callers must know which values are advisory and which require locks.

## Test Signals
Use static size/layout assertions, endian page-header tests, ref-state transition stress with hazard pointers, split-generation concurrency tests, prepared transaction visibility tests, fast-truncate instantiate/commit/rollback tests, reconciliation with single and multi-block replacements, HS restore tests, update-vector growth tests, eviction read-generation tests, disaggregated delta metadata tests, and sanitizer runs for update/insert memory ownership.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree.h -->
# sources/storage-engines/wiredtiger/src/include/btree.h

## Purpose
This header defines the btree handle and high-level btree configuration/state. It connects logical table properties, page sizing, reconciliation settings, compression/encryption, checkpointing, eviction walk state, cache accounting, block-manager integration, disaggregated storage state, and btree flags.

## Important APIs, Types, And Functions
The file defines version constants, page/object size limits, normalized-position constants used by eviction, `WT_BTREE_TYPE`, `WT_BTREE_SYNC`, `WT_BTREE_CHECKSUM`, `WT_EVICT_WALK_TYPE`, btree id namespace helpers, fixed shared table ids, the `WT_BTREE` struct, sync safety macros, clean-checkpoint timer macros, btree flags, `WT_SALVAGE_COOKIE`, page-delta enablement macros, and merge-state structs for applying leaf deltas to base images.

## Control Flow
The header is declarative, but `WT_BTREE` fields drive major flows. Search and reconciliation use type, key/value formats, collator, split settings, compression/encryption, max page sizes, and root ref. Checkpoint flows use `ckpt`, `checkpoint_gen`, `syncing`, clean checkpoint timers, write generations, and rec max transaction/timestamp. Eviction uses the tail fields after `WT_BTREE_CLEAR_SIZE`: current walk ref, soft normalized position, walk direction, progress/target/period, disabled/busy counters, and priority. Disaggregated flows use fixed shared ids, page log, next page id, reconciliation LSN, storage tier, and delta enablement.

## State And Persistence Behavior
Btree id and namespace values are persistent identity for local, shared, and special shared tables. Page size limits and checksum/compression/encryption settings shape on-disk page images. `write_gen`, `base_write_gen`, and checkpoint state track durable evolution. `file_max` currently bounds history-store size. Eviction fields are runtime-only and explicitly placed after `WT_BTREE_CLEAR_SIZE` so handle reset can preserve only the intended prefix. Disaggregated special ids are explicitly compatibility-sensitive.

## Dependencies And Integration Points
`WT_BTREE` embeds a root `WT_REF` from `btmem.h`, points to `WT_BM` from `block.h`, and references checkpoint, compressor, encryptor, bucket storage, page log, data handle, collator, and storage-tier types. It is used by almost every btree subsystem: cursor search, reconciliation, eviction, checkpoint, salvage, verify, history store, rollback, tiered/disaggregated storage, and cache accounting.

## Risks
Changing persistent ids, version bounds, page size limits, or flag values can break compatibility. The btree struct has mixed protected and shared fields; incorrect atomic/lock usage can corrupt cache accounting or sync/eviction coordination. Eviction state is owned by eviction, not generic btree code, so unrelated reset paths must respect `WT_BTREE_CLEAR_SIZE`. Disaggregated delta enablement must match page type and connection configuration.

## Test Signals
Test open/upgrade version bounds, special shared id stability, checksum/compression/encryption configurations, page-size validation, checkpoint sync state transitions, clean checkpoint timer behavior, eviction walk state reset/restore, btree eviction-disabled paths, cache byte accounting, history-store `file_max`, disaggregated page id/LSN allocation, and delta merge behavior for base plus leaf/internal deltas.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree.h -->
