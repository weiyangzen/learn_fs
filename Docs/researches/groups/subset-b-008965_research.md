# subset-b-008965 research

Grouped research for WiredTiger btree row search, cache, call logging, and checkpoint support files. Each source file has a source-path title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/row_srch.c -->
# sources/storage-engines/wiredtiger/src/btree/row_srch.c

## Purpose

Implements row-store key search for WiredTiger btrees. It positions a `WT_CURSOR_BTREE` on the matching row-store key, the closest on-page key, or the appropriate update skiplist insertion point. The file is performance critical for reads and writes because ordinary cursor search, insert, append-like inserts, and page-instantiation paths all pass through this logic.

## Important APIs, Types, And Functions

`__wt_row_search` is the exported tree/leaf search routine. It accepts a cursor, search key, insert-mode flag, optional known leaf `WT_REF`, and leaf-safety flags, then fills cursor fields such as `ref`, `slot`, `ins_head`, `ins`, `compare`, `tmp`, and `WT_CBT_SEARCH_SMALLEST`.

`__wt_search_insert` searches a row-store insert skiplist and builds `cbt->ins_stack` and `cbt->next_stack` for later serialized insertion. `__search_insert_append` is an append fast path for insert lists, using the tail pointers to avoid a full skiplist walk when the new key is at or beyond the current last inserted key. `__validate_next_stack` is a diagnostic-only checker for skiplist search-stack ordering under `WT_CONN_DEBUG_STRESS_SKIPLIST`. `__check_leaf_key_range` validates that an optional leaf reference still covers the target key by comparing against the parent page index boundary keys.

The code depends on `WT_BTREE`, `WT_PAGE`, `WT_PAGE_INDEX`, `WT_REF`, `WT_ROW`, `WT_INSERT_HEAD`, `WT_INSERT`, `WT_ITEM`, `WT_COLLATOR`, cursor flags, row-page macros, and comparison helpers such as `__wt_compare`, `__wt_compare_skip`, `__wt_lex_compare_short`, and `__wt_lex_compare_skip`.

## Control Flow

When a caller supplies a leaf, `__wt_row_search` optionally checks the parent boundary keys, marks whether the leaf was found, and searches only that page. Otherwise it starts at `btree->root` and descends internal row pages. Each internal page search special-cases index 0 because reconciliation may store a non-application sentinel key there. The search uses three binary-search loops: no collator/short key, no collator/long key with skipped matching prefixes, and custom collator. Append-mode insertion first compares against the rightmost internal key and can descend directly to the rightmost child.

After choosing a child, the function handles split races with `__wt_split_descent_race` and `__wt_page_swap`; `WT_RESTART` releases the current page and restarts from the root. On the leaf, it performs the same three-way binary search over the row array. An exact row-array hit returns quickly. Otherwise it maps the search position to the smallest-key insert list or the insert list attached to the previous row slot, optionally tries the append insert-list path, and finally calls `__wt_search_insert`.

## State And Persistence Behavior

This file does not persist bytes itself; it constructs in-memory cursor position and insertion state over persisted row-page images and in-memory update skiplists. It may acquire and transfer page references into `cbt->ref`, release pages during restart/error handling, set append-history state (`cbt->append_tree`), and update `btree->maximum_depth`. Insert-list searches prepare stack pointers consumed by later update insertion code, so cursor state produced here directly affects durable logical updates written elsewhere.

## Dependencies And Integration Points

The implementation integrates with page management (`__wt_page_swap`, `__wt_page_release`), split detection, row-key decoding (`__wt_row_leaf_key`, `__wt_ref_key`), collation, skiplist update insertion, diagnostic flags, eviction read hints (`WT_CBT_READ_ONCE` to `WT_READ_WONT_NEED`), and caller-side cursor semantics expecting `cbt->tmp` to contain the exact found insert key on skiplist matches.

## Risks

The largest correctness risk is concurrent skiplist mutation. The code deliberately uses acquire barriers and single-read patterns so weakly ordered CPUs do not observe a higher-level skiplist insertion without the required lower-level insertion. Prefix-skip comparison is also subtle: it must reset per page and use safe match lengths or concurrent splits/inserts can cause wrong positioning. Internal-page slot 0 must never be passed to a collator. Split-race restarts must not leak or double-release page references. A wrong `compare` sign or `slot` choice would corrupt cursor positioning and insert placement.

## Test Signals

High-signal tests are row-store cursor search/insert/remove workloads with custom collators, long common-prefix keys, small keys, empty pages, smallest-key inserts, repeated append inserts, and concurrent insert/search stress on ARM or TSAN. The built-in diagnostic signal is `WT_CONN_DEBUG_STRESS_SKIPLIST`, which enables `__validate_next_stack`. Split-heavy workloads and tests that force `WT_RESTART` from `__wt_page_swap` are important for restart cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/btree/row_srch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cache/cache.c -->
# sources/storage-engines/wiredtiger/src/cache/cache.c

## Purpose

Owns top-level WiredTiger cache lifecycle and statistics plumbing. It creates `WT_CACHE`, applies cache configuration, initializes disaggregated standby shared-disk cache state when needed, publishes cache statistics, and verifies cache shutdown invariants.

## Important APIs, Types, And Functions

`__wt_cache_config` handles initial configuration and reconfiguration for `cache_size`, `cache_overhead`, and shared-cache transitions. `__wt_cache_create` allocates `conn->cache`, delegates common config, conditionally initializes `cache->shared_dsk_cache`, and populates initial stats. `__wt_cache_stats_update` snapshots many cache counters into connection statistics, including bytes in use, dirty bytes, image bytes, internal/leaf bytes, history-store bytes, page counts, eviction controls, and reconciliation maxima. `__wt_cache_destroy` checks that cache memory and dirty state have drained, destroys shared disk cache if present, and frees `conn->cache`.

The file centers on `WT_CONNECTION_IMPL`, `WT_CACHE`, connection stats arrays, disaggregated role config, shared cache flags, and the shared disk cache APIs in `shared_dsk.c`.

## Control Flow

Configuration first detects whether `shared_cache.name` is set and whether the connection was previously in a cache pool. Reconfiguring away from a shared cache temporarily marks `WT_CONN_RECONFIGURING_CACHE_POOL` and destroys the pool membership. Reconfiguring into a shared cache clears `conn->cache_size` so the pool can manage it. Non-shared mode reads `cache_size`; both modes set `cache->overhead_pct`.

Creation allocates cache memory before configuration because subsequent paths expect `conn->cache`. For disaggregated page-log standby nodes, it reads the role from config and initializes the shared disk cache only when not leader, then marks the disk cache active. Stats update computes aggregate values from atomics, derives leaf bytes defensively from total minus internal bytes, writes stat fields, and then calls eviction stats update. Destruction checks page, image, byte, and dirty counters, logs errors if shutdown is not clean, destroys shared disk cache if allocated, and frees the cache.

## State And Persistence Behavior

This file manages in-memory cache state, not persistent data files. Its settings determine cache capacity and overhead accounting for all page residency and eviction. For disaggregated standby, it creates a cross-checkpoint disk-image cache that can retain page images read from storage while the process runs. Destruction is an integrity check that all cached and dirty pages have already been reconciled, evicted, or otherwise released before connection teardown.

## Dependencies And Integration Points

Integrates with config parsing, cache pool management (`__wt_cache_pool_destroy`), disaggregated configuration, shared disk cache init/destroy, stat macros, atomic cache accounting helpers, eviction stat update, and reconciliation timing fields on the connection. Shared cache creation itself lives in `cache_pool.c`; this file coordinates the cache-size side of entering/leaving that mode.

## Risks

Reconfiguration must keep shared-cache flags consistent even when errors occur; the error path clears `WT_CONN_RECONFIGURING_CACHE_POOL`. Stats are race-tolerant but can momentarily see inconsistent counters, so derived leaf values must avoid underflow. Disaggregated shared disk cache initialization depends on config before metadata/recovery is available, which the source notes as a temporary dependency workaround. Shutdown warnings indicate leaks or dirty state that can imply earlier eviction/checkpoint failures.

## Test Signals

Useful signals include configuration tests for `cache_size`, `cache_overhead`, and shared-cache transitions; disaggregated standby startup verifying `cache_shared_dsk_hash_size` and active state; stat tests checking non-underflow and expected counter publication; and teardown tests that close clean connections without cache leak messages. Stress tests should combine eviction, history store, ingest/stable accounting, and reconfigure paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cache/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cache/cache_pool.c -->
# sources/storage-engines/wiredtiger/src/cache/cache_pool.c

## Purpose

Implements the process-wide shared cache pool. Multiple WiredTiger connections in the same process can join a named pool, receive reserved/quota-based cache allocations, and have a manager thread rebalance `conn->cache_size` based on pressure and total pool capacity.

## Important APIs, Types, And Functions

Public entry points are `__wt_cache_pool_create` and `__wt_cache_pool_destroy`. Internal support includes `__cache_pool_config` for parsing/validating shared cache settings, `__conn_cache_pool_open` for joining the pool and starting a manager thread, `__cache_pool_server` as the per-connection manager thread loop, `__cache_pool_balance` as the locked rebalance pass, `__cache_pool_assess` for pressure scoring, and `__cache_pool_adjust` for growing/shrinking allocations.

The main state lives in global `__wt_process.cache_pool` (`WT_CACHE_POOL`), its spin locks/condition variable/refcount/connection queue, and per-connection cache fields such as `cp_reserved`, `cp_quota`, `cp_pass_pressure`, saved read/eviction counters, skip count, manager/run flags, `cp_session`, and `cp_tid`.

## Control Flow

Configuration rejects a shared-cache size without a name and rejects using both `cache_size` and `shared_cache`. It creates the singleton pool under the process spinlock or validates the requested name against the existing pool. It then locks the pool, increments refs for new joiners, resolves size/chunk/quota/reserve values from config or existing state, validates that all reserved allocations fit within pool size, stores pool/connection settings, and marks `WT_CONN_CACHE_POOL`.

Joining opens an internal no-data-handles session, inserts the connection into the pool queue, marks the pool active, sets the connection run flag, starts the manager thread, and signals for an initial allocation. Each manager thread loops while the pool and connection run flag are active. A CAS elects one active manager via `pool_managed`; that manager alternates forward/backward balancing passes.

Balancing first assesses pressure from bytes read, application eviction count, and application wait count, weighted by constants and cache size. Adjustment ensures each connection reaches its reserve, shrinks low-pressure or idle participants when the pool is full, and grows pressured participants when there is capacity and quota allows. Skip counters dampen oscillation after changes.

Destroying clears the connection cache-pool flag, removes the connection from the queue if present, returns its allocation to `currently_used`, stops and joins its manager thread, closes its internal session, decrements refs, and frees the singleton pool when the last participant exits.

## State And Persistence Behavior

The pool is process-local runtime state and does not persist across process restart. It mutates each participating connection's `cache_size`, which directly controls eviction thresholds and memory residency. Reserved and quota settings survive only as connection/cache fields. Destroy returns pool capacity and frees shared synchronization primitives after the last reference.

## Dependencies And Integration Points

This file integrates with WiredTiger global process state, config parsing, internal sessions, thread creation/join, condition variables, spin locks, eviction pressure helpers (`__wt_evict_needed` and `WT_EVICT` counters), cache byte accounting, verbose shared-cache logging, and `__wt_cache_config`, which decides whether the connection should enter or leave shared mode.

## Risks

Lock ordering is delicate: the process lock is dropped before acquiring the pool lock and reacquired in a documented order to avoid deadlock. Refcounts cover races between open/config and destroy. Rebalancing writes `entry->cache_size` while application/eviction threads read it, so allocation changes must be gradual and bounded. `cp_quota == 0` means unlimited for eligibility, but adjustment uses `cache->cp_quota - entry->cache_size`; implementations must preserve the intended zero-quota behavior. Error handling during partial pool creation or failed open must not leak the singleton, condition variable, or refcount.

## Test Signals

Signals include configuration validation errors for missing names, mixed `cache_size`/shared config, and reserve oversubscription; multi-connection tests showing initial reserve allocation, growth under read/eviction pressure, shrink when over budget, and quota enforcement; shutdown/reconfigure tests proving manager election handoff and clean singleton destruction; and stress tests around concurrent open/close/reconfigure with shared cache verbose logging enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cache/cache_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cache/shared_dsk.c -->
# sources/storage-engines/wiredtiger/src/cache/shared_dsk.c

## Purpose

Implements the shared disk-image cache used by disaggregated standby nodes to share immutable page disk images across checkpoints. It hashes disk addresses plus file IDs to cache entries, reference-counts shared images, updates cache/image accounting, and frees images when no page references remain.

## Important APIs, Types, And Functions

`__wt_shared_dsk_cache_get` looks up an address and file ID, increments the entry refcount on hit, and returns a `WT_SHARED_DSK_ITEM`. `__wt_shared_dsk_cache_put` inserts a disk image or detects a collision with an existing entry; on insert, ownership of the caller's `data` moves to the cache, while on collision/error the caller retains ownership. `__wt_shared_dsk_cache_release` decrements refcount and removes/frees the entry on last release. `__wt_shared_dsk_cache_init` allocates hash buckets and bucket-lock array. `__wti_shared_dsk_cache_destroy` frees all buckets, images, and locks. `__shared_dsk_cache_verbose` formats address-level verbose logs.

The file uses `WT_SHARED_DSK_CACHE`, `WT_SHARED_DSK_ITEM`, `WT_PAGE_BLOCK_META`, `WT_PAGE_HEADER`, per-bucket TAILQs, spin locks, file ID `S2BT(session)->id`, CityHash, and cache statistic/accounting helpers.

## Control Flow

Get computes `hash = city64(addr)`, maps it to `bucket` and `lock_idx`, locks that stripe, scans the bucket for same address size, file ID, and bytes, increments `ref_count` if found, unlocks, and records hit/miss stats. Put preallocates and fills a wrapper with data pointer, data size, copied block metadata, file ID, address bytes, and refcount 1 before taking the bucket lock. Under lock it scans for an existing item; on collision it increments the existing item refcount, returns it, and frees only the unused wrapper. If no collision exists, it inserts the wrapper at the bucket head, transfers data ownership, and increments shared-disk and image cache accounting.

Release recomputes the bucket from the stored address, decrements refcount under the lock, and either leaves the item in place or removes it. The last-release path updates accounting after unlocking, overwrites/frees the disk image bytes, and frees the wrapper. Init sizes the lock array to `min(hash_size, 2000)`, initializes all queues and locks, and publishes hash-size stats. Destroy walks every bucket and frees remaining items without requiring refcount-zero.

## State And Persistence Behavior

The cache stores in-memory copies of disk page images and block metadata; it does not persist new data. Keys are physical disk addresses scoped by btree file ID, so entries represent immutable storage content. Refcounts model sharing by page instances. Cache byte/image counters are updated symmetrically on insert and final release, making this cache visible to broader eviction and cache accounting.

## Dependencies And Integration Points

Initialized from `__wt_cache_create` for disaggregated standby roles and destroyed from `__wt_cache_destroy`. The code integrates with page read/reconciliation paths that can attach shared disk items to pages, the cache accounting layer (`__wt_cache_shared_dsk_inmem_incr`, `__wt_evict_shared_dsk_cache_bytes_decr`, `__wt_cache_image_incr/decr`), connection stats, verbose cross-checkpoint-cache logging, and diagnostic counters for max bucket walk/refcount.

## Risks

Ownership transfer in `put` is easy to misuse: callers must free their data only when `insertedp` is false or an error occurs. `addr_size` is stored in a `uint8_t`, so callers must respect address size bounds. Destroy frees all entries regardless of refcount, so it must only run when no pages can still reference shared items. Hash collisions are handled by full address/file comparison, but long buckets can affect performance; diagnostic max-bucket-walk counters help identify this. Accounting must remain symmetric or cache shutdown/statistics will report leaked image bytes.

## Test Signals

Useful coverage includes get-miss/get-hit behavior, duplicate put collision preserving caller ownership, refcount increment/decrement and final removal, separate entries for same address in different file IDs, statistics hit/miss/hash-size updates, image byte accounting across insert/release, destroy with populated buckets, and disaggregated standby startup/teardown with verbose cross-checkpoint cache logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cache/shared_dsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/call_log/call_log.c -->
# sources/storage-engines/wiredtiger/src/call_log/call_log.c

## Purpose

Provides optional API call logging under `HAVE_CALL_LOG` for the timestamp simulator. It records selected connection/session timestamp and transaction API calls as JSON-like entries in a process-specific `wt_call_log` file so simulator tooling can replay or analyze API sequences.

## Important APIs, Types, And Functions

Lifecycle functions are `__wt_conn_call_log_setup` and `__wt_conn_call_log_teardown`. Shared formatting helpers are `__call_log_print_start`, `__call_log_print_input`, `__call_log_print_output`, and exported `__wt_call_log_print_return`. API-specific loggers include `__wt_call_log_open_session`, `__wt_call_log_set_timestamp`, `__wt_call_log_query_timestamp`, `__wt_call_log_begin_transaction`, `__wt_call_log_prepare_transaction`, `__wt_call_log_commit_transaction`, `__wt_call_log_rollback_transaction`, `__wt_call_log_timestamp_transaction`, `__wt_call_log_timestamp_transaction_uint`, `__wt_call_log_prepared_id_transaction`, `__wt_call_log_prepared_id_transaction_uint`, and `__wt_call_log_close_session`.

The file uses `WT_CONNECTION_IMPL::call_log_fst`, `WT_CONN_CALL_LOG_ENABLED`, session/connection pointer values as IDs, `WT_TS_TXN_TYPE`, WiredTiger file-system stream APIs, and variadic formatting helpers.

## Control Flow

Setup skips readonly connections, builds a filename containing the process ID, opens it for append/create, and sets the enabled flag. Every logger first checks the enabled flag, prints a class/method header, prints a connection or session ID when needed, prints an input object from preformatted JSON fragments, prints an output object, and finally writes a return object with return value and error string. Query timestamp logs output only on successful API return to avoid recording garbage. `timestamp_transaction_uint` maps `WT_TS_TXN_TYPE_*` enum values to symbolic strings. Teardown closes the file stream when enabled.

## State And Persistence Behavior

The persistent artifact is an append-only call-log file in the connection home context. It is not WiredTiger database state and is not intended for recovery. The file stores pointer values as session/connection identifiers for simulator mapping, configuration strings copied from API calls, timestamp/prepared-id values, return codes, and optional error strings. Close-session logging intentionally has no return section in this file, unlike most other entries.

## Dependencies And Integration Points

Integrated into public API paths through conditional call-log hooks and compiled only when `HAVE_CALL_LOG` is defined. It depends on WiredTiger scratch buffers, filename construction, filesystem open/close, formatted stream output, connection flags, and simulator-side expectations for `class_name`, `method_name`, `session_id`, `connection_id`, `input`, `output`, and `return` fields.

## Risks

The output is assembled with fixed 128-byte buffers for config fragments, so long config strings can fail formatting or truncate depending on `__wt_snprintf` semantics. Raw config strings are inserted into JSON without escaping, so embedded quotes or control characters can produce invalid JSON. There is no explicit synchronization around writes; concurrent API calls may interleave unless higher layers serialize or the stream implementation protects writes. Pointer IDs are process-local and not stable across runs. The close-session entry omits a return block, which consumers must tolerate.

## Test Signals

Tests should compile with `HAVE_CALL_LOG`, verify readonly setup does not create/enable logging, exercise each API logger, parse or pattern-check emitted entries, validate query timestamp omits output on failure, confirm enum-to-string mapping for timestamp types, and stress concurrent sessions for malformed/interleaved records. Simulator tests under `test/simulator/timestamp/call_log_manager` are a natural integration signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/call_log/call_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint.h -->
# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint.h

## Purpose

Defines the public internal checkpoint data structures and prototypes shared across WiredTiger checkpoint implementation files. It captures per-session checkpoint work state, connection-wide checkpoint server/stat state, checkpoint metadata records, snapshot metadata, cleanup thread state, and parallel page-reconciliation queues.

## Important APIs, Types, And Functions

`WT_CKPT_SESSION` tracks checkpoint cursor write generation, handle lists, crash-test points, named-checkpoint drop list, current checkpoint time, and size delta. `WT_CKPT_CONNECTION` holds handle stats, checkpoint server state, timer stats, reconciliation/sync accumulators, most recent checkpoint time, progress counters, and previous base write generation. `WT_CKPT_BLOCK_MODS` records incremental backup block-modification bitstrings. `WT_CKPT` is the central checkpoint descriptor with name, order, wall-clock time, size, write generations, block metadata/checkpoint cookies, backup block-mod entries, time aggregate, address/raw cookie buffers, next page ID, block-manager private state, and checkpoint flags.

`WT_CKPT_SNAPSHOT` preserves checkpoint ID, oldest/stable timestamps, write generation, transaction snapshot range/list/count. `WT_CHECKPOINT_CLEANUP` models the cleanup thread. `WT_CHECKPOINT_PAGE_TO_RECONCILE` is a parallel reconcile work item. `WT_CHECKPOINT_RECONCILE_THREADS` contains the thread group, work/done queues, synchronization primitives, and private snapshot buffer for checkpoint workers. Macros expose checkpoint iteration and parallel-checkpoint status/thread count. Prototypes export checkpoint lifecycle, server, parallel reconciliation, stats, snapshot, and ckpt-list helpers.

## Control Flow

The header itself has no executable control flow, but it defines the state passed through checkpoint phases: checkpoint setup populates `WT_CKPT_SESSION` and `WT_CKPT_CONNECTION`; metadata and btree/block layers exchange `WT_CKPT`; transaction code fills `WT_CKPT_SNAPSHOT`; sync/reconciliation queues use `WT_CHECKPOINT_PAGE_TO_RECONCILE`; cleanup and server code consume `WT_CHECKPOINT_CLEANUP` and `WTI_CKPT_THREAD`. Parallel checkpoint macros gate whether btree sync pushes page work to helper threads or uses the single-threaded path.

## State And Persistence Behavior

Several fields represent durable checkpoint metadata: names, order, checkpoint cookies, block metadata, block modification bitstrings, time aggregates, write generations, and snapshot timestamps. Other fields are transient runtime state: handle arrays, crash testing controls, cleanup thread handles, progress counters, private worker snapshots, and queue entries. `ckpt_size_delta` is explicitly accumulated during a checkpoint and applied to connection-level database size only after success.

## Dependencies And Integration Points

Includes `checkpoint_private.h` for private enums/stats/thread/timer types. The prototypes link this header to transaction checkpoint code, metadata, btree sync/reconciliation, block manager, checkpoint server, checkpoint cleanup, stats publishing, and unit tests. Many structures are also consumed by generated prototype machinery, so field/name changes cascade through internal checkpoint modules.

## Risks

These structures are cross-module contracts; changing flags, snapshot ownership, queue fields, or checkpoint metadata buffers can break metadata parsing, incremental backup, recovery, or parallel reconciliation. The `WT_CKPT_FOREACH` macro stops on `name == NULL`, while the private macro in `checkpoint_private.h` also considers `order`, so callers must choose the correct iterator for partially named checkpoints. Worker snapshot buffers must remain valid while helper threads run.

## Test Signals

Signals come from checkpoint/recovery tests, named checkpoint tests, incremental backup tests, timestamped checkpoint visibility tests, parallel checkpoint tests with `checkpoint_threads > 1`, crash-test configurations using checkpoint crash points, and unit tests behind `HAVE_UNITTEST` such as checkpoint-list skipping helpers. ABI-like internal consistency is also checked by generated prototype builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_ckptlist.c -->
# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_ckptlist.c

## Purpose

Owns cleanup of checkpoint-list memory. It frees arrays of `WT_CKPT` descriptors, clears saved btree checkpoint lists, and frees all heap-owned fields inside an individual checkpoint descriptor so the object can be reused or discarded safely.

## Important APIs, Types, And Functions

`__wt_ckptlist_free` frees a NULL-terminated checkpoint array using `WTI_CKPT_FOREACH_NAME_OR_ORDER`, which includes entries that may not yet have a name but do have an order. `__wt_ckptlist_saved_free` frees `S2BT(session)->ckpt` and resets `btree->ckpt_bytes_allocated`. `__wt_checkpoint_free` releases one `WT_CKPT`, including strings, buffers, block-manager private pointer, and incremental backup block-modification entries.

The code manipulates `WT_CKPT`, `WT_CKPT_BLOCK_MODS`, `WT_BTREE::ckpt`, and `WT_BLKINCR_MAX` block-mod slots.

## Control Flow

The list-free path returns immediately for a NULL base pointer. Otherwise it iterates every name-or-order entry, calls the single-checkpoint free helper, and frees the array pointer. The saved-list helper delegates to the generic list free routine and resets btree allocation accounting. The single-checkpoint free routine handles NULL input, frees all scalar-owned allocations, loops over every incremental backup block-mod entry to free bitstrings and IDs and clear validity, then `WT_CLEAR`s the whole descriptor.

## State And Persistence Behavior

This file only frees in-memory representations of checkpoint metadata that was read from or prepared for persistent metadata. It does not update metadata itself. Clearing `WT_CKPT` prevents stale checkpoint names, cookies, block metadata, or backup bitstrings from being reused after free. Resetting `ckpt_bytes_allocated` keeps btree memory accounting aligned after saved checkpoint lists are discarded.

## Dependencies And Integration Points

Used by checkpoint metadata parsing, btree handle cleanup, checkpoint close/reopen paths, and error handling that abandons checkpoint arrays. It depends on memory/buffer helpers and on the private iterator macro to handle not-yet-named checkpoints created during checkpoint assembly.

## Risks

Using the public `WT_CKPT_FOREACH` here would leak unnamed ordered checkpoints. Missing any owned field in `__wt_checkpoint_free` would leak memory or retain stale incremental-backup state. Clearing the descriptor after free is useful for reuse but means callers must not expect any field to survive. Destroying `bpriv` here assumes the block-manager private object is heap-owned by the checkpoint descriptor.

## Test Signals

Memory sanitizer/ASAN leak checks around checkpoint metadata load/drop, named checkpoint creation/drop, incremental backup metadata, and failed checkpoint assembly are the best signals. Unit tests should include a checkpoint list with an ordered but unnamed entry to verify the private iterator path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_ckptlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_conn.c -->
# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_conn.c

## Purpose

Implements the connection-level checkpoint server. It parses checkpoint scheduling configuration, starts/stops the background checkpoint thread, runs periodic or log-size-triggered checkpoints, and exposes a signal path for log writers to wake the server.

## Important APIs, Types, And Functions

`__wt_checkpoint_server_create` configures and starts the server, destroying any existing server first during reconfigure. `__wt_checkpoint_server_destroy` stops the thread, joins it, destroys its condition variable, closes its internal session, and clears server fields. `__wt_checkpoint_signal` wakes the server when enough log bytes have been written. Internal helpers are `__ckpt_server_config`, `__ckpt_server_run_chk`, `__ckpt_server`, and `__ckpt_server_start`.

State lives in `WT_CONNECTION_IMPL::ckpt.server` (`WTI_CKPT_THREAD`), `conn->server_flags`, log manager flags and file size, and the checkpoint generation counter.

## Control Flow

Configuration reads `checkpoint.wait` into microseconds and `checkpoint.log_size` into an atomic logsize field. If either wait is nonzero or log-size checkpointing is enabled with logging, it validates that the connection is not in-memory, raises log-size to at least the log file maximum when needed, resets log-written counters, and requests server start. Start sets `WT_CONN_SERVER_CHECKPOINT`, opens an internal checkpoint-server session with wait capability, allocates a condition variable, creates the thread, and marks `tid_set`.

The server thread waits on the condition variable for the configured interval or explicit signal. After wakeup it exits if the server flag was cleared, otherwise records the current checkpoint generation and calls `WT_SESSION::checkpoint`. If a real checkpoint advanced the generation and log-size scheduling is active, it resets log-written counters, clears the signalled flag, and performs a one-microsecond wait to drain a stale signal so it does not immediately checkpoint again.

Destroy clears the server flag, signals and joins the thread if running, destroys synchronization state, closes the internal session, and zeroes scheduling fields. `__wt_checkpoint_signal` compares the supplied log byte count against the configured threshold and signals only once until the server resets `signalled`.

## State And Persistence Behavior

The server itself is transient, but it triggers durable checkpoints through the normal session checkpoint API. Its persistent effect is indirect: periodic or log-size-triggered metadata, btree, block-manager, and log checkpoint state written by the checkpoint transaction machinery. Runtime scheduling state includes interval, log-size threshold, signal coalescing, thread/session/condition handles, and the server flag.

## Dependencies And Integration Points

Depends on config parsing, the log subsystem (`WT_LOG_ENABLED`, `conn->log_mgr.file_max`, `__wt_log_written_reset`), internal sessions, condition variables, thread APIs, connection server flags, checkpoint generation, public session checkpoint API, and panic handling. It is invoked during connection open and reconfigure and is signaled by log-writing paths.

## Risks

Reconfigure intentionally bounces the server to avoid racing live config reads; failure to destroy cleanly would leave stale sessions or condvars. Log-size checkpointing is valid only when logging is enabled and uses a minimum of log file size to avoid too-frequent checkpoints. In-memory configuration is incompatible and must fail early. Signal coalescing through `signalled` is not atomic; it relies on server/log scheduling assumptions and can skip redundant signals, so tests should watch for missed log-size checkpoints.

## Test Signals

Coverage should include wait-based checkpoints, log-size-triggered checkpoints with logging, no server when both wait/log-size are zero, in-memory incompatibility errors, reconfigure stop/start, clean shutdown with no leaked internal session, and log-written reset only after a non-skipped checkpoint advances `WT_GEN_CHECKPOINT`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_parallel.c -->
# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_parallel.c

## Purpose

Implements helper-thread infrastructure for parallel page reconciliation during checkpoints. When `checkpoint_threads` is greater than one, btree sync can push dirty page refs to a worker queue while the main checkpoint thread later drains results, releases page references, and commits/releases worker transactions in checkpoint phase order.

## Important APIs, Types, And Functions

Public functions are `__wt_checkpoint_parallel_thread_create`, `__wt_checkpoint_parallel_thread_destroy`, `__wt_checkpoint_parallel_push_work`, `__wt_checkpoint_parallel_finish`, `__wti_checkpoint_parallel_release_snapshot`, and `__wti_checkpoint_parallel_commit`. Internal queue/thread helpers include `__checkpoint_parallel_pop_work`, `__checkpoint_parallel_push_done`, `__checkpoint_parallel_pop_done`, queue-empty checks, `__checkpoint_parallel_thread_run`, `__checkpoint_parallel_thread_stop`, `__checkpoint_parallel_thread_release_snapshot`, and `__checkpoint_parallel_thread_commit`.

The core types are `WT_CHECKPOINT_RECONCILE_THREADS` and `WT_CHECKPOINT_PAGE_TO_RECONCILE`, with a `WT_THREAD_GROUP`, work/done TAILQs, spin locks, condition variable, done semaphore, work counter, and a private checkpoint transaction snapshot shared by all worker sessions.

## Control Flow

Thread creation stores the connection's reconcile-thread structure, reads `checkpoint_threads`, disables parallel mode for one thread, otherwise sets the server flag, initializes queues/locks/condition/semaphore, and creates a fixed-size thread group. Pushing work allocates an entry containing the current data handle, isolation level, checkpoint snapshot pointer, page ref, reconcile flags, and release flags, then queues it under `work_lock`, increments `work_pushed`, and signals workers.

Each worker marks its session as checkpoint/checkpoint-worker, waits for work, loops over available entries, begins a transaction if needed, imports the private checkpoint snapshot, restores isolation, reconciles the page under the entry's data handle, records elapsed reconciliation ticks, increments success stats, stores the result, and posts the entry to the done queue. On error it logs and stops processing.

Finish loads the number of pushed work items, waits on the done semaphore until all are popped, accumulates result and page-release errors with `WT_TRET`, releases each page ref using the stored flags, sums reconcile time, frees entries, asserts both queues are empty, and resets `work_pushed`. Snapshot release and commit functions run callbacks across the thread group after all work is empty. Destroy clears the server flag, signals workers, finishes outstanding done entries, destroys the thread group and synchronization primitives, and frees the private snapshot buffer.

## State And Persistence Behavior

The file manages transient checkpoint worker state. Persistent effects occur through `__wt_reconcile`, which writes checkpoint page images and block state. Worker transactions and imported snapshots ensure all parallel page reconciliations see the same checkpoint-consistent transaction view as the main checkpoint. The main thread remains responsible for committing or rolling back worker transactions and releasing snapshots in the correct checkpoint phase.

## Dependencies And Integration Points

Integrated with btree sync (`bt_sync.c`) for pushing work and collecting reconciliation time, transaction snapshot import/release/commit, data-handle switching via `WT_WITH_DHANDLE`, page release semantics, thread group infrastructure, semaphores, condition variables, checkpoint stats, and checkpoint macros from `checkpoint.h`. It also depends on the checkpoint prepare path having populated `checkpoint_snapshot`.

## Risks

The work counter must match queued entries; otherwise finish can wait forever or assert queue corruption. Page references must be released exactly once by the main thread after worker reconciliation. Worker transactions must not survive thread-group stop, enforced by assertions and panic. Snapshot buffers must remain valid until all worker sessions have released snapshots. Error propagation is intentionally aggregated, but destroy suppresses finish errors after warning, so shutdown paths can hide prior reconcile failures. Queue-empty assertions catch phase-order violations when release/commit is called before all work is done.

## Test Signals

High-signal tests set `checkpoint_threads > 1` and generate many dirty pages across handles, then verify successful checkpoints, reopened data, and `checkpoint_parallel_pages_reconciled` increments. Fault-injection tests should force reconcile errors and page-release errors, verify finish returns errors, and ensure destroy still frees resources. Race tests should exercise shutdown/reconfigure with workers waiting, and phase assertions should be covered by diagnostics builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_parallel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_private.h -->
# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_private.h

## Purpose

Defines checkpoint-private constants, lifecycle-state enum, stats structs, progress structs, server-thread state, timer state, and private prototypes used by checkpoint implementation files. It is included by `checkpoint.h` but keeps details scoped to checkpoint internals.

## Important APIs, Types, And Functions

`WTI_CHECKPOINT_SESSION_FLAGS` describes internal checkpoint session capabilities. `WTI_CKPT_FOREACH_NAME_OR_ORDER` iterates checkpoint arrays that may contain unnamed but ordered entries. `WTI_CHECKPOINT_STATE` enumerates phase/progress states from inactive through metadata, btree, oldest update, sync/evict/block-manager, history-store, commit, rollback/log/tree/establish/start-transaction phases.

`WTI_CKPT_HANDLE_STATS` accumulates handle apply/drop/lock/meta-check/skip counts and durations. `WTI_CKPT_PROGRESS` tracks files checkpointed, progress message count, pages visited, write bytes, and write pages. `WTI_CKPT_THREAD` stores the checkpoint server's condition variable, session, thread id, log-size threshold, signal state, and wait interval; `WT_CKPT_LOGSIZE` reads its atomic log-size field. `WTI_CKPT_TIMER` stores min/max/recent/total timing. Private prototypes expose parallel checkpoint worker commit and snapshot-release helpers.

## Control Flow

The header has no executable flow, but its enum ordering mirrors checkpoint lifecycle sequencing for progress/state reporting. The private iterator controls cleanup flow in `checkpoint_ckptlist.c`. `WT_CKPT_LOGSIZE` controls whether log-size checkpoint signaling is active. The private parallel prototypes are called from checkpoint transaction code after queued reconciliation work is complete.

## State And Persistence Behavior

All definitions are runtime state except where they describe phases of producing durable checkpoint metadata. Handle stats, progress counters, timers, log-size signal state, and lifecycle enum values are transient observability and scheduling state. The iterator macro affects memory cleanup of checkpoint metadata descriptors that represent persistent checkpoint records.

## Dependencies And Integration Points

Consumed by `checkpoint.h`, checkpoint server code, checkpoint stats code, checkpoint transaction code, parallel reconciliation code, and checkpoint-list cleanup. The enum and stats fields must stay aligned with connection statistics and verbose/progress reporting. The prototypes form private cross-file links not intended for broader subsystems.

## Risks

Changing enum order can confuse progress/state consumers that assume lifecycle ordering. Timer minima are initialized to `UINT64_MAX` elsewhere; stats publication must preserve that convention. The private iterator's stop condition differs from public checkpoint iteration and is required to avoid leaks. Atomic log-size access must remain compatible with signal paths.

## Test Signals

Signals include compilation/prototype generation, checkpoint progress/verbose tests that observe expected state transitions, stats tests for handle/timer counters, log-size checkpoint scheduling tests through `WT_CKPT_LOGSIZE`, and checkpoint-list cleanup tests with ordered unnamed checkpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_stats.c -->
# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_stats.c

## Purpose

Publishes and maintains checkpoint-related connection statistics for handle processing, timers, reconciliation/sync ratio, and apply-versus-skip decisions. It bridges runtime fields in `WT_CKPT_CONNECTION` to stat counters visible to diagnostics and users.

## Important APIs, Types, And Functions

`__wt_checkpoint_handle_stats_clear` resets handle count/time accumulators. `__wt_checkpoint_timer_stats_clear` initializes timer minima for checkpoint API, prepare, and scrub timers. `__wt_checkpoint_handle_stats` writes handle-related stats to the connection stats array. `__wt_checkpoint_rec_time_stats` atomically accumulates per-file reconciliation and sync ticks. `__wt_checkpoint_timer_stats` publishes scrub, prepare, and overall checkpoint timer max/min/recent/total values and computes reconciliation percentage of sync time. `__wt_checkpoint_apply_or_skip_handle_stats` increments apply or skip counters based on `WT_BTREE_SKIP_CKPT`.

## Control Flow

Clear functions operate directly on `S2C(session)->ckpt`. Handle stat publication copies accumulated values plus the externally measured handle-gather duration. Reconciliation time stats use atomic adds because multiple file or helper paths can contribute. Timer publication reads timer fields atomically, publishes min only after it has been set away from `UINT64_MAX`, and computes `checkpoint_sync_rec_pct` as `reconcile_ticks * 100 / sync_ticks` when sync ticks are nonzero. Apply-or-skip checks the current btree flag and updates the corresponding count and duration.

## State And Persistence Behavior

This file does not affect persistent checkpoint contents. It maintains transient observability state for the current or recent checkpoint activity. The stats reflect handle selection and reconciliation behavior, which helps diagnose durable checkpoint latency and skipped files but is not itself stored in metadata.

## Dependencies And Integration Points

Depends on `WT_CKPT_CONNECTION` from `checkpoint.h`, private handle/timer structs from `checkpoint_private.h`, connection stat macros, atomic operations, and btree flags. It is called from checkpoint transaction and btree sync paths that measure handle gathering, per-file reconciliation/sync, checkpoint preparation, and skip/apply behavior.

## Risks

Stats can be updated from multiple paths, so non-atomic fields must only be touched in serialized checkpoint phases while shared accumulators use atomics. Timer minima require `UINT64_MAX` initialization or min publication becomes misleading. Percentage computation can overflow if reconciliation ticks are extremely large before multiplication, though normal clock deltas make that unlikely. Apply/skip stats depend on `S2BT(session)` being the handle currently evaluated.

## Test Signals

Signals include statistics tests that run checkpoints over applied and skipped handles, verify handle count/duration fields, verify timer min/max/recent/total after checkpoints, and check `checkpoint_sync_rec_pct` after reconciliation. Parallel checkpoint tests should still produce coherent aggregate reconciliation time. Diagnostics should include skipped btree handles marked with `WT_BTREE_SKIP_CKPT`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_stats.c -->
