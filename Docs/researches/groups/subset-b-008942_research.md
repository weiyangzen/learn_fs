# subset-b-008942 Transaction Scheduler Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/mod.rs -->
# sources/storage-engines/tikv/src/storage/txn/mod.rs

## Purpose
`mod.rs` is the public facade for TiKV's transactional storage module. It wires together transaction actions, command types, latches, scheduler, store abstractions, and transaction status cache support. It also defines the shared transaction `Result` and `Error` types and the `ProcessResult` enum that moves command outcomes between command processors, the scheduler, callbacks, and resumed command flows.

## Important APIs, types, and functions
The module exports submodules `commands`, `flow_controller`, `sched_pool`, `scheduler`, and `txn_status_cache`, while keeping `actions`, `latch`, `store`, `task`, and `tracker` private. Public re-exports expose the action entry points used by command handlers: pessimistic lock acquisition, cleanup, commit, flashback-to-version phases, GC, prewrite, transaction property types, `Command`, `TxnScheduler`, `Latches`, `Lock`, and store/scanner helper types.

`ProcessResult` is the central result carrier. It covers unit success, multi-result batches, prewrite details, MVCC introspection, lock lists, transaction status, chained `NextCommand`, error failures, pessimistic lock key results, secondary-lock status, and raw compare-and-swap responses. `ProcessResult::maybe_clone` intentionally clones only the successful pessimistic-lock response shape currently needed by scheduler side paths. `ProcessResult::get_key_lock_info` recognizes the nested storage/txn/MVCC `KeyIsLocked` error inside `PessimisticLockRes`, allowing scheduler logic to detect shared-lock update cases.

`ErrorInner` normalizes lower-level failures from the KV engine, codec, protobuf, MVCC, IO, concurrency-manager max-ts updates, and scheduler-specific validation cases. `Error::from_mvcc`, `Error::maybe_clone`, and the blanket `From<T: Into<ErrorInner>>` implementation make command code concise. `ErrorCodeExt` maps each variant to TiKV storage error codes used by diagnostics and client-facing response conversion.

## Control flow
Most execution flow enters through re-exported `Command` and `TxnScheduler`. Command handlers return `ProcessResult` and `Result<T>` values defined here. Errors propagate upward as `Error`, then are wrapped by storage-level errors in scheduler callbacks. The `NextCommand` result supports multi-phase operations by allowing read or write completion handlers to schedule a new command with the same callback.

The test-only `tests` module re-exports helper functions from action test modules, which gives downstream storage tests a stable namespace for common assertions such as must-prewrite, must-commit, must-cleanup, lock checks, and GC success.

## State and persistence behavior
This file does not maintain persistent state or write to storage directly. Its state role is representational: it defines process-result variants and error variants that describe persistent effects performed elsewhere. Variants such as `MaxTimestampNotSynced`, `RawKvMaxTimestampNotSynced`, `FlashbackNotPrepared`, and `InvalidReqRange` capture correctness gates around timestamp freshness, flashback region state, and physical snapshot bounds.

## Dependencies and integration points
The module integrates `kvproto::kvrpcpb::LockInfo`, transaction key/value/timestamp types from `txn_types`, TiKV storage error and MVCC error types, protobuf and codec errors, and `error_code` mappings. Its re-exports are consumed throughout storage command implementations and tests, so variant shape and public exports are part of a broad internal API surface.

## Risks and edge cases
The nested pattern in `get_key_lock_info` is brittle because it depends on the exact layering of storage, transaction, and MVCC errors. `maybe_clone` deliberately returns `None` for protobuf, IO, and boxed dynamic errors because they are not safely cloneable; callers must be prepared for non-cloneable errors. The blanket `From` implementation is convenient but can obscure which lower-level error conversion path was selected. Adding a new `ErrorInner` variant requires updating `maybe_clone` and `error_code` mappings or error reporting will lose fidelity.

## Test signals
There are no direct tests for `ProcessResult` or `ErrorCodeExt` in this file. Coverage comes from action tests re-exported under `txn::tests` and from scheduler/store tests that construct or inspect `ProcessResult` and transaction errors. Useful additional checks would assert `get_key_lock_info` on `KeyIsLocked`, `maybe_clone` behavior for cloneable and non-cloneable variants, and exact error-code mapping for newer variants such as raw max-ts freshness and invalid max-ts update.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/sched_pool.rs -->
# sources/storage-engines/tikv/src/storage/txn/sched_pool.rs

## Purpose
`sched_pool.rs` builds and manages the transaction scheduler worker pools. It hides whether tasks run on traditional high/normal priority pools or a resource-control-aware priority pool, initializes scheduler-thread TLS state, and batches per-thread metrics before flushing them to Prometheus and PD flow-stat reporters.

## Important APIs, types, and functions
`SchedLocalMetrics` stores thread-local scan statistics keyed by command name, a local key-read histogram vector, and local `WriteStats`. `TLS_SCHED_METRICS` owns those accumulators per scheduler worker thread. `TLS_FEATURE_GATE` stores the feature-gate snapshot that command execution checks through `tls_can_enable`.

`SchedTicker<R>` implements `PoolTicker::on_tick` and calls `tls_flush`, making metric flushes part of Yatp pool ticking. `QueueType` selects `Vanilla` or `Dynamic` queue behavior. `VanillaQueue` wraps separate `FuturePool`s for high-priority and normal/low-priority commands. `PriorityQueue` wraps a priority future pool plus `ResourceController` and `ResourceGroupManager`; it converts command priority into Yatp multilevel extras and wraps futures in `ControlledFuture` plus a resource limiter.

`SchedPool::new` builds all pools with `YatpPoolBuilder`, setting thread counts, names, task wait/exec metrics, TLS engine initialization, foreground-write IO type, TLS feature-gate initialization, TLS engine teardown, and final metric flush on worker stop. `SchedPool::spawn` dispatches according to `QueueType` and whether resource control is currently customized. `scale_pool_size` and `get_pool_size` expose dynamic sizing. TLS helpers collect scan details, key-read histograms, PD query counts, and feature-gate checks.

## Control flow
Scheduler code submits every command future through `SchedPool::spawn`, passing request source, resource metadata, command priority, and write-byte estimate. In vanilla mode high-priority commands use the high-priority pool, all others use the regular pool. In dynamic mode, if resource control is customized, tasks enter the priority pool with metadata and resource limiter; otherwise they fall back to vanilla routing.

When a scheduler worker starts, it installs a cloned engine into TLS, sets IO type to foreground write, and copies the feature gate to TLS. Command execution accumulates statistics through TLS helper functions. On pool ticks and worker shutdown, `tls_flush` drains those local values into global metrics and reports write stats to PD.

## State and persistence behavior
This file does not directly persist user data. It manages execution state for scheduler worker pools and per-thread metrics. The TLS engine pointer is critical process state: command execution later uses `with_tls_engine` and relies on the pool's `after_start`/`before_stop` invariants. Local write stats become PD flow-stat reports, which affect load reporting and scheduling outside this file.

## Dependencies and integration points
The pool integrates `tikv_util::yatp_pool`, `yatp::queue::Extras`, resource-control futures and managers, PD feature gates, raftstore write stats, file-system IO tagging, storage engines, and storage metrics. Thread-name constants make these pools visible in diagnostics. It is consumed by `TxnScheduler` for normal command execution, delayed admission-control tasks, lock-wait wakeups, and async background work.

## Risks and edge cases
`PriorityQueue::spawn` unwraps UTF-8 conversion of the resource group name with a default fallback, so invalid metadata silently maps to the default group. `SchedPool::new` unwraps `resource_mgr` when `resource_ctl` is present; callers must pass both together. Dynamic mode can switch back to vanilla when the resource controller is not customized, so behavior depends on runtime resource-control state rather than only construction-time configuration. TLS engine setup and teardown rely on generic type consistency; the comments explicitly mark the safety invariant.

Metric flushing is opportunistic through pool ticks and stop hooks. If a thread is busy for a long time, local metric visibility can lag. `PriorityQueue` currently uses random task IDs, so task identity is not stable across retries or logs.

## Test signals
No tests live in this file. Indirect coverage comes from scheduler tests that run commands through the pool and from resource-control integration tests elsewhere. Valuable direct tests would cover queue selection in vanilla versus dynamic mode, fallback when resource control is not customized, pool scaling for high-priority and normal pools, TLS feature-gate replacement, and that `tls_flush` drains scan details and write stats exactly once.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/sched_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/scheduler.rs -->
# sources/storage-engines/tikv/src/storage/txn/scheduler.rs

## Purpose
`scheduler.rs` implements `TxnScheduler`, the core transaction command scheduler for TiKV storage. It receives client commands, applies admission and flow-control checks, serializes conflicting command-level access through latches, obtains snapshots, dispatches read/write command processing to worker futures, coordinates lock-wait/resume behavior for pessimistic transactions, submits writes to the engine/raftstore, and delivers callbacks.

## Important APIs, types, and functions
`TxnScheduler<E, L>` is the public scheduler handle. `TxnSchedulerInner<L>` contains sharded task slots, command ID allocation, `Latches`, `SchedPool`, resource-control handles, write-byte counters, flow controller, lock manager, concurrency manager, dynamic pessimistic-lock flags, lock-wait queues, quota limiter, feature gate, transaction status cache, and scheduler memory quota.

`TaskContext` is the in-flight command record. It stores the optional `Task`, latch `Lock`, callback, optional early process result, resumable lock-wait entries woken by released locks, ownership bit, write-byte estimate, command tag, latch timer, and command timer. The atomic `owned` bit prevents races among normal processing, fail-fast precheck, deadline timeout, and early callback paths.

`SchedulerTaskCallback` wraps either a normal storage callback or per-key pessimistic-lock callbacks. `CmdTimer` and `SchedulerDetails` record command and stage timings. `PessimisticLockMode` selects sync, pipelined, or in-memory pessimistic-lock behavior. `get_raw_ext` obtains causal timestamps and key guards for raw compare-and-swap or atomic store commands when API v2 causal-ts support is available.

Major scheduler methods include `run_cmd`, `schedule_command`, `execute`, `process`, `process_read`, `process_write`, `handle_task`, `handle_non_persistent_write_result`, `handle_flow_control`, `handle_async_write`, `on_read_finished`, `on_write_finished`, `finish_with_err`, lock-wait helpers, and wake-up helpers.

## Control flow
`run_cmd` is the command entry point. It first rejects writes when scheduler pending bytes or flow-controller drop logic says the store is too busy. It then asks resource-control admission whether to reject or delay. Delayed commands are re-submitted after sleeping without holding latches. Accepted commands receive a new command ID and are wrapped in `Task::allocate`, which charges scheduler memory quota.

`schedule_command` inserts a `TaskContext`, records metrics and request-tracker fields, and tries to acquire the command's generated latches. If all required latches are acquired, it calls `execute`. If not, it starts fail-fast/precheck/deadline monitoring. The deadline path can take the callback early through `try_own_and_take_cb`; the task remains queued until latch wake-up so latches can be released consistently later.

`execute` installs the tracker token in TLS, starts a tracked future on the scheduler pool, gets an engine snapshot, copies snapshot term and extra operation metadata into the command, claims task ownership, and calls `process`. Read commands execute `Task::process_read`, collect statistics, and finish through `on_read_finished`. Write commands execute `handle_task`, which builds `WriteContext`, gets raw causal-ts extensions if needed, calls the command's write processor, accounts read/write quota samples, and returns `WriteResult`.

`process_write` checks deadlines and duplicate-lock debug conditions, handles non-persistent effects, then either finishes without raftstore persistence or proceeds to flow control and `handle_async_write`. `handle_async_write` configures disk-full behavior and response subscriptions, marks in-memory pessimistic locks as deleted before submitting lock-CF writes, calls engine `async_write`, performs early response on committed/proposed events for async-apply-prewrite or pipelined pessimistic locking, and performs final cleanup on `Finished`.

Completion handlers dequeue `TaskContext`, update status cache for known committed transactions, execute callbacks, wake pessimistic lock waiters when released locks allow it, put back deferred wait entries if needed, and release latches. `release_latches` wakes queued command IDs and `try_to_wake_up` reacquires latches or fails expired tasks through the pool to avoid recursive stack growth.

## State and persistence behavior
Persistent mutations are not built directly in this file; command processors produce `WriteData`, and the scheduler decides whether and when to submit it. It can avoid persistence for eligible pessimistic locks by inserting lock-CF modifies into raftstore `TxnExt` in-memory pessimistic-lock tables when feature gates and size limits allow. It can also skip immediate client waiting for persistence in pipelined or async-apply modes, but final latch release and cleanup still wait for the async write finish event.

In-memory state includes sharded task slots, latch queues, running write-byte counters, lock-wait queues, memory quota allocations, status cache inserts, and per-request tracker metrics. Flow control consumes write bytes before async write; failed writes unconsume to prevent quota exhaustion. Known transaction statuses are inserted into `TxnStatusCache` before callbacks are invoked.

## Dependencies and integration points
The scheduler sits at the center of storage integration. It depends on storage engines and snapshots, raftstore `TxnExt`, concurrency manager key guards, lock manager wait APIs, lock-wait queues, transaction command processors, MVCC errors, latches, resource metering and resource control, quota limiter, flow controller, PD query stats, tracker metrics, Yatp scheduler pool, feature gates, failpoints, and kvproto request context. It is called from higher storage service code through `TxnScheduler::run_cmd` and calls back through `StorageCallback`.

## Risks and edge cases
Correctness depends on precise ordering: wait entries are pushed to scheduler lock-wait queues before calling the lock manager so cancellation does not race with wake-up; in-memory pessimistic locks are marked deleted before raftstore submission and physically removed only after apply succeeds; early callbacks do not release latches until final write completion. Undetermined async write results panic because releasing latches would risk violating correctness, while retaining them would deadlock later transactions.

The ownership bit is essential but subtle. Races among snapshot completion, deadline timers, precheck errors, and early pipeline responses must leave exactly one callback owner. Flow-control delay checks command deadlines in a loop and must unconsume bytes on timeout. `handle_non_persistent_write_result` has special cases for lock wait, resumed lock wait, shared-lock updates, and in-memory lock eligibility. Feature-gated `InMemory` mode requires both pipelined and in-memory flags plus feature support; otherwise it falls back to pipelined or sync behavior.

Resource-control admission delay intentionally happens before latch acquisition, preventing delayed commands from blocking overlapping writers. Memory quota is charged both for command heap size in `Task::allocate` and force-charged for the spawned execution future, then freed on future completion. The debug duplicate-lock check can panic in production if enabled, so it is guarded by `ENABLE_DUP_KEY_DEBUG`.

## Test signals
The local tests cover latch serialization for read/write command classes, deadline expiration while waiting on latches, fail-fast precheck for queued commands, expired commands before pool availability, flow-control timeout and unconsume behavior, avoiding stack overflow when many expired commands wake, pessimistic-lock mode selection and feature gating, forcing shared-lock updates to persist instead of using in-memory locks, and scheduler memory-quota rejection/freeing. These tests exercise many scheduler state transitions but do not fully cover async write event ordering, lock-manager cancellation races, raw causal-ts extension failures, or resource-control dynamic priority routing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/scheduler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/store.rs -->
# sources/storage-engines/tikv/src/storage/txn/store.rs

## Purpose
`store.rs` defines read abstractions used by transaction command implementations. It provides point-get, batch-get, scan, and transaction-entry scan traits, implements them for MVCC snapshots through `SnapshotStore`, and supplies `FixtureStore` plus `FixtureStoreScanner` for deterministic tests. It also defines `TxnEntry` and `EntryBatch` for scanning raw transactional entries such as prewrite and commit records.

## Important APIs, types, and functions
`Store` exposes `get_entry`, `get`, `incremental_get_entry`, incremental statistics/newer-ts state accessors, `batch_get`, and `scanner`. `Scanner` exposes `next_entry`, `next`, `scan`, `met_newer_ts_data`, and `take_statistics`. `scan` returns per-row errors for MVCC `KeyIsLocked` while treating other errors as scan-ending failures.

`TxnEntryStore` and `TxnEntryScanner` support entry-level scans with `entry_scanner` and `scan_entries`. `TxnEntry` has `Prewrite` and `Commit` variants, stores default/write/lock KV pairs plus `OldValue`, can erase last-change metadata for comparison, can convert committed entries into user-facing key/value pairs, can derive the logical key, and can estimate encoded size. `EntryBatch` is a small capacity-bound container for transaction entries.

`SnapshotStore<S>` is the production implementation over a `Snapshot`. It stores the snapshot, read timestamp, isolation level, fill-cache flag, bypass/access lock timestamp sets, newer-ts checking flag, and an optional cached `PointGetter` for incremental gets. `FixtureStore` wraps an ordered map from `Key` to `Result<ValueEntry>`.

## Control flow
Production point gets build a fresh `PointGetter` with the current snapshot, start timestamp, isolation level, fill-cache setting, bypass locks, and access locks, then merge point-getter statistics into the caller's statistics. Incremental gets lazily build and reuse a `PointGetter` to preserve cursor locality and expose accumulated stats. Batch gets reuse one point getter across input keys and push per-key statistics after each lookup.

Production scanners first call `verify_range` to ensure requested bounds fit inside the physical snapshot bounds. They then build an MVCC `Scanner` with direction, key-only mode, cache behavior, isolation level, lock bypass/access sets, newer-ts checking, load-commit-ts behavior, and bounds. Entry scanners similarly verify bounds, translate `after_ts` into optional min/max timestamp hints, and build an MVCC entry scanner.

`FixtureStore::scanner` translates requested lower/upper bounds into `BTreeMap` range bounds, adjusts inclusivity depending on forward versus reverse scans, optionally strips values for key-only mode, clones cloneable errors through `maybe_clone`, and reverses the collected vector for descending scans. `FixtureStoreScanner::next_entry` returns entries in that prepared order.

## State and persistence behavior
This file is read-only with respect to the underlying engine. `SnapshotStore` reads MVCC state at `start_ts` and tracks only local cursor/statistics state in `point_getter_cache`. `load_commit_ts` changes whether returned `ValueEntry` includes commit timestamps and intentionally skips `access_locks` inside MVCC point-getter behavior to obtain a valid commit timestamp. `check_has_newer_ts_data` allows callers to detect whether data newer than the read timestamp was encountered.

`TxnEntry` represents persisted MVCC artifacts from the default, lock, and write column families. `erasing_last_change_ts` is a normalization helper for cases where last-change timestamps should not affect equality or output comparison.

## Dependencies and integration points
The module depends on kvproto isolation levels, `txn_types` key/value/write encodings, MVCC point getter/scanner/entry scanner builders, storage snapshot and statistics traits, and transaction error types from `mod.rs`. It is used by command action implementations for reads, scans, lock checking, MVCC introspection, flashback-like entry iteration, and tests.

## Risks and edge cases
Range verification treats an empty physical lower or upper bound as unbounded. Upper-bound verification rejects requests whose encoded upper bound is greater than the physical upper bound or empty when the physical bound is not empty. Incorrect bound handling would risk leaking keys outside a region snapshot. `TxnEntry::into_kvpair` and `to_key` are only valid for `Commit` and deliberately `unreachable!` for `Prewrite`; callers must not use them on prewrite entries.

`Scanner::scan` preserves `KeyIsLocked` as an item-level error but aborts on other errors. Fixture scanning comments note that MVCC behavior is not guaranteed after non-lock errors; tests encode that caveat. `FixtureStore::clone` requires errors to be cloneable through `maybe_clone`, so fixtures containing non-cloneable errors would panic.

## Test signals
Tests build a Rocks-backed `TestStore`, prewrite and commit deterministic keys, and assert point gets, `get_entry` commit-ts loading, batch gets, forward scans, reverse scans, bounded scans, and scanner physical-bound rejection. Fixture tests cover missing keys, embedded NUL-like raw keys, cloneable lock and bad-format errors, key-only scans, forward and reverse range behavior, and commit-ts preservation. `test_txn_entry_size` validates size accounting for prewrite/commit entries with and without old values. Benchmarks measure fixture get, batch get, scanner creation, next, and scan loops.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/task.rs -->
# sources/storage-engines/tikv/src/storage/txn/task.rs

## Purpose
`task.rs` defines the scheduler's `Task` wrapper around a transaction `Command`. It attaches a command ID, tracker token, optional raft snapshot extra operation, and memory-quota ownership to command execution. The wrapper provides the narrow dispatch points used by the scheduler to process read and write commands once a snapshot is available.

## Important APIs, types, and functions
`Task` stores `cid`, `tracker_token`, `cmd: Option<Command>`, `extra_op: ExtraOp`, and optional `OwnedAllocated` memory quota. `Task::allocate` is the normal constructor. It captures the current TLS tracker token, computes command approximate heap size, reserves that amount from `MemoryQuota`, updates the scheduler memory metric, and returns `MemoryQuotaExceeded` if the command cannot be admitted. `Task::force_create` bypasses quota accounting for internally generated reschedule commands and is documented as a temporary special case.

Accessors expose command ID, tracker token, immutable/mutable command references, and extra operation. `set_extra_op` records snapshot-provided `ExtraOp` after snapshot acquisition and before command processing. `process_write` consumes the command and calls `Command::process_write` with a snapshot and `WriteContext`; `process_read` consumes the command and calls `Command::process_read` with a snapshot and mutable statistics.

## Control flow
`TxnScheduler::run_cmd` creates tasks with `Task::allocate`. Once latches are acquired and a snapshot is fetched, `TxnScheduler::execute` updates the command context from snapshot metadata, calls `set_extra_op`, and then delegates to `process_read` or `process_write` through the scheduler's higher-level flow. When read/write processing begins, the command is taken out of the `Option`, ensuring a task is processed once.

Internal scheduler paths such as `NextCommand` scheduling and resumed pessimistic-lock commands use `force_create`, avoiding a second quota charge for transitional commands until the surrounding scheduler callback flow is refactored.

## State and persistence behavior
The task itself does not persist data. Its `OwnedAllocated` field is stateful: memory remains charged while the task exists and is freed automatically when the task is dropped. This allows queued commands blocked on latches to consume quota and prevents unbounded request accumulation. `extra_op` carries snapshot transaction-extra behavior into write processing, where command handlers may include old-value or CDC-related extra data in `WriteData`.

## Dependencies and integration points
`Task` depends on `Command`, `WriteContext`, `WriteResult`, `ProcessResult`, engine snapshots, lock managers, storage statistics, memory quota utilities, tracker TLS, kvproto `ExtraOp`, and scheduler memory metrics. It is private to the transaction scheduler module and forms the boundary between scheduling mechanics and command execution.

## Risks and edge cases
Both `cmd()` and `cmd_mut()` unwrap the command option, and `process_read`/`process_write` take it. Any attempt to inspect a task after processing would panic. `force_create` intentionally skips quota accounting, so expanding its use beyond reschedule flows could bypass scheduler memory backpressure. `allocate` updates the in-use metric after successful allocation; future allocation or drop paths must keep that metric aligned with quota state.

## Test signals
`test_alloc_memory_quota` converts a default prewrite request into a command, allocates a task against a large quota, asserts quota usage becomes nonzero, drops the task, and asserts quota returns to zero. Scheduler tests in `scheduler.rs` further verify that queued commands are rejected under configured memory quota and that quota is freed after completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/task.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/tracker.rs -->
# sources/storage-engines/tikv/src/storage/txn/tracker.rs

## Purpose
`tracker.rs` implements `TlsFutureTracker`, a `tracker::FutureTrack` adapter that measures scheduler future active poll time and suspended-between-polls time. It exists because scheduler callbacks may be invoked inside future polling, and TiKV wants request trackers to contain accurate timing before callbacks hand details back to the gRPC layer.

## Important APIs, types, and functions
`PollState` records whether timing has been collected, a poll began at an `Instant`, or a poll finished at an `Instant`. `State` stores the tracker token, command kind tag, command ID, current poll state, accumulated future process nanoseconds, and accumulated suspend nanoseconds. `CURRENT_STATE` is TLS holding the state for the currently polled future.

`TlsFutureTracker::new` creates a tracker in `Finished(now)` state so the wait before the first poll is counted as suspend time. `TlsFutureTracker::collect_to_tracker` reads the TLS current state, folds any active poll duration into accumulated process time, adds accumulated process/suspend nanoseconds to the provided global tracker, resets the accumulators, and marks the state as `Collected` to avoid double counting before the poll finish hook.

`State::on_poll_begin` accounts suspend time from the previous finish to the new begin. `State::on_poll_finish` accounts active process time and writes it into the request tracker. The `FutureTrack` implementation moves state between the wrapper and TLS on poll begin/finish and uses `GLOBAL_TRACKERS.with_tracker` to update the global tracker by token.

## Control flow
Scheduler futures are wrapped with `tracker::track(future, TlsFutureTracker::new(...))`. On every poll begin, the wrapper takes its state, accounts any suspend interval, sets state to `Began(now)`, and installs it into TLS. Code inside the future can call `TlsFutureTracker::collect_to_tracker` just before a callback, which updates request metrics while the future is still polling. On poll finish, the TLS state is removed, process time is collected if it was not already collected, state is set to `Finished(now)`, and moved back into the wrapper for the next poll.

## State and persistence behavior
This module maintains only in-memory timing state. It updates `tracker.metrics.future_process_nanos` and `tracker.metrics.future_suspend_nanos`, which later feed request execution details. It does not interact with storage persistence.

## Dependencies and integration points
The implementation depends on `tikv_util::time::Instant`, the external `tracker` crate's `FutureTrack`, `GLOBAL_TRACKERS`, and `TrackerToken`, plus storage `CommandKind` for debugging messages. `TxnScheduler` uses it around futures submitted to `SchedPool` and calls `collect_to_tracker` before early responses, normal completions, and error completions.

## Risks and edge cases
The state machine intentionally panics on impossible poll ordering, missing TLS state, double TLS installation, or missing wrapper state. This catches nested or incorrectly tracked futures but makes misuse fail hard. `collect_to_tracker` expects to be called only while a tracked future is polling and TLS state is present. If the global tracker has already been removed, the poll-finish path simply cannot update it, but direct collection into a provided standalone tracker still works when TLS state exists.

The `Collected` state prevents double counting when collection happens inside a poll before the poll finish hook. Future suspend time includes wall-clock time before the first poll and between polls; process time includes wall-clock time spent inside polls and can include blocking work done during a poll.

## Test signals
`test_tracker` wraps a oneshot future, forces two polls with sleeps, calls `collect_to_tracker` inside the second poll, and asserts suspend time covers the waiting/sleep interval while process time covers only the intended in-poll work. `test_no_tracker` removes the global tracker before completion, verifies collection does not depend on the token being live for standalone tracker use, and asserts TLS state is cleared after completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/tracker.rs -->
