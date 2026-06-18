# subset-b-008268 research

Grouped source-tree-aligned research for the RustFS lock fast-lock/namespace modules and selected madmin models. Each source file section is delimited for deterministic reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/guard.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/guard.rs

Purpose: `guard.rs` defines the RAII ownership layer for the fast object lock system. `FastLockGuard` represents one acquired object lock and releases it on `Drop`; `MultipleLockGuards` is a container for batch acquisitions that should be held and released together.

Important APIs/types/functions: `FastLockGuard::new` constructs enabled guards with a shard reference, records read/write held metrics, and assigns a monotonically increasing `guard_id` from `GUARD_ID_COUNTER`. `FastLockGuard::new_disabled` creates guards for globally disabled locks and deliberately has no shard. The public inspection methods expose `key`, `mode`, `owner`, `is_released`, `is_disabled`, `guard_id`, and `lock_info`. `release` is the explicit early-release path and calls `LockShard::release_lock_with_guard`. `Drop` mirrors release for still-active enabled guards. `MultipleLockGuards` exposes collection construction, merging, iteration, `release_all`, `active_count`, key extraction, mode splitting, bucket/owner filtering, and conversion from individual or vector guards.

Control flow: normal acquisition happens in `manager.rs`; once a shard acquisition succeeds, the manager creates a `FastLockGuard` and registers the guard id on the shard. Manual `release` first checks the guard's local `released` bit, handles disabled guards as a successful no-op, then delegates to the shard using `(key, owner, mode, guard_id)`. On success it marks the guard released, records held-lock release metrics, and unregisters the guard. Dropping an unreleased guard repeats the shard release and always unregisters afterward, logging only at debug level if the shard says release failed.

State and persistence behavior: state is in memory only. The guard owns cloned `ObjectKey`, `LockMode`, `Arc<str>` owner, optional `Arc<LockShard>`, a boolean release flag, a disabled flag, and a guard id. No lock state is persisted; dropping a process would lose all state. The guard id is local process state and is used as a double-release token in `LockShard`.

Dependencies and integration points: depends on `fast_lock::types::{ObjectKey, LockMode}`, `fast_lock::shard::LockShard`, and `rustfs_io_metrics` held-lock counters. `FastObjectLockManager`, `DisabledLockManager`, `NamespaceLockGuard`, and batch APIs are direct consumers. Metrics integration is intentionally separate from shard metrics: held counters are updated when guards are created and released.

Risks: `FastLockGuard::new` records an acquired metric before `manager.rs` registers the guard id; if a future path could drop the guard before registration, `release_lock_with_guard` would reject the release as inactive. Current manager code registers immediately after construction. Disabled guards never record held metrics, so metrics consumers must not compare enabled and disabled lock counts directly. `MultipleLockGuards::into_iter` uses `mem::take` plus `mem::forget` to avoid running `Drop` on the emptied container; this is deliberate but unusual and should be preserved carefully. `Drop` cannot report release errors to callers, so failed release can only be diagnosed through debug logs.

Test signals: `fast_lock/tests.rs` covers manual release, drop auto-release, double release, lock info disappearance after release, batch guard behavior indirectly, and namespace guard release. Shard tests cover guard-id cleanup and cancellation safety indirectly. Useful additional tests would assert held metrics around `FastLockGuard::new`, `release`, drop, and disabled guards.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/guard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/manager.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/manager.rs

Purpose: `manager.rs` implements `FastObjectLockManager`, the high-level sharded lock manager for local object locks. It owns the shard array, global metrics, configuration, batch-acquisition orchestration, and background cleanup task.

Important APIs/types/functions: constructors are `new` and `with_config`; `with_config` requires a power-of-two shard count, builds `Arc<LockShard>` entries, creates `GlobalMetrics`, and starts cleanup. Acquisition APIs include `acquire_lock`, read/write helpers, high-priority helpers, critical-priority helpers, and `acquire_locks_batch`. Batch internals are `group_requests_by_shard`, `acquire_locks_best_effort`, and `acquire_locks_two_phase_commit`. Monitoring/control APIs include `get_lock_info`, `get_metrics`, `total_lock_count`, `get_pool_stats`, `cleanup_expired`, `cleanup_expired_traditional`, `shutdown`, and `get_shard`. It implements the unified `LockManager` trait and custom `Clone`/`Drop`.

Control flow: single-lock acquisition hashes the key to a shard, awaits `LockShard::acquire_lock`, then creates and registers a `FastLockGuard`. Batch acquisition first sorts by `(shard_id, key)` to impose a global acquisition order that avoids deadlocks across concurrent batches. Best-effort mode walks shard groups and requests, using `try_fast_path_only` before async acquisition and accumulating successes/failures independently. All-or-nothing mode acquires in the same sorted order and drops already-created guards on first failure. Background cleanup runs a Tokio interval, calls `adaptive_cleanup` on every shard, and records cleanup runs when objects were removed.

State and persistence behavior: manager state is entirely in process memory. `shards` hold per-object lock state, `shard_mask` supports fast modulo by power-of-two mask, `config` controls timeouts/cleanup, and `cleanup_handle` tracks the background task. `Clone` shares shards and metrics but deliberately does not clone the cleanup task. `shutdown` aborts the cleanup task and forces one final adaptive cleanup.

Dependencies and integration points: integrates `LockShard`, `FastLockGuard`, request/result types, `GlobalMetrics`, and the `LockManager` trait. `lib.rs` wraps it in `GlobalLockManager`; `LocalLock` and `LocalClient` route namespace/local operations through it. `ecstore` uses `BatchLockRequest`, `NamespaceLockWrapper`, and `GlobalLockManager` for object-storage namespace locking.

Risks: `with_config` panics on non-power-of-two shard counts, so callers must validate configuration. `start_cleanup_task` uses `tokio::spawn`, requiring an active runtime during construction; creating a manager outside Tokio can panic. All-or-nothing rollback relies on dropping guards, so release failures during drop are not surfaced. Best-effort mode can return partial locks that callers must hold/release through returned guards. The comments on `acquire_write_lock` say "specific version" but it is just the write-lock helper. Background cleanup abort in `Drop` is best-effort because async final cleanup cannot run there.

Test signals: local tests verify shard grouping order. `fast_lock/tests.rs` exercises read/write acquisition, release, auto drop, timeouts, versioned keys, concurrent readers/writers, priority behavior, and lock info. `namespace/tests.rs` exercises this manager through `GlobalLockManager`, `LocalClient`, distributed quorum tests, rollback, and cleanup of late successes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/manager_trait.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/manager_trait.rs

Purpose: `manager_trait.rs` defines the unified async trait that lets enabled and disabled lock managers share one public API. The trait is used by `GlobalLockManager` to hide whether locking is active at runtime.

Important APIs/types/functions: `LockManager` requires `Send + Sync` and uses `async_trait`. It declares single-lock acquisition, read/write convenience acquisition, batch acquisition, lock inspection, aggregated metrics, total active lock count, object-pool stats, adaptive and traditional cleanup, shutdown, and `is_disabled`.

Control flow: this file has no runtime control flow beyond dynamic/static dispatch through trait methods. Implementors in this module set are `FastObjectLockManager`, `DisabledLockManager` from the same module tree, and `GlobalLockManager` in `lib.rs`, which delegates calls to either enabled or disabled managers.

State and persistence behavior: no state is stored here. The trait shape defines what state implementors must expose: lock info, metrics, pool stats, cleanup, and disabled status. All implementations in this crate are in-memory.

Dependencies and integration points: depends on `FastLockGuard`, `AggregatedMetrics`, `BatchLockRequest`, `BatchLockResult`, `ObjectKey`, `ObjectLockInfo`, `ObjectLockRequest`, and `LockResult`. It is imported by `manager.rs`, `disabled_manager.rs`, `lib.rs`, and `local_lock.rs`. Because methods accept `impl Into<Arc<str>> + Send`, the trait is not object-safe; it is designed for concrete/generic dispatch, not `dyn LockManager`.

Risks: adding object-safety requirements later would require changing generic owner parameters. Implementors must preserve semantics for disabled managers, especially returning disabled guards and empty metrics rather than failing. Divergence between inherent methods and trait methods can cause recursion mistakes, but current implementations explicitly delegate to inherent methods.

Test signals: indirect coverage comes from every `GlobalLockManager` and `LocalLock` test. Disabled-manager-specific behavior is outside this assigned source set but is critical for this trait contract.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/manager_trait.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/metrics.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/metrics.rs

Purpose: `metrics.rs` provides in-memory atomic counters and aggregation helpers for fast-lock performance and health monitoring.

Important APIs/types/functions: `ShardMetrics` owns atomic counters for fast-path success, slow-path success, timeouts, releases, cleanups, contention events, total wait time, and max wait time. It exposes record methods, total acquisition count, fast-path rate, average wait time in nanoseconds, and `snapshot`. `MetricsSnapshot` is an immutable point-in-time copy with helpers for total acquisitions, fast-path rate, average/max wait durations, and timeout rate. `GlobalMetrics` tracks shard count, start time, cleanup runs, and total objects cleaned, and `aggregate_shard_metrics` folds per-shard snapshots into `AggregatedMetrics`. `AggregatedMetrics` exposes empty metrics, empty detection, operations per second, average locks per shard, and a simple performance `is_healthy` heuristic.

Control flow: shards call record methods during acquisition/release/cleanup; the manager snapshots each shard and asks `GlobalMetrics` to aggregate. Max wait time uses a relaxed compare-exchange loop. Health is derived from fast-path rate over 80%, timeout rate under 5%, and average wait under 10 ms.

State and persistence behavior: all counters are atomic process-local state. Ordering is `Relaxed` for counters and max wait, so metrics are approximate under concurrency and should not be treated as linearizable accounting. Uptime comes from `Instant` and resets on process restart.

Dependencies and integration points: used by `LockShard` for shard-level counters, `FastObjectLockManager` for aggregation and cleanup-run accounting, `DisabledLockManager` for empty metrics, and exposed through crate exports as `AggregatedMetrics`. `guard.rs` separately updates `rustfs_io_metrics` held-lock gauges, so there are two metrics surfaces.

Risks: wait-time counters are only meaningful when slow-path code calls `record_wait_time`; current shard code records slow-path success/timeouts but does not visibly record elapsed wait time, so average wait health may underreport latency. `avg_locks_per_shard` uses cumulative acquisitions, not current active locks, so the name can mislead dashboards. `is_healthy` returns false for idle metrics because fast-path rate is 0, which can make a quiet but healthy system look unhealthy.

Test signals: unit tests cover basic shard counters and global aggregation. Higher-value signals are workload tests that assert timeout rates and fast-path rates under read-heavy, write-heavy, and contention-heavy scenarios, plus metrics consistency after cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/mod.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/mod.rs

Purpose: `mod.rs` is the module root and public facade for the fast object lock system. It documents the architecture and re-exports the main manager, guard, trait, and types.

Important APIs/types/functions: public modules are `disabled_manager`, `guard`, `manager`, `manager_trait`, `metrics`, `object_pool`, `optimized_notify`, `shard`, `state`, and `types`; test module `tests` is compiled under `cfg(test)`. Re-exports include `DisabledLockManager`, `FastLockGuard`, `FastObjectLockManager`, `LockManager`, and all `types::*`. Constants define default shard count, lock TTL, acquire timeout, max acquire timeout, and cleanup interval.

Control flow: this file has no runtime flow. Its constants influence `LockConfig::default`, `GlobalLockManager` environment clamping, and namespace convenience APIs.

State and persistence behavior: no state is stored. Constants are compile-time defaults; runtime state lives in manager/shard/state modules.

Dependencies and integration points: this facade is consumed by `lib.rs` for public exports and global manager setup; `local_lock.rs` imports lock types and the trait; external crates use `rustfs_lock::FastObjectLockManager`, `ObjectKey`, `BatchLockRequest`, and related exports through this module.

Risks: the default constants are policy-sensitive. `DEFAULT_SHARD_COUNT` must stay power-of-two because `FastObjectLockManager::with_config` asserts that. Increasing acquire/cleanup timeouts changes namespace-lock latency and cleanup memory retention. The private `DEFAULT_RUSTFS_*` constants are used by env parsing in `lib.rs`.

Test signals: module-level tests in `fast_lock/tests.rs` exercise the exported facade rather than private modules only. Build coverage is important because re-export changes affect downstream crates.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/object_pool.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/object_pool.rs

Purpose: `object_pool.rs` implements a small lock-state pool to reduce allocation churn for `ObjectLockState` entries removed by cleanup.

Important APIs/types/functions: `ObjectStatePool` wraps a lock-free `crossbeam_queue::SegQueue<Box<ObjectLockState>>` and `PoolStats` atomic counters. `acquire` pops a state, resets it, and records a hit or creates a new state and records a miss. `release` pushes states back while the pool length is below 1000 and records releases. `stats` and `hit_rate` expose pool health. An extension impl on `ObjectLockState` adds `reset_for_reuse`.

Control flow: cleanup in `LockShard::cleanup_expired_batch` attempts `Arc::try_unwrap` on idle lock states; if successful it boxes and returns them to this pool. Future acquisitions take states from the pool, resetting atomics, owners, shared owners, priority, and optimized notification before reuse.

State and persistence behavior: pool state is process-local and bounded by a soft `pool.len() < 1000` check. The queue length check is approximate under concurrency. Reset explicitly clears owner/priority fields and creates a new `OptimizedNotify`; traditional `Notify` fields are not reset directly because the entire `ObjectLockState` value came from an unwrapped object.

Dependencies and integration points: depends on `ObjectLockState`, `AtomicLockState`, `OptimizedNotify`, `LockPriority`, `crossbeam_queue`, and parking_lot locks inside the state. `LockShard` owns one pool per shard and exposes stats through manager APIs.

Risks: pooling is safe only for states no longer referenced by any lock holder or waiter. The shard only recycles after `Arc::try_unwrap`, which protects against outstanding `Arc`s, but future code must maintain that invariant. `pool.len()` on `SegQueue` can be expensive or approximate under load. Reset changes `optimized_notify` but not every field by name, so new fields added to `ObjectLockState` must be added to `reset_for_reuse`.

Test signals: unit tests check hit/miss/release accounting and owner reset. Cleanup-path tests should confirm recycled states do not retain owners, waiting counters, priority, or notifications across keys.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/object_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/optimized_notify.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/optimized_notify.rs

Purpose: `optimized_notify.rs` provides a pooled notification mechanism for lock waiters, reducing per-object allocation and limiting broad wakeups under contention.

Important APIs/types/functions: `NOTIFY_POOL` is a lazily initialized vector of 128 shared `tokio::sync::Notify` instances. `OptimizedNotify` stores reader and writer waiter counters plus an index into that pool. Public methods are `new`, `notify_readers`, `notify_writer`, `wait_for_read`, `wait_for_write`, and `has_waiters`.

Control flow: construction selects a pool index from current time nanoseconds. Wait methods increment the corresponding counter, await `notified()` on the selected pooled `Notify`, then decrement the counter. Notify methods check counters and call either `notify_waiters` for readers or `notify_one` for writers.

State and persistence behavior: waiter counters and pool index are atomic in-memory state. Pool entries are global process state shared by many object locks; a notification can wake waiters from unrelated object states that landed on the same pool index. Correctness depends on callers retrying actual lock acquisition after wakeup, which `LockShard::acquire_lock_slow_path` does.

Dependencies and integration points: used by `ObjectLockState` release paths and slow-path waits in `LockShard`. It complements but does not use the traditional `read_notify` and `write_notify` fields still present on `ObjectLockState`.

Risks: `wait_for_read` and `wait_for_write` do not use a cancellation guard internally; if the waiting future is aborted while inside the method, the decrement after `.await` will not run. `LockShard` separately increments/decrements atomic waiting counters with `WaiterCounterGuard`, but these `OptimizedNotify` counters can still leak on cancellation and make `has_waiters`/notify decisions noisy. Pooled notifications can cause spurious wakes, which is acceptable only because lock acquisition is retried. Time-based pool index selection is simple and may cluster under bursty creation.

Test signals: unit tests cover basic read and writer notification completion. Shard cancellation tests cover the separate atomic waiting counters, not the `OptimizedNotify` counters; a targeted cancellation test for `reader_waiters`/`writer_waiters` would be useful.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/optimized_notify.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/shard.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/shard.rs

Purpose: `shard.rs` implements the per-shard lock table, acquisition algorithms, release logic, adaptive timeouts, cleanup, and shard metrics for fast object locks.

Important APIs/types/functions: `LockShard` owns `objects: RwLock<HashMap<ObjectKey, Arc<ObjectLockState>>>`, an `ObjectStatePool`, `ShardMetrics`, a shard id, and an `active_guards` set. Public APIs include `new`, `acquire_lock`, `try_fast_path_only`, `release_lock`, `release_lock_with_guard`, guard registration helpers, batch acquisition, `get_lock_info`, load/active count functions, cleanup variants, metrics, lock count, and pool stats. `WaiterCounterGuard` is a private cancellation-safe ticket that increments waiting-reader/writer counters and decrements them on drop.

Control flow: acquisition starts with `try_fast_path`, which reads an existing state and attempts atomic shared/exclusive acquisition; for absent exclusive locks it takes the write lock, creates a pooled state, and acquires it immediately. Slow path computes an adaptive deadline, creates/fetches object state, retries acquisition, does short exponential backoff for early retries, then waits on optimized notifications with a `WaiterCounterGuard` and timeout. Release verifies owner/mode in `ObjectLockState`, records metrics, and schedules cleanup when the state is unlocked and has no atomic waiters. Guard-aware release first removes the guard id from `active_guards` and rejects double-release attempts.

State and persistence behavior: the shard is entirely in-memory. `objects` retains lock states after release until cleanup removes them, allowing reuse and reducing churn. `active_guards` prevents double release and informs cleanup conservatism but is keyed only by guard id, not object key. Cleanup removes idle, unlocked, no-waiter states after thresholds; batch cleanup can recycle `Arc`-unwrapped states into the pool.

Dependencies and integration points: uses `parking_lot::RwLock`, `HashMap`, `HashSet`, `tokio::time::timeout`, `ObjectLockState`, `ObjectStatePool`, `ShardMetrics`, and fast-lock request/result types. `FastObjectLockManager` owns shards and hashes keys to them. `FastLockGuard` releases through `release_lock_with_guard`.

Risks: cancellation safety is split: atomic waiter counters are protected by `WaiterCounterGuard`, but `OptimizedNotify` internal counters can still leak on cancellation. Adaptive timeout scales request timeout based on current object count and active guards, so caller-specified low timeouts may be extended up to the module max; that is intentional but affects API expectations. `current_load_factor` is active/total and cannot exceed 1, so the `current_load > 1.5` branch in cleanup is unreachable as written. `release_lock` without guard id remains available for batch cleanup and can bypass double-release protection. Cleanup thresholds use second-granularity `last_accessed`, converted to millis, making exact idle timing coarse.

Test signals: shard tests cover fast-path acquisition/release, contention timeout, batch cleanup safety, and aborted reader/writer waiters not blocking later acquisitions. Manager and namespace tests add coverage for guard release, batch order, quorum rollback, and late cleanup. Additional stress tests should exercise high-reader counts near 255, cancellation of optimized-notify waiters, cleanup under active guards, and repeated best-effort batch partial failures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/shard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/state.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/state.rs

Purpose: `state.rs` defines the per-object lock state and the packed atomic state machine used by fast shared/exclusive lock acquisition.

Important APIs/types/functions: `AtomicLockState` packs writer flag, reader count, reader-waiter count, and writer-waiter count into a `u64`, plus a `last_accessed` timestamp. It exposes fast-path availability, shared/exclusive acquisition/release, waiting-counter increment/decrement, free/waiter checks, access timestamp, and test-only waiter count accessors. `ObjectLockState` combines `AtomicLockState`, traditional `Notify` fields, `OptimizedNotify`, owner metadata locks, and priority. `ExclusiveOwnerInfo` and `SharedOwnerEntry` track owners, acquired time, counts, and timeout. Object-level methods acquire/release shared/exclusive locks, inspect lock status, and derive current mode.

Control flow: fast shared acquisition requires no writer and no waiting writers, then increments reader count up to 255. Exclusive acquisition requires state exactly zero and sets writer flag. Object-level acquisition first updates atomic state, then records owner metadata under parking_lot locks. Shared release removes/decrements owner metadata first, then releases one atomic reader and notifies a writer if no shared owners remain. Exclusive release verifies owner, clears writer flag, clears owner metadata, and notifies one writer if waiting writers exist, otherwise all readers.

State and persistence behavior: state is in-memory and cache-line aligned. Atomic bit layout supports at most 255 concurrent readers and 65535 waiting readers/writers. Owner metadata is separate from atomic state, so consistency depends on acquisition/release methods updating both. Timestamps use `SystemTime` and second precision for idle cleanup. Lock TTL is stored in owner metadata and used for monitoring expiry, but this file does not itself auto-expire held locks.

Dependencies and integration points: used by `LockShard` for all actual locking, by `ObjectStatePool` for reset/reuse, and by `ObjectLockInfo` generation. It depends on `parking_lot`, `smallvec`, `tokio::sync::Notify`, `OptimizedNotify`, `LockMode`, and `LockPriority`.

Risks: object-level acquisition modifies atomic state before owner metadata; if a panic occurred while holding metadata locks, atomic and owner state could diverge. Release attempts to roll back shared-owner metadata if atomic release fails, but the correction is necessarily best-effort. Reentrant shared locks by the same owner increment an owner count; reentrant exclusive locks are not supported. The 255-reader cap is encoded in eight bits and can become a scalability limit. Writer preference is implemented by blocking new readers when writers are waiting; leaked writer-waiting counters can starve readers.

Test signals: unit tests cover atomic shared/exclusive transitions and object-level shared/exclusive ownership. Shard cancellation tests cover waiting counters after aborted futures. Additional tests should assert owner metadata consistency on repeated shared acquisitions by the same owner, reader cap behavior, writer-preference fairness, and TTL/expiry reporting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/tests.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/tests.rs

Purpose: `fast_lock/tests.rs` is the integration-style unit test module for the fast lock facade. It validates externally visible manager, guard, key, timeout, and contention behavior using Tokio tests.

Important APIs/types/functions: the test helper `create_test_manager` builds a `FastObjectLockManager` with four shards and shorter defaults. Tests exercise `acquire_write_lock`, `acquire_read_lock`, `acquire_lock` with custom `ObjectLockRequest`, `FastLockGuard::release`, automatic `Drop`, `ObjectKey::with_version`, and `LockResult::Timeout`.

Control flow: the tests acquire guards through the manager, assert guard fields, release explicitly or by drop, and then attempt conflicting/follow-up acquisitions. Concurrency tests spawn multiple reader or writer tasks with shared `Arc<FastObjectLockManager>`. Timeout tests create contended requests with short acquire timeouts to make failures deterministic.

State and persistence behavior: test state is in-memory and per manager. Versioned keys are treated as independent `ObjectKey` values, so latest and version-specific locks can coexist. Drop tests rely on RAII release rather than background cleanup.

Dependencies and integration points: these tests cover the interaction of `manager.rs`, `shard.rs`, `state.rs`, `guard.rs`, and `types.rs`. They indirectly validate `LockConfig` defaults and `LockPriority` plumbing, but not `GlobalLockManager` env selection.

Risks surfaced by tests: same-owner exclusive acquisition is intentionally not reentrant and should time out; high-priority write locks still cannot bypass an existing exclusive lock; write locks exclude readers and other writers; read locks exclude writers but allow multiple readers; a released guard no longer reports lock info. These are contract signals for downstream namespace/object-store code.

Test gaps: the suite is good for basic behavior but does not include long-running stress, randomized cancellation, reader-count cap, cleanup/pool recycling, metrics accuracy, or disabled-lock mode. It also does not assert background cleanup shutdown behavior. Namespace tests provide broader distributed coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/types.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/types.rs

Purpose: `types.rs` defines the fast-lock public data model: object keys, lock modes, requests, results, configuration, lock info, and batch operation structures.

Important APIs/types/functions: `ObjectKey` stores bucket/object/version as `Arc<str>`, implements manual serde, ordering, display, latest/version constructors, and `shard_index`. `OptimizedObjectKey` uses `SmartString` and cached `OnceLock<u64>` hash with conversion to/from `ObjectKey`. `LockMode` is shared/exclusive. `ObjectLockRequest` has constructors for read/write and builders for version, acquire timeout, lock timeout, and priority. `LockPriority` defines Low/Normal/High/Critical. `LockResult` includes `Acquired`, `Timeout`, and `Conflict`. `LockConfig` supplies shard/default timeout/cleanup/metrics configuration. `ObjectLockInfo`, `BatchLockRequest`, and `BatchLockResult` model monitoring and batch acquisition outputs.

Control flow: these types are mostly passive. `ObjectKey::shard_index` hashes all key fields and masks by shard count. Request builders mutate and return `self`. Batch builder accumulates read/write requests using the batch owner and controls all-or-nothing behavior.

State and persistence behavior: keys and requests are cloneable in-memory values and serde-compatible where implemented. `ObjectKey` serde stores bucket, object, and optional version. `OptimizedObjectKey` hash cache is process-local and must be invalidated if fields are changed. `LockConfig::default` pulls constants from `fast_lock/mod.rs`; no values are persisted.

Dependencies and integration points: every fast-lock module depends on these types. `crate::types` defines a parallel higher-level lock model used by distributed/client APIs; `local_lock.rs` maps between the two priority and mode enums. `lib.rs` re-exports several fast-lock types publicly.

Risks: `LockResult::Acquired` is an odd error/result variant because successful acquisitions return `Ok(FastLockGuard)`; callers should rarely see it. `LockConfig::default_acquire_timeout` and `default_lock_timeout` are not applied by `ObjectLockRequest::new_*` through a manager config; request constructors use module constants directly. `BatchLockRequest::owner` is copied into new requests, but callers can also pass prebuilt requests with different owners if they construct the struct manually. `OptimizedObjectKey` is not currently the main map key in `LockShard`, so its benefits depend on future adoption.

Test signals: unit tests cover object key construction/display, request builders, and batch builder modes. Manager and namespace tests cover versioned-key behavior and batch requests indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/lib.rs -->
# sources/object-store/rustfs/crates/lock/src/lib.rs

Purpose: `lib.rs` is the crate root for `rustfs-lock`. It declares modules, re-exports the public API, defines version/policy constants, and provides the global lock manager singleton with runtime enabled/disabled selection.

Important APIs/types/functions: modules include `distributed_lock`, `local_lock`, `namespace`, `client`, `fast_lock`, `error`, and `types`. Public re-exports cover clients, guards, errors, fast-lock managers/types, namespace wrappers, and core lock/health structures. `GlobalLockManager` is an enum over `Enabled(Arc<FastObjectLockManager>)` and `Disabled(DisabledLockManager)`. `GlobalLockManager::new` reads lock enablement and acquire-timeout environment variables, clamps timeout, and constructs the appropriate manager. `get_global_lock_manager` returns the `OnceLock` singleton; `get_global_fast_lock_manager` is deprecated and panics when locks are disabled.

Control flow: when the singleton is first requested, environment variables are read. `RUSTFS_LOCK_ENABLED` is canonical and `RUSTFS_ENABLE_LOCKS` is a deprecated alias. If disabled, a `DisabledLockManager` is returned. If enabled, `RUSTFS_LOCK_ACQUIRE_TIMEOUT` is clamped to [1, max] seconds and installed into `LockConfig::default_acquire_timeout`, then a fast manager is created. The `LockManager` trait impl delegates every method to the active enum variant.

State and persistence behavior: global manager state is process-local in a `OnceLock<Arc<GlobalLockManager>>`; environment changes after initialization have no effect. No lock state persists across restarts. Version/build constants are compile-time strings.

Dependencies and integration points: `rustfs_utils` provides env parsing with aliases; `fast_lock` supplies manager/config/constants; `namespace` and `client` form the higher-level locking API. Downstream object-store code uses `NamespaceLockWrapper`, `GlobalLockManager`, and the re-exported request/response types.

Risks: creating the global manager can spawn a Tokio cleanup task through `FastObjectLockManager::with_config`, so initialization context must have a runtime. The configured `default_acquire_timeout` in `LockConfig` may not affect all request constructors, which use module constants unless the caller sets timeouts explicitly. OnceLock makes tests involving env changes order-dependent unless isolated. Deprecated `get_global_fast_lock_manager` panics in disabled mode.

Test signals: namespace tests create fresh `Arc<GlobalLockManager::new()>` instances heavily, exercising enabled mode and trait delegation. Disabled-mode env tests are not in the listed files and would be important for this facade.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/local_lock.rs -->
# sources/object-store/rustfs/crates/lock/src/local_lock.rs

Purpose: `local_lock.rs` adapts high-level `LockRequest`/`LockType` APIs to the fast local `GlobalLockManager`, returning `FastLockGuard` instances for namespace-local locking.

Important APIs/types/functions: `LocalLock` stores a `namespace: String` and `Arc<GlobalLockManager>`. Public methods expose construction, namespace access, resource-key formatting, and convenience `lock_guard`/`rlock_guard` methods. The central internal method is `acquire_guard`, which converts `LockRequest` into `ObjectLockRequest`.

Control flow: `acquire_guard` clones the request resource, maps `LockType::{Exclusive,Shared}` to `LockMode::{Exclusive,Shared}`, converts owner to `Arc<str>`, maps `types::LockPriority` to `fast_lock::types::LockPriority`, preserves acquire timeout and TTL as lock timeout, then awaits `GlobalLockManager::acquire_lock`. Any fast-lock error is collapsed to `Ok(None)`. Convenience methods construct `LockRequest` values with requested timeout and TTL before calling `acquire_guard`.

State and persistence behavior: `LocalLock` itself stores only namespace and manager reference. It does not maintain a local table; all lock state lives in the global manager/shards. Resource-key formatting is just a string helper and is not used to namespace the `ObjectKey` passed to the manager.

Dependencies and integration points: used by `NamespaceLock::Local` in `namespace/mod.rs`. It bridges crate-level types from `types.rs` and fast-lock types from `fast_lock/types.rs`. `LocalClient` in the client module performs a related adaptation for distributed-lock clients.

Risks: errors are swallowed into `Ok(None)`, so callers lose the distinction between timeout, conflict, disabled behavior, and internal fast-lock errors. The namespace string is not incorporated into the actual `ObjectKey`; two `LocalLock` instances sharing the same manager but different namespaces can conflict if they use the same bucket/object/version. If namespace isolation is expected, callers must encode namespace into the object key or this module must change. Priority mapping must stay in sync between the two enum definitions.

Test signals: namespace tests cover local-manager construction, local write/read guard acquisition, guard release, health and stats defaults, and wrapper behavior. Tests do not currently cover namespace collision between two local namespaces on the same manager.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/local_lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/mod.rs -->
# sources/object-store/rustfs/crates/lock/src/namespace/mod.rs

Purpose: `namespace/mod.rs` provides the public namespace-lock facade, unifying distributed quorum locks and fast local locks behind `NamespaceLock`, `NamespaceLockGuard`, and `NamespaceLockWrapper`.

Important APIs/types/functions: `NamespaceLockGuard` wraps either `DistributedLockGuard` or `FastLockGuard` and exposes `lock_id`, `key`, `release`, and `is_released`. `NamespaceLockWrapper` stores a lock, resource, and owner for repeated convenience acquisition. `NamespaceLock` variants are `Distributed(DistributedLock)` and `Local(LocalLock)`. Constructors include `new`, `with_client`, `with_local_manager`, `with_clients`, and `with_clients_and_quorum`. Acquisition APIs include `acquire_guard`, `lock_guard`, `rlock_guard`, `get_write_lock`, `get_write_lock_quiet`, and `get_read_lock`. Health/stat APIs are `get_health` and `get_stats`.

Control flow: constructors choose distributed mode for client-based locks and local mode for a `GlobalLockManager`. Multi-client distributed locks default write quorum to majority, while explicit quorum is passed through. Acquisition methods dispatch by enum variant and wrap returned guards. The convenience `get_*` methods convert `Ok(None)` into `LockError::timeout`. `get_write_lock_quiet` suppresses expected distributed contention logs. Health checks run client `is_online` calls in parallel for distributed locks and mark local locks healthy with one connected node. Stats aggregate successful/failed acquires from distributed clients; local stats remain default.

State and persistence behavior: namespace lock objects store either a distributed lock with clients/quorum or a local lock with manager. Guards own release responsibility. No persistent state exists here; distributed state lives in clients/backends and local state in fast-lock shards.

Dependencies and integration points: integrates `DistributedLock`, `DistributedLockGuard`, `LockClient`, `LocalLock`, `FastLockGuard`, `LockRequest`, `LockId`, and crate error/types. Downstream storage layers use `NamespaceLockWrapper` for object and bucket operation serialization.

Risks: local namespace isolation has the same caveat as `LocalLock`: the namespace is not necessarily part of the actual lock key. `get_*` methods map `None` to timeout, which can blur disabled or internal failures. `NamespaceLockGuard::lock_id` is unavailable for fast guards, and `key` is unavailable for distributed guards, so callers must handle variant-specific metadata. Local `get_stats` returns zeros even though fast-lock metrics exist elsewhere.

Test signals: `namespace/tests.rs` broadly covers constructors, local guards, wrapper, health/stats, distributed quorum, rollback, retries, offline clients, read/write quorum differences, slow-client early return, and no-runtime drop.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/tests.rs -->
# sources/object-store/rustfs/crates/lock/src/namespace/tests.rs

Purpose: `namespace/tests.rs` is the primary behavioral test suite for the namespace facade and distributed quorum semantics. It validates local wrappers and simulated multi-node distributed locking with custom clients.

Important APIs/types/functions: helper client types include `FailingClient`, `FailureResponseClient`, `DelayedClient`, `FlakyAcquireClient`, and `FlakyReleaseClient`. Helpers `create_test_object_key` and `wait_until_all_managers_can_write` build keys and verify cleanup across simulated nodes. Tests exercise `NamespaceLock`, `NamespaceLockGuard`, `NamespaceLockWrapper`, `LocalClient`, `GlobalLockManager`, `LockClient` batch defaults, and distributed read/write operations.

Control flow: local tests instantiate managers and assert local guard variants, release behavior, wrapper owner/resource usage, health, and stats. Distributed tests build multiple `LocalClient`s backed by independent managers, acquire quorum locks, assert contention failures, release guards, and probe every manager for cleanup. Failure tests inject offline clients, RPC-like failure responses, delayed clients, transient acquisition failures, and release failures to verify retry/rollback/early-return behavior.

State and persistence behavior: all simulated nodes are in-memory `GlobalLockManager` instances. Distributed guards are expected to release all successful node locks, including rollback after quorum failure and cleanup of late successes from slow clients. Tests deliberately drop a distributed guard after its runtime is gone to ensure drop does not panic and cleanup can later complete.

Dependencies and integration points: covers the interaction of namespace facade, distributed lock implementation, client trait, local client, global manager, and fast lock internals. It is a strong integration signal for object-store code that maps quorum failures into storage errors.

Risks captured: two-node read locks can succeed with one healthy node while writes fail with one offline node; remote RPC failures should be hard quorum failures rather than contention timeouts; ordinary contention should exhaust timeout and not masquerade as quorum loss; failed quorum must roll back successful nodes; late successes from slow clients must be cleaned up after early success or early failure; release false values should be retried.

Test gaps: these tests are comprehensive for quorum behavior but use deterministic simulated clients, not real network RPC. They do not test environment-disabled global managers, namespace collision in local mode, metrics exposure, or high-volume concurrent distributed operations beyond selected scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/types.rs -->
# sources/object-store/rustfs/crates/lock/src/types.rs

Purpose: `types.rs` defines the crate-level lock protocol model used by distributed locks, clients, namespace APIs, health reporting, and wait/deadlock metadata. It is distinct from `fast_lock/types.rs` and is the serialization-facing model for many client paths.

Important APIs/types/functions: lock enums include `LockType`, `LockStatus`, and `LockPriority`. `LockInfo` stores id, resource, type, status, owner, acquired/expires/refresh times, metadata, priority, and optional wait start. `LockId` combines `ObjectKey` with a UUID and has `new`, `new_unique`, `as_str`, default, display, and serde. `LockMetadata` supports builder methods for client info, operation id, priority, and tags. `LockRequest` stores lock id/resource/type/owner/acquire timeout/TTL/metadata/priority/deadlock flag/log suppression and has builder methods. `LockResponse` models success/failure/waiting responses. `LockStats`, `NodeInfo`, `ClusterInfo`, `HealthInfo`, timestamp helpers, `DeadlockDetectionResult`, `WaitGraphNode`, and `WaitQueueItem` round out monitoring and deadlock/wait-queue structures.

Control flow: most methods are builders or inspectors. `LockInfo` checks expiry/remaining validity against `SystemTime::now`. `LockRequest::new` generates a unique lock id and default 10-second acquire timeout/30-second TTL. `LockResponse` constructors encode success/failure/waiting variants. Timestamp helpers convert between UNIX seconds and `SystemTime`.

State and persistence behavior: all structs are serde-compatible and suitable for RPC/admin payloads. UUIDs are generated per request/id; timestamps use `SystemTime`. No storage is performed here, but these types define what can be serialized over local/remote lock clients.

Dependencies and integration points: depends on `serde`, `uuid`, and `ObjectKey` from the fast-lock public exports. Used by `client`, `distributed_lock`, `namespace`, `local_lock`, remote locker code, and storage error mapping. `local_lock.rs` maps this model to fast-lock requests.

Risks: there are duplicate priority and mode enums between this file and `fast_lock/types.rs`, requiring explicit mapping. `LockMetadata.priority` says lower number means higher priority, while `LockPriority` enum uses larger discriminants for higher priority; consumers must not conflate them. `LockInfo::has_expired` uses wall-clock time and can be affected by clock changes. `deadlock_detection` and wait-graph types are data-model hooks; actual detection behavior depends on other modules.

Test signals: direct tests are not in this file, but namespace and distributed-lock tests heavily exercise `LockRequest`, `LockResponse`, `LockId`, and `LockStats`. Serialization compatibility should be covered by RPC tests that round-trip these structures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/Cargo.toml -->
# sources/object-store/rustfs/crates/madmin/Cargo.toml

Purpose: `Cargo.toml` defines the `rustfs-madmin` crate, which provides management/admin data structures and APIs for RustFS.

Important APIs/types/functions: package metadata names the crate `rustfs-madmin`, inherits edition/license/repository/rust-version/version/homepage from the workspace, and describes management/admin tooling with docs.rs documentation. It disables doctests for the library. Runtime dependencies are workspace versions of `chrono`, `humantime`, `hyper`, `serde`, `serde_json`, and `time`; dev dependency is `rmp-serde`.

Control flow: no runtime control flow exists. Cargo uses this manifest to compile the crate and resolve workspace dependency versions/lints.

State and persistence behavior: no application state is stored here. Dependency choices influence serialization formats and API model support in the Rust source files.

Dependencies and integration points: `serde`, `serde_json`, and `time` are directly used by the listed `group.rs`, `heal_commands.rs`, and `health.rs` files. `rustfs-madmin` types are consumed by object-store/ecstore healing and peer APIs, especially `HealResultItem`, `HealDriveInfo`, group descriptions, and health payloads.

Risks: disabling doctests means examples in documentation will not be validated. Workspace-inherited versions centralize compatibility but can introduce changes crate-wide. `hyper` is listed even though these specific model files are mostly serde data structures; unused dependency risk depends on other madmin modules.

Test signals: crate tests in individual source modules validate serde behavior for group and health models. Build/test coverage should include the whole workspace because madmin structs are serialized across admin and peer APIs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/group.rs -->
# sources/object-store/rustfs/crates/madmin/src/group.rs

Purpose: `group.rs` defines admin payload structures for group membership/status operations and group descriptions.

Important APIs/types/functions: `GroupStatus` is a lower-case serde enum with variants `Enabled` and `Disabled`; it has custom deserialization that treats the empty string as enabled. `GroupAddRemove` contains group name, member list, `groupStatus`, and `isRemove` fields. `GroupDesc` contains group name/status/members/policy and optional `updatedAt` timestamp serialized/deserialized as RFC3339 through `time::serde::rfc3339::option`.

Control flow: deserialization of `GroupStatus` reads a string and matches `""` or `"enabled"` to enabled, `"disabled"` to disabled, and rejects all other values. The rest is serde field mapping.

State and persistence behavior: these are plain DTOs with no persistence logic. `updated_at` is optional and skipped on serialization when absent. Using `OffsetDateTime` preserves timezone-offset-aware timestamps in admin JSON.

Dependencies and integration points: depends on `serde` and `time`. These structures likely back madmin group add/remove/describe APIs and must match MinIO-compatible field names (`groupStatus`, `isRemove`, `updatedAt`).

Risks: `GroupDesc.status` is a raw `String`, not `GroupStatus`, so invalid statuses can be represented and serialized. `GroupStatus` custom deserializer is intentionally lenient for empty strings, but only lowercase accepted strings are supported. Timestamp serialization removes nanoseconds in the test setup but the serde helper can encode full RFC3339 values.

Test signals: tests verify `updatedAt` RFC3339 round-trip and empty-string status deserializing to enabled. Additional tests should cover invalid status rejection and field renames for `GroupAddRemove`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/heal_commands.rs -->
# sources/object-store/rustfs/crates/madmin/src/heal_commands.rs

Purpose: `heal_commands.rs` defines serializable admin/result models for healing operations.

Important APIs/types/functions: `HealItemType` is a string alias. `HealDriveInfo` contains drive UUID, endpoint, and state. `Infos` wraps `drives` as a vector of drive info. `HealResultItem` contains result id (`resultId`), item type (`type`), bucket/object/version identifiers, detail, erasure-coding block counts, disk/set counts, before/after drive info, and object size.

Control flow: no runtime logic exists; serde derive handles field mapping and default construction.

State and persistence behavior: these are DTOs. `Default` yields empty strings, zero numeric counts, and empty drive lists. They do not validate consistency between data/parity blocks, disk count, or before/after states.

Dependencies and integration points: depends on `serde`. `rg` shows `HealResultItem` and `HealDriveInfo` are consumed throughout `ecstore` heal paths, peer S3 clients, set/disk healing, config storage tests, and store APIs. Field names appear designed for admin API compatibility.

Risks: numeric fields use `usize`, which can vary by platform width and may not be ideal for stable wire/API contracts. The `type` JSON field is represented by `heal_item_type` to avoid Rust keyword conflict. Absence of validation means producers must populate coherent counts and drive states. `version_id` is a plain string, so missing version and empty version are indistinguishable.

Test signals: there are no direct tests in this file. Integration tests in healing modules should verify JSON/msgpack compatibility, populated before/after drive states, and object-size/count correctness.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/heal_commands.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/health.rs -->
# sources/object-store/rustfs/crates/madmin/src/health.rs

Purpose: `health.rs` defines madmin health/system-information DTOs and placeholder getter functions for CPU, partition, OS, process, services, config, errors, and memory information.

Important APIs/types/functions: data structs include `NodeCommon`, `Cpu`, `CpuFreqStats`, `Cpus`, `Partition`, `Partitions`, `OsInfo`, `ProcInfo`, `SysService`, `SysServices`, `SysConfig`, `SysErrors`, and `MemInfo`. Getter functions are `get_cpus`, `get_partitions`, `get_os_info`, `get_proc_info`, `get_sys_services`, `get_sys_config`, `get_sys_errors`, and `get_mem_info`; they currently return defaults. `MemInfo` and `NodeCommon.error` use `skip_serializing_if = Option::is_none`, and swap fields use explicit snake-case renames.

Control flow: all getter functions are stubs returning `Default`. Tests instantiate values, serialize/deserialize selected structs, and assert default behavior. There is no system probing yet.

State and persistence behavior: these are plain in-memory DTOs. Many fields are private, so external callers can serialize/deserialize returned values but cannot construct all structs field-by-field outside the module except for public fields like `NodeCommon` and `Cpu`. Optional memory fields are omitted from JSON when absent.

Dependencies and integration points: depends on `serde` and `HashMap`. Peer REST client code references `get_mem_info`-style health payloads, and this crate provides admin-facing health models. Future implementations will likely integrate OS/process/filesystem probing crates or platform APIs.

Risks: placeholder getters returning empty/default values can be mistaken for real health data unless callers know these functions are TODOs. Many struct fields are private, limiting external construction and possibly making public API evolution harder. `Partition.error` is public but other partition details are private. Numeric units are not documented in the structs, which can lead to inconsistent producers. The memory efficiency test only checks rough struct size, not allocation behavior.

Test signals: tests cover defaults, value construction inside the module, JSON skip behavior, getter stubs returning defaults, debug formatting, and approximate memory footprint. Missing tests include real system data collection, cross-platform behavior, and API compatibility snapshots.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/health.rs -->
