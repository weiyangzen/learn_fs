# subset-b-008982 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/stat.h -->
## sources/storage-engines/wiredtiger/src/include/stat.h

Purpose: `stat.h` is WiredTiger's generated internal statistics contract. It defines how connection, data-source, and session counters are stored, updated, read, cleared, and bucketed, then declares the generated `WT_CONNECTION_STATS`, `WT_DSRC_STATS`, and `WT_SESSION_STATS` field layouts consumed by statistics cursors, diagnostics, and subsystem instrumentation.

Important APIs and types: the file exposes slot-count constants `WT_STAT_CONN_COUNTER_SLOTS` and `WT_STAT_DSRC_COUNTER_SLOTS`, session-to-slot macros, field-to-offset macros, statistic mode flags such as `WT_STAT_CLEAR`, `WT_STAT_JSON`, `WT_STAT_TYPE_FAST`, `WT_STAT_TYPE_SIZE`, and `WT_STAT_TYPE_TREE_WALK`, aggregation helpers `__wt_stats_aggregate_conn` and `__wt_stats_aggregate_dsrc`, clearing helpers, read/write/update macros, histogram generator macros, and the three generated stats structs.

Control flow: writers update one slot selected from the session id to reduce cache-line contention. Readers aggregate the same field offset across every slot without locking, clamp negative aggregate results to zero for external API compatibility, and can clear all slots when a set operation needs a single absolute value. The `WT_STAT_CONN_*`, `WT_STAT_DSRC_*`, and `WT_STAT_SESSION_*` families route increments, decrements, atomic updates, and set operations to the correct connection, data handle, or session storage.

State and persistence behavior: statistics are in-memory observability state, not durable storage. The generated field list is nevertheless ABI-like inside WiredTiger: field offsets are used by generic statistic cursor code, and the connection/data-source/session base values partition statistic id spaces. Data-source counters mirror per-handle state for block, cache, cursor, reconciliation, compression, and rollback-to-stable activity; connection counters include global cache, checkpoint, log, perf histogram, lock, tiered, live-restore, and transaction metrics.

Dependencies and integration points: this header depends on session, connection, data-handle, atomic, TSAN-suppression, and generated-flag infrastructure included through the broader internal header stack. It is included by nearly every subsystem that records counters. `txn_inline.h`, timestamp/time code, tiered code, eviction, reconciliation, cursor paths, block manager, live restore, log manager, and rollback-to-stable all rely on these field names compiling exactly.

Risks: aggregation is intentionally racy and can undercount, overcount, or temporarily see negative per-slot arithmetic before clamping. Non-atomic update macros use TSAN-suppressed relaxed operations and are not a correctness synchronization primitive. Adding, removing, or reordering generated fields without regenerating statistic metadata can break statistic ids and cursor output. `WT_STATP_*_SET` clears all slots before setting slot zero, so concurrent increments can be lost by design.

Test signals: compile-time generation checks from `dist/stat.py`, statistic cursor tests for id/name/value alignment, JSON and clear-mode tests, stress tests with concurrent increments/decrements, TSAN builds that confirm known suppressions are intentional, and subsystem tests that assert counters such as transaction conflicts, checkpoint activity, tiered work units, history-store reads, and perf histograms move under the expected workload.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/str_inline.h -->
## sources/storage-engines/wiredtiger/src/include/str_inline.h

Purpose: `str_inline.h` provides tiny stringification helpers for internal enum-like byte values used in diagnostics and logging.

Important APIs: `__wt_prepare_state_str` maps `WT_PREPARE_INIT`, `WT_PREPARE_INPROGRESS`, `WT_PREPARE_LOCKED`, and `WT_PREPARE_RESOLVED`; `__wt_update_type_str` maps update types including modify, reserve, standard, and tombstone; `__wt_page_type_str` maps page types including row/column internal and leaf pages, overflow, block-manager, and invalid/count sentinels.

Control flow and state: each helper is a pure switch returning a string literal and falling back to an `*_INVALID` literal. There is no mutable state, allocation, or persistence.

Dependencies and integration points: the helpers depend on prepare-state, update-type, and page-type constants declared elsewhere in WiredTiger's internal headers. They integrate with verbose messages, assertions, debugging dumps, and tests that need stable human-readable names for compact numeric state.

Risks: enum drift is the primary risk. If a new prepare state, update type, or page type is added without updating these switches, diagnostics degrade to the invalid fallback and tests that inspect text may miss a newly important state. There is no default assertion, so unknown values are tolerated.

Test signals: compile all include users after enum changes, unit or diagnostic tests that stringify every defined value, and failure-path/verbose tests that confirm invalid values produce explicit fallback text rather than undefined behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/str_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/swap.h -->
## sources/storage-engines/wiredtiger/src/include/swap.h

Purpose: `swap.h` centralizes byte-swap helpers for 16-, 32-, and 64-bit unsigned values so on-disk little/big-endian conversions and metadata encodings can use one internal spelling.

Important APIs: `__wt_bswap16`, `__wt_bswap32`, and `__wt_bswap64` are defined as compiler or platform intrinsics on MSVC, Clang, GCC, and Solaris where available, with inline bit-manipulation fallbacks otherwise.

Control flow and state: preprocessor feature detection chooses the implementation at compile time. The fallback functions are pure arithmetic transformations, have no side effects, and preserve no state.

Dependencies and integration points: the header includes `misc.h` and uses WiredTiger's `WT_INLINE` convention. It is a low-level dependency for packed disk structures, compressor/encryptor prefixes, block metadata, checksum paths, and any code that must normalize endian-specific byte order.

Risks: feature-detection branches must match compiler versions correctly. The fallback constants rely on unsigned widths and should stay warning-clean across 32/64-bit platforms. Misuse on already-swapped values is outside the helper's control and can corrupt persistent formats.

Test signals: build coverage across GCC, Clang, MSVC, and Solaris-like branches; value tests for fixed byte patterns such as `0x0102`, `0x01020304`, and `0x0102030405060708`; and endian-sensitive recovery/format tests that read files produced on the opposite endian mode when such coverage is available.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/swap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/thread_group.h -->
## sources/storage-engines/wiredtiger/src/include/thread_group.h

Purpose: `thread_group.h` defines the shared control structures for WiredTiger utility thread pools such as eviction, checkpoint-adjacent workers, and other background services that need common start, pause, wake, and stop mechanics.

Important APIs and types: `WT_THREAD` stores a worker session, numeric id, OS thread id, lifecycle flags (`WT_THREAD_ACTIVE`, `WT_THREAD_CAN_WAIT`, `WT_THREAD_PANIC_FAIL`, `WT_THREAD_RUN`), a pause condition variable, and check/run/stop function pointers. `WT_THREAD_GROUP` stores allocation bounds, current active count, group name, a group lock, wake condition, an array of stable `WT_THREAD *` entries, and shared callbacks. `WT_THREAD_PAUSE` defines the paused-thread timeout.

Control flow: group owners allocate a `WT_THREAD_GROUP`, assign callbacks, and grow or shrink `WT_THREAD` entries. Individual threads call the check function to decide whether work is available, the run function to perform work, wait on `pause_cond` or `wait_cond` when inactive, and optionally call the stop function during teardown.

State and persistence behavior: all state is in-memory process/thread lifecycle state. The array is intentionally an array of pointers rather than structures so reallocating the group table does not move live thread contexts observed by running worker threads.

Dependencies and integration points: the definitions depend on `WT_SESSION_IMPL`, `WT_CONDVAR`, `WT_RWLOCK`, `wt_thread_t`, and WiredTiger flag macros. Thread-group management code and subsystem-specific background workers consume this header to share lifecycle semantics and panic-on-failure behavior.

Risks: lifetime and synchronization are central. Moving `WT_THREAD` objects, freeing a group while worker callbacks still reference it, or updating flags without the expected lock/condition discipline can race shutdown. Callback contracts are not type-rich, so subsystem implementations must preserve session ownership and blocking rules themselves.

Test signals: background-worker start/stop tests, resize tests that grow and shrink groups under load, shutdown/panic injection for `WT_THREAD_PANIC_FAIL`, condition wake tests for paused workers, and sanitizer runs that exercise worker teardown while work remains queued.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/thread_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/tiered.h -->
## sources/storage-engines/wiredtiger/src/include/tiered.h

Purpose: `tiered.h` declares the in-memory model for WiredTiger tiered storage: local and shared tier slots, per-tier operation capabilities, background work units, tiered table handles, and object/tree descriptors.

Important APIs and types: constants define tier indexes (`WT_TIERED_INDEX_LOCAL`, `WT_TIERED_INDEX_SHARED`, `WT_TIERED_INDEX_INVALID`), `WT_TIERED_MAX_TIERS`, object-name flags, `WT_FLUSH_STATE_DONE`, work-unit types (`WT_TIERED_WORK_FLUSH`, `WT_TIERED_WORK_FLUSH_FINISH`, `WT_TIERED_WORK_REMOVE_LOCAL`, `WT_TIERED_WORK_REMOVE_SHARED`), work flags, `WT_TIERED_WORK_UNIT`, `WT_TIERED_TIERS`, `WT_TIERED`, `WT_TIERED_OBJECT`, and `WT_TIERED_TREE`.

Control flow: tiered tables maintain a local writable tier and a shared tier that can receive flushed objects. Flush and cleanup paths enqueue `WT_TIERED_WORK_UNIT` records with an operation type, object id, tiered handle, and force/free flags. Worker code dequeues units, performs object flush/finish/remove operations, and uses the tier definitions to decide whether a tier supports read, write, or flush.

State and persistence behavior: the structures mirror metadata that describes tiered tables and object ids, but the header itself stores only in-memory handles. `current_id`, `next_id`, and `oldest_id` track object generations for a tiered handle; object descriptors include URI, approximate count, size, switch transaction/timestamp, id, generation, reference count, and local-residency flag. Actual persistence occurs through metadata and bucket storage implementations.

Dependencies and integration points: the header depends on `WT_DATA_HANDLE`, `WT_BUCKET_STORAGE`, `TAILQ_ENTRY`, timestamps, and atomic helpers. It integrates with metadata creation/open, tiered cursor/open logic, background flush-tier workers, object naming helpers, and statistics such as `flush_tier`, `local_objects_inuse`, and tiered work-unit counters from `stat.h`.

Risks: several object/tree structures are marked currently unused, so future code can accidentally assume invariants that are not maintained. Object id transitions and flush-state atomic counters must stay synchronized with metadata publication or readers may miss shared objects or retain local objects too long. Static tier slots simplify initial design but require care if more than local/shared tiers become active.

Test signals: tiered table create/open/reopen tests, `flush_tier` success and skip cases, forced flush behavior, local-object removal, shared-object removal, object naming with each flag combination, metadata crash/recovery around object id changes, and background work queue tests that verify unit counters and free semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/tiered.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/time_inline.h -->
## sources/storage-engines/wiredtiger/src/include/time_inline.h

Purpose: `time_inline.h` provides fast internal time helpers for wall-clock time, CPU tick reads, operation timeouts, and elapsed-time measurement.

Important APIs: `__wt_rdtsc` reads x86 `rdtsc`, ARM virtual counter `cntvct_el0`, MSVC `__rdtsc`, or returns zero on unsupported platforms. `__wt_epoch` wraps raw epoch time and enforces per-session monotonicity through `__time_check_monotonic`. `__wt_clock` chooses epoch nanoseconds or CPU ticks based on process configuration. Helpers return milliseconds/seconds, convert clock deltas to nanoseconds, start/stop/check operation timers, evaluate timers in milliseconds, and convert microseconds to `timespec`.

Control flow: callers choose raw elapsed timing through `__wt_clock` or wall-clock time through `__wt_epoch`. If a session observes time moving backward, the helper increments the `time_travel` stat and reuses the last per-session epoch value. Operation timers copy the active transaction timeout into session fields, then compare `WT_CLOCKDIFF_US(now, start)` against the configured timeout.

State and persistence behavior: state is per-session timing state (`last_epoch`, `operation_start_us`, `operation_timeout_us`) plus process-level timing configuration (`use_epochtime`, `tsc_nsec_ratio`). Nothing is persisted. The monotonicity guarantee is per session only; multiple sessions can still observe non-monotonic ordering relative to each other.

Dependencies and integration points: depends on `wt_internal.h`, stat macros, transaction flags, process timing calibration, raw epoch functions, and WiredTiger time arithmetic macros. It is used by cursor/session operations, operation timeout enforcement, perf histogram accounting, checkpoint/eviction timing, and diagnostic duration reporting.

Risks: unsupported hardware tick reads return zero, so builds must configure epoch timing or avoid interpreting raw ticks as real time. TSC conversion depends on a valid `tsc_nsec_ratio`; CPU frequency changes or unstable counters can skew elapsed results. `__wt_seconds32` has a documented 2038 limitation. Operation timeout checks only fire for running transactions and can miss non-transactional work.

Test signals: monotonic-time tests using mocked backward raw time, operation timeout tests for running and non-running transactions, platform build tests for x86/ARM/MSVC/fallback branches, perf histogram sanity checks, and tests that force epoch timing to validate nanosecond/millisecond conversions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/time_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/timestamp.h -->
## sources/storage-engines/wiredtiger/src/include/timestamp.h

Purpose: `timestamp.h` defines the core time-window and time-aggregate structures that encode transaction ids, commit/durable timestamps, stop timestamps, and prepare metadata for values, tombstones, pages, and reconciled aggregates.

Important APIs and types: string buffer constants include `WT_TS_HEX_STRING_SIZE`, `WT_TS_INT_STRING_SIZE`, and `WT_TIME_STRING_SIZE`. `WT_TIME_WINDOW` stores durable/start/prepare/start transaction fields plus durable/stop/prepare/stop transaction fields. `WT_TIME_AGGREGATE` stores newest start/stop durable timestamps, oldest start timestamp, newest transaction, newest stop timestamp and transaction, prepare marker, and `init_merge`.

Control flow and state: this header is declarative; mutation is performed by `timestamp_inline.h`, transaction code, reconciliation, history-store code, and page-delete logic. The defaults are semantically important: no start is `WT_TXN_NONE`/`WT_TS_NONE`, no stop is `WT_TXN_MAX`/`WT_TS_MAX`, and prepared ids default to `WT_PREPARED_ID_NONE`.

Persistence behavior: these structures are part of WiredTiger's MVCC and history metadata model. Time windows can be materialized into on-disk cells/pages, and time aggregates summarize page-level visibility for reconciliation, eviction, checkpoint, rollback-to-stable, and obsolete-history decisions.

Dependencies and integration points: depends on timestamp and transaction sentinel constants from `txn.h`. It integrates tightly with `txn_inline.h` visibility checks, `timestamp_inline.h` macros, cell unpacking, reconciliation time aggregation, history-store lookup, rollback-to-stable, and checkpoint stable/oldest timestamp rules.

Risks: sentinel values carry meaning, so changing `WT_TS_MAX`, `WT_TXN_MAX`, or default initialization semantics would affect visibility and obsolete detection. Durable timestamps must be treated conservatively because content cannot be discarded merely because commit timestamp is old. Prepared metadata must be propagated consistently or readers can miss prepare conflicts.

Test signals: timestamp format tests, time-window encode/decode tests, checkpoint/recovery with prepared updates and tombstones, rollback-to-stable tests that rely on newest durable timestamps, and reconciliation tests that verify page aggregates for all-live, all-deleted, prepared, and mixed windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/timestamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/timestamp_inline.h -->
## sources/storage-engines/wiredtiger/src/include/timestamp_inline.h

Purpose: `timestamp_inline.h` supplies the mutation and predicate macros for `WT_TIME_WINDOW` and `WT_TIME_AGGREGATE`, plus inline getters for globally managed oldest, stable, and disaggregated schema timestamps.

Important APIs: time-window macros initialize, copy, compare, test start/stop/prepare presence, and set start/stop values from `WT_UPDATE` with prepared-rollback race handling. Time-aggregate macros initialize normal or merge accumulators, test emptiness, update from a time window or page delete, merge aggregates conservatively, normalize aggregates for obsolete-visible checks, and test whether stop data exists. Inline getters are `__wt_get_oldest_timestamp`, `__wt_get_stable_timestamp`, and `__wt_get_stable_disaggregated_schema_epoch`.

Control flow: update/read/reconciliation paths fill a `WT_TIME_WINDOW` from updates or cells, then feed it into `WT_TIME_AGGREGATE_UPDATE` while scanning keys or pages. Merge paths start with `WT_TIME_AGGREGATE_INIT_MERGE`, then choose max durable/newest values and min oldest-start values. Obsolete checks use `WT_TIME_AGGREGATE_MERGE_OBSOLETE_VISIBLE` to preserve the subtle distinction between all-deleted and partially-live pages.

State and persistence behavior: macros mutate caller-owned in-memory structs that often mirror persistent cell/page metadata. The getters read `WT_TXN_GLOBAL` booleans with acquire ordering before reading timestamp values; stable timestamp falls back to `recovery_timestamp` when no stable timestamp is published, while disaggregated schema epoch falls back to `WT_SCHEMA_EPOCH_NONE`.

Dependencies and integration points: depends on `WT_UPDATE`, `WT_PAGE_DELETED`, `WT_TXN_GLOBAL`, timestamp sentinels, atomic helpers, TSAN suppression, and visibility semantics in `txn_inline.h`. It integrates with update-chain reads, reconciliation, page deletion, checkpoint, rollback-to-stable, history store, disaggregated storage, and transaction timestamp APIs.

Risks: these are macros with repeated field access and no type safety beyond compile-time field names. Race handling around prepared rollback depends on reading saved transaction ids when an update txnid has become `WT_TXN_ABORTED`. Aggregate merge semantics are easy to misuse; in particular durable stop timestamp and `WT_TS_MAX` encode different concepts for obsolete checks.

Test signals: unit tests for empty/default predicates, prepared start/stop propagation, aborted prepared rollback races, page-delete aggregate updates, aggregate merge/all-deleted cases, getter ordering under concurrent timestamp publication, and rollback-to-stable/checkpoint suites that validate durable timestamp retention.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/timestamp_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/truncate.h -->
## sources/storage-engines/wiredtiger/src/include/truncate.h

Purpose: `truncate.h` defines the compact context object used to carry state through a range truncate operation.

Important APIs and types: `WT_TRUNCATE_INFO` stores the owning session, URI, optional start and stop cursors, original start and stop keys, and flags `WT_TRUNC_EXPLICIT_START` and `WT_TRUNC_EXPLICIT_STOP` that distinguish caller-provided boundaries from inferred range boundaries.

Control flow and state: truncate code fills this structure before validating cursors and applying row-store or column-store range deletion. The flags guide boundary handling, error reporting, and whether original keys need to be retained while cursors move during truncate processing.

Persistence behavior: the structure itself is transient. Persistent effects are produced elsewhere as tombstone updates, page-delete records, transaction operations, and metadata/stat changes when the truncate is committed or rolled back.

Dependencies and integration points: depends on `WT_SESSION_IMPL`, public `WT_CURSOR`, `WT_ITEM`, and transaction/truncate implementation code. It connects public `WT_SESSION::truncate` inputs to lower-level cursor, btree, transaction, and reconciliation code.

Risks: lifetime of `orig_start_key` and `orig_stop_key` must outlive the truncate operation. Mis-set explicit-bound flags can delete too broad or too narrow a range. Cursor movement during truncate makes key preservation important for diagnostics and transaction operation reconstruction.

Test signals: truncate with no bounds, start-only, stop-only, and both bounds; row and column stores; rollback and prepared transactions; empty ranges; cursor repositioning; and crash/recovery tests that verify committed truncates persist while rolled-back truncates do not.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/truncate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/tsan_suppress.h -->
## sources/storage-engines/wiredtiger/src/include/tsan_suppress.h

Purpose: `tsan_suppress.h` provides narrowly named inline wrappers for known benign or transitional data races so WiredTiger can use function-level TSAN suppressions without suppressing entire complex callers.

Important APIs: wrappers cover relaxed loads/stores for integer, bool, size, pointer, and volatile variants; non-atomic add/subtract helpers for selected counters; TSAN-suppressed `memcpy`/`memset`; and typed pointer helpers for `WT_FH`, `WT_PAGE`, `WT_INSERT`, `WT_SESSION_IMPL`, `WT_ADDR`, `WTI_LOGSLOT`, `WT_PAGE_MODIFY`, `WT_PAGE_HEADER`, `WT_UPDATE`, and `const char *`.

Control flow and state: most wrappers call WiredTiger relaxed atomic primitives and return or store a single value. A few add/subtract wrappers intentionally perform plain arithmetic while carrying a suppressible function name. There is no independent state or persistence.

Dependencies and integration points: depends on WiredTiger atomic helpers and forward-declared internal types. It is used by stats, transaction timestamp assignment, update-chain reads, page/ref pointer access, log slot access, cache/page structures, and other hot paths where full synchronization is either pending or intentionally unnecessary for the observed field.

Risks: the file explicitly encodes technical debt. A wrapper can hide a real race if used too broadly, and relaxed atomics do not create ordering guarantees. The plain arithmetic helpers are not atomic despite their suppressive naming. Comments in nearby callers often reference future fixes such as replacing statistic and timestamp races with proper synchronization.

Test signals: TSAN CI with a suppression file that names these wrappers, code review requiring each new wrapper use to document why relaxed/plain access is safe, stress tests around transaction prepare/commit, statistics, page eviction, and log slot handling, plus eventual removal tests when a race is replaced by stronger atomics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/tsan_suppress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/txn.h -->
## sources/storage-engines/wiredtiger/src/include/txn.h

Purpose: `txn.h` declares WiredTiger's transaction constants, sentinel ids/timestamps, rollback reason strings, visibility/isolation enums, shared transaction table entries, global transaction state, per-transaction operation records, snapshots, transaction time points, and per-session transaction context.

Important APIs and types: key sentinels include `WT_TXN_NONE`, `WT_TXN_FIRST`, `WT_TXN_MAX`, `WT_TXN_ABORTED`, `WT_TS_NONE`, `WT_TS_MAX`, and schema epoch sentinels. It defines checkpoint log flags, oldest-timestamp flags, timestamp-set flags, `WT_VISIBLE_TYPE`, `WT_OP_CONTEXT`, `WT_TXN_ISOLATION`, `WT_TXN_TYPE`, `WT_TXN_TRUNC_MODE`, `WT_TXN_SHARED`, `WT_PENDING_PREPARED_ITEM`, `WT_PENDING_PREPARED_MAP`, `WT_TXN_GLOBAL`, `WT_TXN_OP`, `WT_TXN_SNAPSHOT`, `WT_TXN_LOG`, `WT_TXN_TIME_POINT`, `WT_TXN`, and `WT_FIX_PREPARED_COOKIE`.

Control flow: transaction code publishes per-session state through `WT_TXN_SHARED`, tracks global current/oldest/durable/stable/pinned timestamps in `WT_TXN_GLOBAL`, stores per-operation undo/log/prepare metadata in `WT_TXN_OP`, and carries snapshot bounds plus active transaction ids in `WT_TXN_SNAPSHOT`. `WT_WITH_TXN_ISOLATION` temporarily forces isolation while asserting that transaction id and pinned state are restored safely.

State and persistence behavior: the structures are in-memory control state for MVCC, checkpoint, logging, prepared transactions, rollback-to-stable, and disaggregated schema epochs. They drive persistent effects by assigning transaction ids and timestamps to updates, page deletes, metadata, and log records. Prepared transaction maps can hold operations discovered from checkpoints for later claim/commit/rollback.

Dependencies and integration points: depends on cache-line padding, atomic/shared annotations, tail queues, btree/data-handle/session types, LSNs, item buffers, and timestamp definitions. It is the core contract consumed by `txn_inline.h`, transaction implementation files, checkpoint, logging, reconciliation, history store, recovery, cursor reads/writes, truncate, and prepared-discovery code.

Risks: sentinel ordering is fundamental: aborted must remain never visible, none must remain always visible, and max must represent end-of-time. Shared fields require precise memory ordering in inline code. The prepared transaction claim path swaps operation arrays, so ownership mistakes can double-free or leak operation state. Rollback reason strings are API-observable and should not change casually.

Test signals: transaction begin/commit/rollback suites, isolation matrix tests, prepared transaction recovery and claim tests, timestamp API tests, checkpoint visibility tests, rollback-to-stable, write-conflict tests, debug rollback injection, and assertions around `WT_WITH_TXN_ISOLATION` restoring shared pinned ids.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/txn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/txn_inline.h -->
## sources/storage-engines/wiredtiger/src/include/txn_inline.h

Purpose: `txn_inline.h` implements the hot inline transaction machinery: API context checks, logging eligibility, transaction error marking, operation capture, prepare-state transitions, timestamp validation/assignment, update allocation, visibility checks, update-chain reads, history-store fallback, transaction begin/autocommit/id allocation, write-conflict detection, snapshot publication, and activity checks.

Important APIs: early helpers include `__wt_txn_context_prepare_check`, `__wt_txn_context_check`, `__wt_txn_log_op_check`, `__wt_txn_err_set`, key/recno capture helpers, `__wt_txn_modify`, `__wt_txn_truncate`, `__wt_txn_modify_page_delete`, timestamp helpers such as `__wt_txn_timestamp_usage_check` and `__wt_txn_op_set_timestamp`, visibility helpers such as `__wt_txn_visible_id`, `__wt_txn_visible`, `__wt_txn_visible_all`, `__wt_txn_upd_visible_type`, update allocation/read helpers, `__wt_txn_begin`, `__wt_txn_id_alloc`, `__wt_txn_id_check`, `__wt_txn_modify_check`, and cursor/snapshot release helpers.

Control flow: writes first ensure a running transaction can update, allocate and publish a transaction id when needed, append a `WT_TXN_OP`, stamp the update or truncate/page-delete object, optionally log the operation, and roll back the operation record if insertion fails. Prepare and commit paths transition updates through `WT_PREPARE_INPROGRESS`, `WT_PREPARE_LOCKED`, and `WT_PREPARE_RESOLVED` with release/acquire ordering so readers never observe partially rewritten timestamps.

Visibility behavior: id visibility honors sentinels, own writes, read-uncommitted, and snapshot min/max/member lists. Timestamp visibility separately gates reads by read timestamp or checkpoint read/stable timestamps. Global visibility uses oldest transaction id plus pinned/stable/checkpoint/disaggregated timestamps to decide when updates or time windows are visible to every possible reader and can be made obsolete.

Read path: `__wt_txn_read` scans the in-memory update chain for the first visible update, handles ignored tombstones and prepared conflicts, reconstructs modify chains, reads on-page values when no visible update exists, detects visible tombstones, and finally searches the history store when necessary. It retries once around races with prepared updates restored from disk and records race counters such as `txn_read_race_prepare_commit` and `txn_read_race_prepare_update`.

State and persistence behavior: this file mutates per-session `WT_TXN`, global/shared transaction table state, btree `max_upd_txn`, update records, page-delete timestamps, dirty byte statistics, and session/data-handle usage counts. Persistent consequences appear through update timestamps, durable timestamps, logged operations, history-store records, page-delete metadata, and checkpoint/rollback visibility.

Dependencies and integration points: it depends on nearly all core WiredTiger internals: sessions, btrees, data handles, refs/pages, updates, page deletes, history store, reconciliation modify reconstruction, logging, eviction assist, timestamp globals, stats, TSAN wrappers, atomics/barriers, verbose/error handling, and prepared-discovery helpers. Cursor insert/update/remove/search paths and reconciliation/eviction call these helpers extensively.

Risks: correctness is concurrency-sensitive. Prepare resolution relies on explicit barriers and state rereads; visibility can be wrong if id and timestamp checks are mixed incorrectly; durable timestamp ordering is enforced and may abort in diagnostic builds; history-store fallback has subtle races with prepared rollback/commit; read-committed/uncommitted writes are rejected except metadata; and TSAN-suppressed timestamp writes document known data-race cleanup areas.

Test signals: isolation and snapshot tests, timestamp assertion tests (`always`/`never` read/write), prepared commit/rollback/read-conflict tests, history-store read fallback and modify reconstruction tests, truncate/page-delete timestamp tests, transaction id exhaustion/error-path tests, autocommit tests, cache-full eviction-assist paths, write conflict and debug rollback tests, TSAN stress around prepare transitions, and checkpoint cursor visibility tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/txn_inline.h -->
