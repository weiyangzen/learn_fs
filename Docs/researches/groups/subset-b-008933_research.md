# subset-b-008933 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/lock_manager/lock_waiting_queue.rs -->
# sources/storage-engines/tikv/src/storage/lock_manager/lock_waiting_queue.rs

## Purpose

This file implements `LockWaitQueues`, the per-key waiting queue used by TiKV storage when `AcquirePessimisticLock` requests encounter an existing lock. It tracks blocked lock acquisition requests, orders them by transaction start timestamp, wakes them when the blocking lock is released, and supports the legacy retry behavior where non-resumable waiters are cancelled with `WriteConflict` after a delayed wake-up window. It also connects queue changes to lock-manager wait-for updates and Prometheus metrics.

The module-level comments are important design documentation. They distinguish legacy requests (`allow_lock_with_conflict == false`) from resumable requests (`allow_lock_with_conflict == true`) and explain why delayed notification exists: after a legacy waiter is woken and returns retry to the client, the key may remain unlocked and older waiters must not wait forever for a release event that may never happen.

## Important APIs, Types, and Functions

`LockWaitEntry` represents a single waiting pessimistic-lock request. It stores the target `Key`, a precomputed `lock_hash`, full `PessimisticLockParameters`, key-local flags (`should_not_exist`, `is_shared_lock`), its `LockWaitToken`, shared cancellation state, optional `legacy_wake_up_index`, and the key callback to finish the request. Its ordering reverses `start_ts` comparison so `KeyedPriorityQueue`, which is a max heap, pops the smallest start timestamp first.

`KeyLockWaitState` is the value stored per key in the dashmap. It contains the latest known `current_lock`, a `legacy_wake_up_index` counter, the keyed priority queue, the latest conflict timestamps used to construct `WriteConflict`, and optional delayed-notify state `(id, start_time, delay_duration)`.

`LockWaitQueueInner` holds the concurrent `DashMap<Key, KeyLockWaitState>`, internal delayed-notify id allocator, atomic entry count, and the generic `LockManager`. `LockWaitQueues<L>` wraps it in `Arc` so handles can be cloned into delayed futures.

`push_lock_wait` inserts a `LockWaitEntry` for its key, initializes per-key state when needed, records the current legacy wake index on first insertion, refreshes `current_lock`, increments `entries_count`, and updates `LOCK_WAIT_QUEUE_ENTRIES_GAUGE_VEC` plus `LOCK_WAIT_QUEUE_LENGTH_HISTOGRAM`.

`on_push_canceled_entry` handles the corner case where a request was cancelled while temporarily absent from the queue. If the stored external error is `KeyIsLocked`, it replaces the embedded lock info with the latest per-key `current_lock` when available, then invokes the waiting callback as cancelled.

`pop_for_waking_up` and `pop_for_waking_up_impl` remove the next waiter or a consecutive group of shared-lock waiters. Legacy waiters increment the per-key wake index and may schedule delayed notification if more entries remain. The method returns popped entries plus an optional `DelayedNotifyAllFuture` that the caller must execute.

`handle_delayed_wake_up`, `async_delayed_notify_all`, and `delayed_notify_all` implement the delayed legacy wake path. Existing delayed tasks are extended by atomically increasing the target delay. A new task sleeps through `GLOBAL_TIMER_HANDLE`, checks that its notify id still matches the key state, drains only entries whose recorded legacy index predates the latest wake-up, cancels legacy entries with `WriteConflict`, and stops at the first resumable entry, returning it to the caller for resumed execution.

`remove_by_token` removes a particular waiter from a key queue without calling the callback. The caller owns completion/cancellation after removal.

`update_lock_wait` accepts fresh `LockInfo` records, updates `current_lock` for matching keys, builds `UpdateWaitForEvent` entries for each queued waiter, and calls `lock_mgr.update_wait_for` so deadlock detection and wait-for diagnostics track the latest blocking lock.

`entry_count`, `is_empty`, and test-only assertion helpers expose queue state.

## Control Flow

The normal enqueue path starts when storage creates a `LockWaitEntry` for a lock conflict and calls `push_lock_wait`. The function checks cancellation state before insertion, gets or creates a per-key `KeyLockWaitState`, stamps legacy entries with the current wake index, pushes into the keyed priority queue by token, increments atomic and Prometheus counters, and records queue length.

When a lock release can wake waiters, callers use `pop_for_waking_up`. Under `DashMap::remove_if_mut`, the implementation updates conflict timestamps, pops the highest-priority entry, optionally keeps popping adjacent shared-lock entries, updates legacy wake state, schedules or extends delayed notification if legacy waiters were popped and the queue is still non-empty, decrements counts, and removes the key entry if the queue is empty.

The delayed notification flow is asynchronous but stateful. A queued future waits until elapsed time reaches the latest atomic delay value, allowing later legacy wakeups to extend the same task. On timeout, `delayed_notify_all` verifies the notify id to avoid acting on stale recreated key state, clears delayed state, drains only entries that existed before the wake event, cancels drained legacy entries with `PessimisticRetry` write conflicts, and returns one resumable entry if encountered.

Cancellation can happen outside the queue through `LockWaitContextSharedState`. If a waiter is still queued, external cancellation eventually removes it by token. If cancellation happens while a waiter is being re-pushed after temporary removal, `push_lock_wait` detects it and calls `on_push_canceled_entry`.

`update_lock_wait` is a side-channel refresh path. It does not reorder queues; it updates diagnostic/current-lock information and propagates revised wait-for edges to the lock manager.

## State and Persistence Behavior

All state is in memory. There is no durable persistence in this file. Queue state is held in a concurrent `DashMap`, each key state owns an in-memory priority queue, and counts are maintained in atomics plus Prometheus metrics. Delayed wake-up state is also in memory and keyed by an internal id so stale futures do not mutate newly recreated queues.

The logical state invariants are more important than persistence: `entries_count` should match total queued entries, `LOCK_WAIT_QUEUE_ENTRIES_GAUGE_VEC.waiters` and `.keys` should track waiters and non-empty key queues, and `legacy_wake_up_index` partitions old waiters from waiters that arrived after the wake event that scheduled delayed notification.

The callback in each `LockWaitEntry` is consumed exactly when a waiting request is cancelled by delayed notification or by the cancelled-on-push path. Pop and remove paths intentionally return entries without invoking callbacks so upper layers can resume, retry, or otherwise finish the request.

## Dependencies and Integration Points

The implementation depends on `dashmap` for concurrent key-state storage, `keyed_priority_queue` for token-addressable priority queues, `smallvec` for small batches of delayed cancellations, `sync_wrapper` for storing callback closures, `GLOBAL_TIMER_HANDLE` plus `Future01CompatExt` for sleeping delayed tasks, and TiKV transaction types such as `Key`, `TimeStamp`, `PessimisticLockParameters`, `StorageError`, `TxnError`, and `MvccError`.

The generic `LockManager` integration is used through `update_lock_wait` and through test mocks. `LockWaitToken`, `KeyLockWaitInfo`, `LockDigest`, and `UpdateWaitForEvent` come from the sibling lock-manager module. Metrics are imported from `storage::metrics` and updated on enqueue, pop, removal, and delayed drain.

Storage command execution must run returned `DelayedNotifyAllFuture` values. The queue itself does not own a runtime or thread pool, so missing future execution would leave legacy waiters blocked until another path wakes or cancels them.

## Risks and Edge Cases

The main correctness risk is count drift between the queue map, `entries_count`, and Prometheus gauges. The code decrements inside `remove_if_mut` and then adjusts metrics after lock release; any future changes to early returns or multi-entry shared pops must preserve those paths.

The delayed wake logic is subtle. It relies on `legacy_wake_up_index` comparisons, notify ids, and an atomically extendable delay. Off-by-one changes can either over-cancel new waiters, causing unnecessary retries, or under-cancel old waiters, causing indefinite waiting.

Shared-lock grouping wakes consecutive shared waiters only at the front of the queue. This assumes the priority ordering plus `is_shared_lock` semantics are sufficient; mixed shared/exclusive waiters require careful tests so exclusive waiters are not bypassed incorrectly.

Callback ownership is a risk because `key_cb` is an `Option` that is unwrapped in cancellation paths. Callers must only enqueue entries with callbacks and must avoid double-consuming a callback.

`on_push_canceled_entry` rewrites nested error lock info only for a specific `StorageError::Txn::Mvcc::KeyIsLocked` shape. New error variants or wrapper changes could make cancellation return stale lock info.

`async_delayed_notify_all` unwraps the timer result. Timer failures are presumably fatal/unexpected in TiKV, but this is still a panic edge.

## Test Signals

The file contains focused unit tests and benches. `test_simple_push_pop` validates basic enqueue, pop, key removal, and empty-state accounting. `test_popping_priority` verifies start-ts ordering and duplicate start timestamps. `test_removing_by_token` exercises targeted removal and idempotent missing-token removal. `test_dropping_cancelled_entries` validates external cancellation removing queued entries.

`test_delayed_notify_all` is the most important behavioral test. It covers delayed legacy wake-up, avoiding wake of entries added after the scheduling wake event, stopping at a resumable waiter, stale/mismatched notify ids, extending an existing delayed future, latest conflict timestamp propagation, and no-op behavior for missing keys.

`test_pop_shared_group` checks grouped popping of consecutive shared lock waits and transition to a later exclusive wait. Two benchmarks measure `update_lock_wait` overhead for an empty/mismatched update and a queue with 512 waiters.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/lock_manager/lock_waiting_queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/lock_manager/mod.rs -->
# sources/storage-engines/tikv/src/storage/lock_manager/mod.rs

## Purpose

This module defines the storage lock-manager interface used by TiKV transactions that wait for pessimistic locks. It provides common types for describing lock wait relationships, a timeout encoding helper, diagnostic context carried into wait tracking, and the `LockManager` trait implemented by real server-side deadlock/waiter managers. It also exports the `lock_wait_context` and `lock_waiting_queue` submodules.

The file is the boundary between storage code that encounters locks and the server lock-manager subsystem that tracks wait-for relationships, timeouts, cancellation, deadlock handling, and diagnostic dumps.

## Important APIs, Types, and Functions

`LockDigest` is a compact identity for a blocking lock: its transaction timestamp plus a key hash.

`DiagnosticContext` carries diagnostic metadata for lock waits: the key of interest, TiDB resource group tag or SQL digest-style tag, and a `TrackerToken`. Its custom `Debug` implementation logs key-like fields through `log_wrappers::Value::key`, avoiding raw sensitive key output.

`WaitTimeout` models lock wait timeout policy. `Default` means use the caller-provided ceiling, while `Millis(u64)` is capped by `into_duration_with_ceiling`. `from_encoded` maps protobuf-style timeout integers into `Option<WaitTimeout>`: zero means default, positive means explicit milliseconds, and negative means no wait (`None`).

`KeyLockWaitInfo` describes the lock a request is waiting for. It includes the waiting key, `LockDigest`, full protobuf `LockInfo`, and whether the request is allowed to lock despite conflict.

`LockWaitToken` uniquely identifies a waiting request. The token wraps `Option<u64>`, allowing invalid/no-token states; `is_valid` checks for `Some`.

`UpdateWaitForEvent` carries updates for an existing wait-for edge: token, waiting transaction start timestamp, first-lock flag, and new `KeyLockWaitInfo`.

`LockManager` is the key trait. Implementors must allocate tokens, register wait-for relationships through `wait_for`, update them through `update_wait_for`, remove waiters, expose a cheap `has_waiter` hint, and dump wait-for entries through `waiter_manager::Callback`.

`MockLockManager` is a test implementation backed by `Arc<AtomicU64>` token allocation and an `Arc<parking_lot::Mutex<HashMap<LockWaitToken, (KeyLockWaitInfo, CancellationCallback)>>>`. It can simulate timeout for all waiters or a single waiter by invoking stored cancellation callbacks with `KeyIsLocked` errors.

## Control Flow

The typical flow begins with storage code calling `allocate_token`, then creating lock wait context and queue state tied to that token. When a transaction must wait on a lock, storage calls `wait_for` with region metadata, transaction start timestamp, `KeyLockWaitInfo`, first-lock status, timeout policy, cancellation callback, and diagnostics. The real implementation records the dependency for timeout/deadlock handling.

If the underlying blocking lock information changes while the request is still waiting, storage or `LockWaitQueues` calls `update_wait_for` with `UpdateWaitForEvent` records. If the waiter no longer needs tracking, `remove_lock_wait` removes it. Monitoring or diagnostics can call `dump_wait_for_entries`.

The mock follows the same broad contract but stores only `wait_info` and cancellation callbacks. `simulate_timeout_all` drains the map and cancels every waiter. `simulate_timeout` removes and cancels one token.

## State and Persistence Behavior

This file defines in-memory interfaces and test state only. There is no durable persistence. `DiagnosticContext` and wait-info structs are passed by value into runtime managers. `MockLockManager` persists waiters only for the lifetime of the test object.

The important state contract is token identity. `LockWaitToken` must be allocated before wait registration so related storage structures and cancellation callbacks can reference the same waiter. Mock token allocation uses relaxed atomics, which is enough for uniqueness in tests because the token value has no synchronization semantics.

## Dependencies and Integration Points

The module depends on `kvproto` lock and region metadata, TiKV `txn_types::{Key, TimeStamp}`, `tracker::TrackerToken`, `collections::{HashMap, HashSet}`, and `parking_lot::Mutex` for the mock. It imports server lock-manager callback types from `crate::server::lock_manager::waiter_manager`.

It re-exports `CancellationCallback` from `lock_wait_context`, making cancellation callback type usage available to other storage modules. It declares `lock_wait_context` and `lock_waiting_queue`, whose code uses the trait and types here.

Error integration in the mock uses `StorageError`, `TxnError`, and `MvccErrorInner::KeyIsLocked` to emulate timeout/deadlock cancellation paths expected by storage callers.

## Risks and Edge Cases

Timeout decoding is compact but semantically loaded: negative encoded values return `None`, meaning no wait rather than an immediate timeout. Callers must preserve that distinction.

`LockWaitToken(None)` is representable. Code using tokens must either validate with `is_valid` or be designed to tolerate invalid tokens.

The default `has_waiter` returns `true`, favoring correctness over optimization. Real implementations should override it if they want to avoid unnecessary wake-up calculations.

`DiagnosticContext::Debug` intentionally redacts key-like fields. Future changes should avoid accidentally logging raw keys or resource tags.

The mock `remove_lock_wait` is a no-op, unlike a real lock manager. Tests that rely on exact removal semantics need either a richer mock or direct map inspection.

## Test Signals

There are no direct `#[test]` functions in this file. Its test signal is the `MockLockManager`, which supports unit tests in `lock_waiting_queue.rs` and other storage modules. The mock exposes `simulate_timeout_all`, `simulate_timeout`, and `get_all_tokens` to validate cancellation behavior and token registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/lock_manager/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/metrics.rs -->
# sources/storage-engines/tikv/src/storage/metrics.rs

## Purpose

This file defines Prometheus metrics and thread-local metric collection helpers for TiKV storage. It covers scheduler command counts and durations, scan details, read flow reporting to PD, query counts, latch and processing histograms, flow-control gauges/counters, memory quota gauges, pessimistic lock queue gauges, in-memory pessimistic locking counters, and transaction status cache metrics.

The file centralizes storage metric labels through `prometheus_static_metric` macros and exposes static metric handles used throughout storage and lock-manager code.

## Important APIs, Types, and Functions

`StorageLocalMetrics` is thread-local aggregation state containing `local_scan_details: HashMap<CommandKind, Statistics>` and `local_read_stats: ReadStats`.

`TLS_STORAGE_METRICS` stores `StorageLocalMetrics` in a `RefCell` per thread. This avoids global contention while commands collect scan and read-flow details.

`tls_collect_scan_details` accumulates `Statistics` by `CommandKind`. `tls_collect_read_flow` records per-region read flow into `ReadStats`, including optional bucket metadata and write/data CF flow stats. `tls_collect_query` and `tls_collect_query_batch` record query counts using raftstore key-range helpers or provided protobuf ranges.

`tls_flush` drains local scan details into `KV_COMMAND_SCAN_DETAILS_STATIC`, swaps out non-empty read stats, and reports them through a generic `FlowStatsReporter`. This is the flushing boundary from thread-local state to global Prometheus counters and PD flow reporting.

The `make_auto_flush_static_metric!` block defines static label enums and typed metric wrappers: `CommandKind`, `CommandStageKind`, `CommandPriority`, `GcKeysCF`, `GcKeysDetail`, `CheckMemLockResult`, `InMemoryPessimisticLockingResult`, and metric structs such as `CommandScanDetails`, `SchedDurationVec`, `ProcessingReadVec`, `KReadVec`, `KvCommandCounterVec`, `SchedStageCounterVec`, `SchedLatchDurationVec`, `KvCommandKeysWrittenVec`, `SchedTooBusyVec`, `SchedCommandPriCounterVec`, `CheckMemLockHistogramVec`, `TxnCommandThrottleTimeCounterVec`, and `InMemoryPessimisticLockingCounter`.

`impl From<ServerGcKeysCF> for GcKeysCF` and `impl From<ServerGcKeysDetail> for GcKeysDetail` bridge server-level scan detail labels into storage labels.

`unsafe fn with_perf_context<E, Fn, T>` wraps a function call with engine perf context observation for selected command kinds. It creates one thread-local `PerfContext` slot per supported command kind, starts observation, runs the closure, reports metrics with the current tracker token, and returns the closure result. Unsupported command kinds bypass perf-context instrumentation and directly run the closure.

The `make_static_metric!` block defines typed gauges for lock wait queue entries, transaction status cache size, and scheduler memory quota.

The `lazy_static!` block registers all Prometheus metrics and exposes both raw vectors/histograms/gauges and typed static wrappers. Important exported metrics include `KV_COMMAND_COUNTER_VEC`, `SCHED_STAGE_COUNTER`, scheduler flow-control gauges, scheduler duration histograms, key read/write histograms, scan-detail counters, check-memory-lock histograms, transaction throttle counters, in-memory pessimistic locking counters, `LOCK_WAIT_QUEUE_ENTRIES_GAUGE_VEC`, `LOCK_WAIT_QUEUE_LENGTH_HISTOGRAM`, `SCHED_TXN_STATUS_CACHE_SIZE`, `SCHED_TXN_MEMORY_QUOTA`, and `SCHED_TXN_RUNNING_COMMANDS`.

## Control Flow

Command execution paths collect metrics locally during storage operations. Scan details are accumulated through `tls_collect_scan_details`; read flow and query information are accumulated through the other `tls_collect_*` functions. A scheduler or worker flush point calls `tls_flush`, which drains local scan counters into Prometheus and reports accumulated read stats to the supplied `FlowStatsReporter`.

Metric registration happens lazily when each static is first accessed. Static wrappers generated by `auto_flush_from!` provide typed label access and local auto-flush behavior for high-frequency counters/histograms.

Perf context collection wraps selected storage command kinds. The caller enters `with_perf_context`, the function selects the command-specific TLS perf-context cell, initializes it with `E::Local::get_perf_context` if missing, starts observation, executes the closure, and reports engine perf metrics tagged with the TLS tracker token.

## State and Persistence Behavior

All state is runtime-only. Thread-local metrics are buffered in memory until flushed, then counters/histograms/gauges live in the process Prometheus registry. Read-flow stats are moved to the caller-provided reporter rather than persisted here.

The TLS buffers are per thread, so missing or infrequent `tls_flush` calls can delay visibility and PD reporting for scan/read-flow metrics. Conversely, flushing drains scan details and swaps out read stats, resetting local accumulation after publication.

Registered metrics are effectively process-global once initialized. Gauge values such as lock-wait queue entries, scheduler memory quota, and running commands must be maintained by callers through increments/decrements or set operations in other modules.

## Dependencies and Integration Points

The file depends on `prometheus`, `prometheus_static_metric`, `lazy_static`, engine perf-context traits from `engine_traits`, `kvproto` range and query metadata, PD client bucket/write-detail types, raftstore `ReadStats` and `build_key_range`, `tikv_kv::Engine`, and tracker TLS tokens.

It integrates with `crate::storage::kv::{FlowStatsReporter, Statistics}` for flow/stat collection, with server GC-key metric label enums for conversion, and with many storage command modules through the exported metric statics and `CommandKind` labels.

`lock_waiting_queue.rs` specifically uses `LOCK_WAIT_QUEUE_ENTRIES_GAUGE_VEC` and `LOCK_WAIT_QUEUE_LENGTH_HISTOGRAM` from this file. Pessimistic locking and scheduler modules use the command, stage, throttle, memory, and in-memory-locking metrics.

## Risks and Edge Cases

The `with_perf_context` function is explicitly unsafe: callers must ensure the thread-local engine context exists and that using the selected engine local perf context is valid for the current thread. Misuse can produce incorrect metrics or engine-specific undefined behavior depending on the engine implementation contract.

Metric label enums are a compatibility surface. Renaming or removing labels changes exported Prometheus series and can break dashboards, alerts, or downstream monitoring.

Thread-local aggregation can hide metrics until flush. Any command path that collects TLS stats but fails to flush on completion or worker teardown risks under-reporting scan details and PD read stats.

The command-kind match in `with_perf_context` instruments only selected command labels. New command kinds added to `CommandKind` will not receive perf-context metrics unless explicitly mapped.

Prometheus registration uses `unwrap()`, so duplicate metric names or invalid bucket definitions panic at initialization. This is common for static metrics but means tests or alternate binaries must avoid double registration in the same registry.

Gauge metrics rely on balanced caller updates. For example, lock wait queue gauges can drift if queue operations skip decrement paths on new error branches.

## Test Signals

This file does not define local tests. Indirect test signals come from modules that assert metric-affecting behavior, such as lock wait queue tests exercising waiter/key increments and decrements. Runtime validation is primarily through Prometheus metric presence, label stability, and PD read-flow reporting behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/metrics.rs -->
