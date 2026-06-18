# subset-b-008901 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/thread_group.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/thread_group.rs

Purpose: provides process-local thread group properties, currently a shared shutdown flag propagated through thread-local storage.

Important APIs/types/functions: `GroupProperties`, `current_properties`, `set_properties`, `is_shutdown`, and `mark_shutdown`. `GroupProperties` wraps an `Arc<GroupPropertiesInner>` so cloned handles share the same `AtomicBool`.

Control flow: parent code captures `current_properties()` before spawning a thread and the child calls `set_properties`. `mark_shutdown` flips the shared flag; `is_shutdown(true)` panics through `safe_panic!` if no properties were installed.

State and persistence: all state is in-memory TLS plus an `Arc` atomic; nothing is persisted.

Dependencies/integration: used by timer, worker, and YATP pool thread startup paths to propagate shutdown awareness into spawned runtime threads.

Risks: missing `set_properties` silently returns false unless `ensure_set` is true; `SeqCst` is conservative but low-risk.

Test signals: no local tests in this file; coverage is indirect through spawned-thread utilities.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/thread_group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/thread_name_prefix.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/thread_name_prefix.rs

Purpose: central registry of TiKV-owned thread name prefixes, ordered roughly by server startup sequence.

Important APIs/types/functions: many `pub const` prefixes plus `matches_thread_name_prefix` and `matches_scheduler_thread_name`. Matching handles full prefixes and Linux `comm` truncation to 15 visible bytes.

Control flow: callers pass an observed thread name and a prefix; long prefixes are checked both as full strings and truncated byte slices. The scheduler helper uses the generic `sched` prefix to cover multiple scheduler thread families.

State and persistence: stateless constants and pure matching helpers.

Dependencies/integration: consumed by thread builders, diagnostics, thread maps, profiling, and tests that identify TiKV threads by name.

Risks: byte slicing assumes ASCII prefixes; adding non-ASCII names would be unsafe. Over-broad scheduler matching intentionally accepts historical `scheduler-worker-pool` names.

Test signals: unit tests cover basic prefix matching, Linux truncation, and scheduler-name matching.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/thread_name_prefix.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/time.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/time.rs

Purpose: TiKV time utility layer for monotonic clocks, Unix time conversion, slow-operation timers, time-jump monitoring, read stream IDs, and coarse-clock integration with `async_speed_limit`.

Important APIs/types/functions: `Timespec`, `Instant`, `UnixSecs`, `SlowTimer`, `Monitor`, `CoarseClock`, `Limiter`, `ThreadReadId`, conversion helpers, `setup_for_spin_interval`, and `spin_at_least`.

Control flow: Linux paths call `clock_gettime` for monotonic, raw, and coarse clocks; non-Linux paths emulate with a process-local `std::time::Instant` origin. `Instant` refuses comparisons across monotonic/coarse variants except equality false and `partial_cmp(None)`. `Monitor` periodically samples `SystemTime` and calls `on_jumped` if wall time moves backward.

State and persistence: no persistence. TLS stores per-thread read sequence; static mutable spin calibration is initialized once; monitor owns a background thread and shutdown channel.

Dependencies/integration: used by metrics, timers, scheduling, rate limiting, and transaction timestamp-related wall-clock helpers.

Risks: duration conversion can overflow for huge inputs; `to_std_duration` unwraps and therefore rejects negative `time::Duration`; static mutable spin calibration is intentionally guarded by `Once` but still unsafe.

Test signals: tests cover time monitor callbacks, conversions, monotonic ordering, instant arithmetic, SMP coarse-clock saturation, spin waits, and benchmarks for clock reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/time.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/timer.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/timer.rs

Purpose: timer utilities for sorted timeout tasks and global Tokio 0.1 timer handles, including a steady timer insulated from wall-clock adjustment.

Important APIs/types/functions: `Timer<T>`, `GLOBAL_TIMER_HANDLE`, `SteadyClock`, `SteadyTimer`, `RatchetClock`, and `start_timer_thread`.

Control flow: `Timer<T>` stores `TimeoutTask`s in a `BinaryHeap<Reverse<_>>` and pops tasks due before a supplied `Instant`. Global timer threads run `tokio_timer::Timer::turn` forever and return handles over a channel. `RatchetClock` clamps backwards movement at millisecond precision to avoid tokio-timer panics.

State and persistence: in-memory heaps, lazy-static global handles, and a background thread per global timer. Thread group properties are copied into timer threads.

Dependencies/integration: used by worker intervals, future workers, YATP cleanup tasks, and delay futures. Depends on `tokio_timer`, `tokio_executor`, and TiKV clock utilities.

Risks: timer threads are intentionally never joined; clock-family mismatches in `TimeoutTask` ordering would panic; `SteadyClock` instants are only comparable within the same zero origin.

Test signals: unit tests cover ordered task popping, global timer delay, steady delay, and ratchet behavior under an intentionally backward-moving clock.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/timer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/topn.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/topn.rs

Purpose: fixed-capacity collector for the largest `N` ordered values.

Important APIs/types/functions: `TopN<T>::new`, `push`, `pop`, `peek`, `len`, `is_empty`, and `IntoIterator`.

Control flow: values are wrapped in `Reverse<T>` inside a `BinaryHeap`, turning the heap top into the smallest retained value. Every push inserts first and pops once if length exceeds capacity.

State and persistence: in-memory heap only.

Dependencies/integration: general utility for bounded top-k calculations without sorting all inputs.

Risks: `pop` returns values from smallest retained to largest, not descending; `IntoIterator` is explicitly unordered; capacity zero accepts pushes then immediately discards them.

Test signals: tests cover zero capacity, one capacity, retained top values, pop order, and unordered iteration after sorting externally.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/topn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/future.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/worker/future.rs

Purpose: single-threaded future-aware worker abstraction backed by an unbounded futures mpsc channel and a current-thread Tokio runtime.

Important APIs/types/functions: `Runnable<T>`, `Scheduler<T>`, `Worker<T>`, `Stopped<T>`, `dummy_scheduler`, and internal `poll`.

Control flow: `Scheduler::schedule` sends `Some(task)` and increments pending metrics. The worker thread receives messages, runs `runner.run`, decrements pending, increments handled, and breaks on `None`; after the loop it calls `runner.shutdown`.

State and persistence: in-memory channel, worker join handle, metrics gauges/counters, and optional receiver protected by a `Mutex` to prevent double start.

Dependencies/integration: integrates with `tokio::task::LocalSet`, legacy `tokio_timer` futures, Prometheus worker metrics, and thread-group propagation.

Risks: scheduling increments metrics after successful send but `run` panics can skip decrements; `is_busy` really means not currently startable/handle missing, not queue saturation.

Test signals: tests cover asynchronous timer tasks executing concurrently and nested `block_on` inside the worker.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/future.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/metrics.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/worker/metrics.rs

Purpose: Prometheus metric definitions for classic workers.

Important APIs/types/functions: `WORKER_PENDING_TASK_VEC` and `WORKER_HANDLED_TASK_VEC`.

Control flow: lazy-static registration creates an `IntGaugeVec` labeled by worker name for pending plus running work and an `IntCounterVec` for completed tasks.

State and persistence: metric state is process-local and exported through Prometheus; no durable persistence.

Dependencies/integration: used by `worker/future.rs` and `worker/pool.rs` schedulers and runners.

Risks: metric labels depend on stable worker names; duplicated labels intentionally aggregate clones of the same scheduler.

Test signals: worker tests assert handled counts in timer-backed lazy workers; metric registration itself is not independently tested.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/mod.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/worker/mod.rs

Purpose: public module facade for TiKV background worker abstractions.

Important APIs/types/functions: re-exports classic pool workers (`Builder`, `Worker`, `Scheduler`, `Runnable`, `RunnableWithTimer`, `LazyWorker`) and future workers (`FutureWorker`, `FutureScheduler`, `FutureRunnable`, `Stopped`).

Control flow: this file mostly delegates to submodules. Its local tests exercise scheduling, threaded producers, worker shutdown, and pending capacity through the exported API surface.

State and persistence: no state in the module facade.

Dependencies/integration: gives downstream TiKV components a stable import path for worker APIs and hides submodule layout.

Risks: exported names overlap between classic and future workers, so aliases matter for callers; tests use sleeps around busy-state updates.

Test signals: module tests cover sequential handling, cross-thread scheduling, shutdown callbacks, and capacity errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/pool.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/worker/pool.rs

Purpose: YATP-backed worker pool abstraction for synchronous `Runnable` tasks, optional periodic timeouts, lazy workers, and generic async tasks.

Important APIs/types/functions: `ScheduleError`, `Runnable`, `RunnableWithTimer`, `Scheduler`, `LazyWorker`, `ReceiverWrapper`, `Builder`, and `Worker`.

Control flow: schedulers maintain an atomic pending counter and unbounded channel. `schedule` enforces `pending_capacity`; `schedule_force` bypasses it but still increments metrics and counter. `Worker::start_with_timer_impl` spawns an async loop in `FuturePool`, dispatching `Msg::Task` to `run` and `Msg::Timeout` to `on_timeout`, rescheduling timeouts via `GLOBAL_TIMER_HANDLE`.

State and persistence: in-memory YATP pool, atomics for stop/pending count, Prometheus metrics, and channels. `RunnableWrapper::drop` invokes `shutdown`.

Dependencies/integration: built on `yatp_pool::FuturePool`, global timer, Prometheus worker metrics, and TiKV future helpers.

Risks: pending counter is decremented only after `run`; panics can poison accounting. Timeout messages share the same channel as tasks and may be delayed behind workload. `is_busy` uses pending count versus core thread count, not actual executor availability.

Test signals: tests cover lazy timer workers, capacity failures, shutdown callbacks, interval timeout behavior, and handled-task metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/worker/pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/future_pool.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/future_pool.rs

Purpose: wraps a YATP future thread pool with TiKV metrics, task-count admission control, handle-returning spawn, and tracker TLS propagation.

Important APIs/types/functions: `FuturePool`, `PoolInner`, `Full`, `spawn`, `spawn_with_extras`, `spawn_handle`, `scale_pool_size`, `set_max_tasks_per_worker`, and `get_running_task_count`.

Control flow: spawns wrap futures in `TlsTrackedFuture`, infer task priority from YATP extras, gate against the running gauge for that priority, increment running before spawn, and use `FutureExt::map` to decrement running and increment handled at completion. `spawn_handle` sends the output through a oneshot channel.

State and persistence: in-memory YATP pool, atomic pool size and max task limit, and Prometheus gauges/counters.

Dependencies/integration: used by worker pool and YATP builder; depends on `tracker`, `yatp`, resource-control task priority, failpoints, and Prometheus.

Risks: admission checks use metric gauge values, so metric-accounting bugs can affect behavior; per-priority gating compares only the selected priority count to a global max; cancellation before execution must still reach the mapped completion path to decrement.

Test signals: tests cover ticker behavior, spawn handles, running counts, full-pool rejection, and scaling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/future_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/metrics.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/metrics.rs

Purpose: Prometheus metrics for YATP future pools and schedule latency.

Important APIs/types/functions: `FUTUREPOOL_RUNNING_TASK_VEC`, `FUTUREPOOL_HANDLED_TASK_VEC`, `YATP_POOL_SCHEDULE_WAIT_DURATION_VEC`, and `YATP_POOL_SCHEDULE_EXEC_DURATION_VEC`.

Control flow: lazy-static registration creates gauges/counters and histograms labeled by pool name and priority. Histogram buckets span roughly 10 microseconds to 42 seconds.

State and persistence: process metric state only.

Dependencies/integration: consumed by `future_pool.rs` and `yatp_pool/mod.rs` local histogram flushing.

Risks: label cardinality follows pool names and priority strings; changing names changes metric continuity.

Test signals: schedule wait histogram counts are asserted in YATP pool tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/mod.rs -->
# sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/mod.rs

Purpose: TiKV builder and runner integration for YATP pools, including lifecycle hooks, per-thread setup, task schedule latency metrics, priority/multilevel queues, cleanup scheduling, and periodic ticker callbacks.

Important APIs/types/functions: `CleanupMethod`, `PoolTicker`, `TickerWrapper`, `DefaultTicker`, `Config`, `TaskScheduleHistograms`, `YatpPoolRunner`, and `YatpPoolBuilder`.

Control flow: builders configure thread counts, stack, max tasks, queue type, cleanup strategy, hooks, and metrics. Runner `start` installs thread hooks, thread group properties, thread memory accessor, and allocator arena; `handle` records wait and execution durations around YATP future runner handling; `end` flushes ticker and removes thread bookkeeping.

State and persistence: in-memory pool configuration, local histograms flushed on ticks/end, optional cleanup futures scheduled locally or remotely.

Dependencies/integration: bridges `yatp`, TiKV resource control metadata, allocator hooks, thread maps, global timer, and worker pools.

Risks: local histogram flushing depends on task/tick activity; cleanup strategy changes where long-lived cleanup futures execute; hook closures must be thread-safe and non-panicking.

Test signals: tests cover schedule-wait recording and cleanup execution for in-place, local, and remote strategies.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tipb_helper/Cargo.toml -->
# sources/storage-engines/tikv/components/tipb_helper/Cargo.toml

Purpose: Cargo manifest for the private `tipb_helper` crate.

Important APIs/types/functions: declares package metadata and workspace dependencies on `codec`, `tidb_query_datatype`, and `tipb`.

Control flow: no runtime control flow; the manifest wires the helper crate into the workspace dependency graph.

State and persistence: build metadata only.

Dependencies/integration: supports expression protobuf construction used by query-related code and tests.

Risks: dependency versions are inherited from the workspace, so helper behavior tracks workspace-wide codec/datatype/tipb changes.

Test signals: no manifest-local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tipb_helper/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tipb_helper/src/expr_def_builder.rs -->
# sources/storage-engines/tikv/components/tipb_helper/src/expr_def_builder.rs

Purpose: fluent builder for `tipb::Expr` expression definitions.

Important APIs/types/functions: `ExprDefBuilder` constructors for integer, unsigned integer, real, bytes, decimal, time, duration, null, column reference, scalar function, and aggregate function; `push_child`; `build`; `From<ExprDefBuilder> for Expr`.

Control flow: each constructor creates a default `Expr`, sets `ExprType`, encodes literal bytes with TiKV/TiDB codec helpers, and fills `FieldType` metadata. `push_child` appends nested expressions and returns the builder for chaining.

State and persistence: no persistence; state is the owned protobuf expression under construction.

Dependencies/integration: depends on `codec`, TiDB query datatype accessors/codecs, and `tipb` protobuf types. Used to produce valid TiDB expression trees for coprocessor/query paths and tests.

Risks: constructors unwrap codec writes; incorrect field type metadata can produce expressions that decode but execute incorrectly; `column_ref` casts `usize` to `i64`.

Test signals: no direct tests in this file; validation is indirect via query expression consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tipb_helper/src/expr_def_builder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tipb_helper/src/lib.rs -->
# sources/storage-engines/tikv/components/tipb_helper/src/lib.rs

Purpose: crate facade for `tipb_helper`.

Important APIs/types/functions: private `expr_def_builder` module and public `ExprDefBuilder` re-export.

Control flow: no runtime behavior beyond module export.

State and persistence: none.

Dependencies/integration: gives callers a compact import path for expression construction helpers.

Risks: public surface is intentionally tiny; adding helpers requires preserving the builder’s protobuf correctness.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tipb_helper/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/Cargo.toml -->
# sources/storage-engines/tikv/components/tracker/Cargo.toml

Purpose: Cargo manifest for the private `tracker` crate.

Important APIs/types/functions: declares dependencies on `crossbeam-utils`, `kvproto`, `parking_lot`, `pin-project`, Prometheus, `slab`, `slog`, and supporting macros.

Control flow: build metadata only.

State and persistence: no runtime state; controls compilation and linkage.

Dependencies/integration: tracker bridges request metrics, protobuf response details, TLS propagation, and sharded slab storage.

Risks: dependency changes can affect pin projection, slab behavior, locking, or protobuf field availability.

Test signals: no manifest-local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/future.rs -->
# sources/storage-engines/tikv/components/tracker/src/future.rs

Purpose: generic future polling instrumentation wrapper.

Important APIs/types/functions: `FutureTrack`, `track`, and internal pinned `Tracker<F, T>`.

Control flow: wrapper calls `on_poll_begin`, polls the inner future, then calls `on_poll_finish` before returning the poll result.

State and persistence: wrapper owns the future and tracker object; no persistence.

Dependencies/integration: uses `pin-project` for safe projection and is suitable for recording per-poll timing or resource state around async execution.

Risks: `on_poll_finish` is skipped if the inner poll panics; tracker hooks must be cheap because they run on every poll.

Test signals: no local tests; used as a primitive by higher-level tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/future.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/lib.rs -->
# sources/storage-engines/tikv/components/tracker/src/lib.rs

Purpose: request tracker model and response-detail writers for TiKV request timing, RocksDB scan stats, write pipeline timing, and RU v2 accounting.

Important APIs/types/functions: `Tracker`, `RequestInfo`, `RequestType`, `RequestMetrics`, `merge_time_detail`, `write_scan_detail`, `write_write_detail`, and `write_ru_v2`.

Control flow: request code creates `RequestInfo` from `kvrpcpb::Context`, mutates metrics through TLS/slab access, then writes metrics into protobuf details. Some scan MVCC fields are filled only when currently unset to avoid clobbering coprocessor-provided stats.

State and persistence: per-request in-memory metrics; protobuf detail messages carry the final serialized results to clients/telemetry.

Dependencies/integration: re-exports future tracking, TLS helpers, and global tracker slab; integrates with `kvproto::kvrpcpb`.

Risks: several write-detail fields subtract related timestamps and can underflow if metrics are recorded out of order; metrics are public fields, so invariants are convention-based.

Test signals: unit tests cover MVCC scan stat idempotence and non-overwrite behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/metrics.rs -->
# sources/storage-engines/tikv/components/tracker/src/metrics.rs

Purpose: Prometheus metric for tracker slab capacity failures.

Important APIs/types/functions: `SLAB_FULL_COUNTER`.

Control flow: lazy-static registration creates a counter incremented when a tracker slab shard refuses insertion due to maximum capacity.

State and persistence: process-local Prometheus counter only.

Dependencies/integration: used by `slab.rs` insert failure path.

Risks: failure means the request loses tracker detail while continuing with `INVALID_TRACKER_TOKEN`; alerting depends on this counter being scraped.

Test signals: no direct metric test.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/slab.rs -->
# sources/storage-engines/tikv/components/tracker/src/slab.rs

Purpose: global sharded slab storage for active request trackers, addressed by compact tokens safe against stale key reuse.

Important APIs/types/functions: `GLOBAL_TRACKERS`, `ShardedSlab`, `TrackerSlab`, `TrackerToken`, `INVALID_TRACKER_TOKEN`, and `TrackerTokenArray`.

Control flow: `insert` chooses a shard using a thread-local round-robin counter, inserts into a `slab::Slab`, and builds a token from shard id, sequence, and slab key. `with_tracker` and `remove` validate both key and sequence before returning/mutating a tracker.

State and persistence: process-local 64-shard slab protected by cache-padded `parking_lot::Mutex` values. No durable persistence.

Dependencies/integration: used by TLS tracker propagation and slog serialization of tracker token arrays.

Risks: shard capacity is capped at 4096 and insert failure silently returns `INVALID_TRACKER_TOKEN` after incrementing a metric; sequence bits can wrap eventually, so stale-token protection is probabilistic over very long runtimes.

Test signals: tests cover token bit packing, basic insert/get/remove/iteration, and sharding distribution across threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/slab.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/tls.rs -->
# sources/storage-engines/tikv/components/tracker/src/tls.rs

Purpose: thread-local active tracker token management and future wrapper that propagates that token while polling.

Important APIs/types/functions: `set_tls_tracker_token`, `clear_tls_tracker_token`, `get_tls_tracker_token`, `with_tls_tracker`, and `TlsTrackedFuture`.

Control flow: callers set a token in TLS; `with_tls_tracker` resolves it through `GLOBAL_TRACKERS`. `TlsTrackedFuture::new` captures the current TLS token, and each poll temporarily installs it, polls the inner future, then clears TLS.

State and persistence: per-thread `Cell<TrackerToken>` only.

Dependencies/integration: used by `tikv_util::yatp_pool::FuturePool` to preserve request tracker context across executor threads.

Risks: TLS is cleared after every poll, so nested code must rely on the wrapper; panics during poll skip the clear path. Invalid tokens are treated as no tracker.

Test signals: no local tests; behavior is indirectly exercised by future pool tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tracker/src/tls.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/Cargo.toml -->
# sources/storage-engines/tikv/components/txn_types/Cargo.toml

Purpose: Cargo manifest for the private `txn_types` crate.

Important APIs/types/functions: declares package metadata, runtime dependencies for encoding, protobufs, errors, hashing, logging, allocation, and TiKV utilities, plus test dependencies.

Control flow: build metadata only.

State and persistence: no runtime state; controls the transaction type crate’s compilation.

Dependencies/integration: this crate is shared by storage, MVCC, lock, and write paths.

Risks: codec and protobuf dependency changes can alter persistent lock/write wire compatibility.

Test signals: no manifest-local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/lib.rs -->
# sources/storage-engines/tikv/components/txn_types/src/lib.rs

Purpose: public facade and error model for TiKV transaction types.

Important APIs/types/functions: re-exports lock, timestamp, key/value/mutation, and write types; defines `ErrorInner`, `Error`, `Result`, `maybe_clone`, `ErrorCodeExt`, and `ENABLE_DUP_KEY_DEBUG`.

Control flow: errors convert from I/O, codec, lock/write format, key lock, write conflict, and invalid operation variants. `ErrorCodeExt` maps each variant to storage error codes for downstream handling.

State and persistence: no persisted state, but error variants carry transaction keys, timestamps, lock info, and reasons across API boundaries.

Dependencies/integration: central import point for storage transaction code and clients needing typed transaction errors.

Risks: specialization-based generic `From<T>` requires nightly features; `maybe_clone` intentionally cannot clone I/O errors.

Test signals: no direct tests in this file; exported modules have focused tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/lock.rs -->
# sources/storage-engines/tikv/components/txn_types/src/lock.rs

Purpose: transaction lock model, persistent lock encoding/decoding, shared-lock container, pessimistic-lock compact representation, and lock conflict checks.

Important APIs/types/functions: `LockType`, `Lock`, `SharedLocks`, `PessimisticLock`, `TxnLockRef`, `LockInfoExt`, `LockOrSharedLocks`, `decode_lock_type`, `decode_lock_start_ts`, `parse_lock`, `check_ts_conflict`, and `check_ts_conflict_for_replica_read`.

Control flow: `Lock::to_bytes` writes a legacy prefix followed by ordered tagged fields such as for-update ts, txn size, min commit ts, async commit secondaries, rollback timestamps, last-change metadata, txn source, conflict flag, and generation. Parsing reads known tags and stops at unknown bytes for forward compatibility. Conflict checks ignore non-conflicting lock types, future/min-commit locks, bypassed start timestamps, and selected latest-primary reads, otherwise returning key-lock or write-conflict errors.

State and persistence: lock bytes are persisted in TiKV lock CF. `SharedLocks` persists multiple lock segments under one shared-lock record and lazily parses segment bytes into `Lock` values on access. `PessimisticLock` is an in-memory compact representation convertible to persisted `Lock`.

Dependencies/integration: depends on TiKV codec helpers, `kvproto::kvrpcpb::LockInfo`, transaction keys/mutations, `TimeStamp`, `TsSet`, and logging redaction wrappers.

Risks: lock encoding is compatibility-sensitive; unknown tags require ordered serialization. `SharedLocks::into_lock_info` unwraps segment parsing. Conflict behavior around `TimeStamp::max`, async commit, one-PC, and replica reads is correctness-critical.

Test signals: extensive tests cover lock type conversion, encode/decode round trips, bad input, unknown-byte forward compatibility, SI and RC conflict behavior, redacted debug output, pessimistic conversion/memory sizing, shared-lock operations, shrink-only enforcement, duplicate insert, and update errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/timestamp.rs -->
# sources/storage-engines/tikv/components/txn_types/src/timestamp.rs

Purpose: timestamp wrapper and small immutable timestamp-set abstraction for transaction code.

Important APIs/types/functions: `TimeStamp`, `TSO_PHYSICAL_SHIFT_BITS`, `compose`, `physical`, `logical`, `next`, `prev`, `incr`, `decr`, `physical_now`, and `TsSet`.

Control flow: `TimeStamp` is a transparent `u64` wrapper whose high bits encode physical milliseconds and low 18 bits encode logical counter. `TsSet::new` chooses empty, small `Arc<[TimeStamp]>`, or `Arc<HashSet<TimeStamp>>` representation based on size; `contains` dispatches to the chosen representation.

State and persistence: timestamps are value types persisted throughout MVCC/lock/write metadata. `TsSet` is immutable shared in memory through `Arc`.

Dependencies/integration: used by lock conflict bypass sets, key timestamp parsing tests, transaction metadata, and heap-size accounting.

Risks: `next/prev/incr/decr` assert at bounds; unsafe vector transmute from `Vec<u64>` depends on transparent representation; `physical_now` unwraps system time since Unix epoch.

Test signals: tests cover physical/logical splitting, key timestamp split integration, and all `TsSet` representations/contains behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/txn_types/src/timestamp.rs -->
