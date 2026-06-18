# subset-b-008859 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/endpoint.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/endpoint.rs

`endpoint.rs` is the central resolved-ts worker. It owns the observed leader-region set, starts initial lock scans, receives raft-applied change logs, forwards advance requests, handles dynamic config, and exports timer-driven diagnosis metrics. `Endpoint<T, E, S>` depends on raftstore `CdcHandle`, `RegionReadProgressRegistry`, `StoreRegionMeta`, PD timestamp advancement, `ScannerPool`, and a shared `MemoryQuota`.

Important internal state is split between `ObserveRegion` and `ResolverStatus`. A newly registered region starts in `Pending` with an observe handle, cancellation channel, tracked apply index, and buffered `PendingLock` entries. During this phase, `track_change_log` records prewrite and commit events without publishing a ready resolver. When `ScannerPool` returns all existing lock-CF entries, `track_scan_locks(ScanEntries::None, apply_index)` updates the resolver to the snapshot apply index, drains pending lock/unlock operations into the resolver, frees pending memory quota, and marks the status `Ready`.

Control flow enters through `Task`, implemented by `Runnable::run`. Region lifecycle tasks register, deregister, re-register, update epochs, or destroy observed regions. `ChangeLog` frees channel memory accounting, checks observe-id freshness, converts `CmdBatch` into `ChangeLog`, and updates resolver state. Split and merge admin commands stop tracking ready resolvers until region metadata is re-registered. `ResolvedTsAdvanced` applies a PD or lock-derived timestamp to ready resolvers only. Config changes update `advance_ts_interval`, memory quota capacity, and scan concurrency, then notify the advance worker.

State is in memory only, but it publishes safe-ts and tracked index into raftstore `RegionReadProgress`. Persistence/recovery is achieved by re-registration and fresh lock scanning instead of storing resolver state. Memory quota is explicitly charged for pending locks and channel batches; quota overflow triggers either region re-registration or all-region re-registration with randomized backoff.

Risks center on ordering and resource control: observe-id ABA protection must discard stale scan/change-log results, tracked indexes must remain monotonic, and pending locks must be drained exactly once to avoid quota leaks. Test signals come from integration and failpoint tests for split/merge behavior, dynamic interval changes, scan/change-log quota overflow, pending channel draining, store partition handling, and check-leader timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/errors.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/errors.rs

This small module defines the resolved-ts component error boundary. `Error` has two variants: `MemoryQuotaExceeded`, wrapping `tikv_util::memory::MemoryQuotaExceeded`, and `Other`, wrapping a boxed `dyn std::error::Error + Sync + Send`. The module also defines `Result<T>` as the component-local result alias.

The purpose is to keep quota failures distinguishable from generic operational failures. `endpoint.rs` matches `Error::MemoryQuotaExceeded` to re-register all regions and shed accumulated pending memory, while `Error::Other` usually re-registers only the affected region. `scanner.rs` converts raftstore snapshot and MVCC scan failures into `Error::Other`, while pending and resolver lock tracking use the quota variant.

There is no persistent state here. The integration point is Rust's `thiserror::Error` derive and `From` conversions, which keep call sites concise with `?` and `box_err!`. The main risk is overuse of `Other`, which can erase structured raftstore causes such as epoch mismatch except where the caller parses them first. Test coverage is indirect through scanner and endpoint failpoint tests that assert distinct quota and re-registration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/lib.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/lib.rs

`lib.rs` is the crate facade for TiKV's resolved-ts component. Its module-level documentation states the core invariant: resolved-ts is a lower bound for future commit timestamps and an upper bound for commits already visible for transaction-level consistent views. It lists the required premises: track all region locks, use the minimum start-ts while locks exist, use a fresh timestamp when no locks exist, and advance only from the region leader after it has applied in its term.

The public API is mostly re-exported modules: `resolver`, `cmd`, `observer`, `advance`, `endpoint`, `errors`, `scanner`, and `metrics`. External users can construct observers and endpoints, schedule `Task`s, inspect or use `Resolver`, and consume metrics symbols through this facade. The crate enables `#![feature(box_patterns)]`, so it depends on nightly features in the TiKV build.

There is no runtime state in this file, but it defines the integration surface and makes internal modules part of the crate API. This has compatibility risk: broad `pub use` exports can expose internal types such as resolver internals or metrics names to other TiKV components. Test signals are distributed across module unit tests and integration tests that import `resolved_ts::Task`, metrics, and helpers directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/metrics.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/metrics.rs

This file registers Prometheus metrics for the resolved-ts subsystem. The metrics cover pending command bytes, check-leader request sizes and counts, scan duration and task counts, minimum resolved-ts and safe-ts by leader/follower role, zero resolved-ts counts, memory quota usage, resolver readiness counts, follower lag histograms, and detailed timestamps for slow-region diagnosis.

The metrics are exported as `lazy_static!` globals and are used by `endpoint.rs`, `scanner.rs`, `observer.rs`, `advance.rs`, and `resolver.rs`. `Endpoint::on_timeout` periodically collects `Stats` and writes gauges such as `RTS_MIN_RESOLVED_TS`, `RTS_LOCK_HEAP_BYTES_GAUGE`, and role-specific min-ts gauges. `Observer` increments and decrements pending channel bytes around scheduled command batches. `ScannerPool` records scan task lifecycle and initial backoff duration. `Resolver::resolve` increments fail-advance counters labeled by `TsSource`.

No state is persisted beyond Prometheus process memory. The integration point is the global default registry via `prometheus::register_*`, so metric name stability matters for dashboards and alerts. Risks include typo compatibility, for example `RTS_MIN_LEADER_DUATION_TO_LAST_UPDATE_SAFE_TS`, and high-cardinality concerns are avoided by using fixed labels rather than region labels. Tests indirectly validate metrics through failpoint assertions of `RTS_CHANNEL_PENDING_CMD_BYTES` draining after quota-triggered re-registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/observer.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/observer.rs

`observer.rs` bridges raftstore coprocessor events into resolved-ts worker tasks. `Observer` holds a `Scheduler<Task>` and shared `MemoryQuota`. `register_to` installs it as a command observer with low priority 1000, a role observer, and a region-change observer. Low command priority lets other observers process batches before resolved-ts takes ownership with `mem::take`.

For applied command batches, `on_flush_applied_cmd_batch` exits when no observer level is active, filters batches through `lock_only_filter`, charges their serialized size into `RTS_CHANNEL_PENDING_CMD_BYTES` and `memory_quota.alloc_force`, then schedules `Task::ChangeLog`. If scheduling fails, it frees the charged quota. `on_applied_current_term` registers a region after a peer becomes leader and applies in its current term. `on_role_change` deregisters on non-leader roles. `on_region_changed` forwards leader-only update and destroy events to the endpoint.

The file has no persistent state; correctness depends on raftstore event order, observe handles, and the endpoint's stale-observe-id checks. The risk is memory pressure because command batches are forcibly charged before asynchronous handling, but endpoint active quota checks and all-region re-registration are designed to drain overload. Unit tests cover command filtering under cdc/resolved-ts/PITR observe-handle combinations, including lock-only filtering when only resolved-ts observes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/observer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/resolver.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/resolver.rs

`resolver.rs` implements the timestamp safety model for one region. `Resolver` tracks in-memory lock state and computes a resolved-ts that is never greater than a possible future commit timestamp. Normal locks are stored as `locks_by_key: HashMap<Arc<[u8]>, TimeStamp>` and summarized by `lock_ts_heap: BTreeMap<TimeStamp, TxnLocks>`. Large/pipelined transactions use `large_txns` plus `large_txn_key_representative` and consult `TxnStatusCache` for `min_commit_ts`.

Key APIs are `track_lock`, `untrack_lock`, `resolve`, `oldest_transaction`, `stop_tracking`, `update_tracked_index`, diagnosis counters, and optional publication to `RegionReadProgress`. `TsSource` labels why a resolve attempt used a lock, concurrency-manager memory lock, PD TSO, backup stream, or CDC. `LastAttempt` is logged for slow-region diagnosis. Memory quota is charged for normal lock keys, freed on untrack/drop, and estimated through `approximate_heap_bytes`.

The main control flow is `resolve(min_ts, now, source)`: shrink the lock map periodically, ignore advancement when stopped, find the oldest normal transaction or large transaction `min_commit_ts.prev()`, choose `min(new_oldest, min_ts)`, record success/failure metrics, monotonically update `resolved_ts`, publish `(tracked_index, safe_ts)` to read progress, and update `min_ts`. Large transactions intentionally use `min_commit_ts - 1` so a later commit at exactly `min_commit_ts` remains safe.

State is volatile and reconstructed by endpoint scans. Risks include idempotency of duplicate prewrite/unlock observations, approximate memory accounting for large transactions, stale or missing `TxnStatusCache` entries, and monotonic tracked-index assertions. Unit tests cover basic resolve cases, quota free-on-drop, hash map shrink behavior, idempotent tracking/untracking, large transaction min-commit-ts handling, and the strict `commit_ts > resolved_ts` invariant.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/resolver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/scanner.rs -->
# sources/storage-engines/tikv/components/resolved_ts/src/scanner.rs

`scanner.rs` performs the asynchronous initial lock scan needed before a registered region's resolver can become ready. `ScanTask` carries the observe handle, region metadata, checkpoint timestamp, optional backoff, cancellation receiver, and endpoint scheduler. `ScannerPool<T, E>` owns a Tokio multi-thread runtime and a raftstore `CdcHandle`.

`spawn_task` optionally sleeps for re-registration backoff, acquires a scan concurrency semaphore, obtains a region snapshot through `capture_change(ChangeObserver::from_rts(...))`, then scans lock CF with `MvccReader::scan_locks_from_storage`. It emits batches as `Task::ScanLocks { entries: ScanEntries::Lock(..) }` and finally sends `ScanEntries::None` with the snapshot apply index. The endpoint uses that final marker to merge pending change-log events and publish a ready resolver.

Snapshot acquisition retries transient raft errors with exponential backoff. Epoch mismatch and stale observe-id errors are not retried because the same metadata/observe handle cannot succeed. Cancellation is checked before and during waits so deregistration can stop obsolete scans. Only `Put` and `Delete` locks are scanned; 1PC and ingest SST are handled through tracked-index updates in change logs.

State is not persisted; it is a bounded asynchronous reconstruction pass. Integration points are raftstore CDC observation, MVCC snapshots, `GLOBAL_TIMER_HANDLE`, Tokio semaphores, resolved-ts metrics, and failpoints around snapshot acquisition. Risks include stale scans racing with re-registration, scan backlogs under low concurrency, snapshot retry latency, and memory quota overflow when scanned locks are inserted. Integration and failpoint tests cover scan quota failures and split-triggered rescans.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/src/scanner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/tests/failpoints/mod.rs -->
# sources/storage-engines/tikv/components/resolved_ts/tests/failpoints/mod.rs

This integration-test module uses failpoints to exercise resolved-ts behavior under timing stalls and quota pressure. It imports the shared `TestSuite` and manipulates PD TSO, raft leadership, TiKV KV operations, and endpoint diagnosis tasks.

`test_check_leader_timeout` pauses check-leader calls on follower stores, commits a locked key, and verifies resolved-ts does not advance until enough follower leadership confirmation recovers. `test_report_min_resolved_ts` and `test_report_min_resolved_ts_disable` force short reporting intervals and verify PD min-resolved-ts reporting can advance or remain disabled. `test_pending_locks_memory_quota_exceeded` pauses after scanner snapshot acquisition so incoming prewrite locks accumulate in endpoint pending state, then shrinks memory quota and asserts the quota failpoint fires. `test_change_log_task_channel_memory_quota_exceeded` pauses after change-log handling, accumulates pending command bytes, lowers quota, resumes, and asserts re-registration drains locks and channel bytes.

The tests validate volatile state transitions rather than persistence. They are strong signals for concurrency boundaries: scan pending state, channel memory accounting, active quota checks, and backoff-based re-registration. Risks covered include deadlocked pending scans, quota leaks, stale locks after all-region re-registration, and incorrect PD min-resolved-ts reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/tests/failpoints/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/tests/integrations/mod.rs -->
# sources/storage-engines/tikv/components/resolved_ts/tests/integrations/mod.rs

This module contains end-to-end resolved-ts tests over `test_raftstore` clusters. It validates normal operation without synthetic failpoint pauses. The tests use `TestSuite` helpers to start clusters, issue KV prewrite/commit/rollback requests, split and merge regions, ingest SST files, adjust online config, query region read progress, and isolate stores.

`test_resolved_ts_basic` checks that a lock prevents advancement, split creates one region that advances and one that inherits the blocked timestamp, merge preserves the blocked timestamp, commit releases advancement, ingest SST advances tracked index, and 1PC updates tracked index without lock tracking. `test_dynamic_change_advance_ts_interval` confirms online config can slow advancement to a long interval and later wake the advance worker when restored. `test_change_log_memory_quota_exceeded` and `test_scan_log_memory_quota_exceeded` reduce quota to one byte and verify diagnosis reports zero resolved-ts for overloaded affected regions. `test_store_partitioned` isolates one store and asserts resolved-ts still advances quickly with available leadership.

These tests are the main behavioral safety net for endpoint, observer, scanner, and resolver integration. Risks covered include region epoch changes, merge/split lock ranges, online config propagation, scan/change-log quota paths, and partial cluster partitions. They do not prove metric accuracy except indirectly through state and diagnosis callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/tests/integrations/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/tests/mod.rs -->
# sources/storage-engines/tikv/components/resolved_ts/tests/mod.rs

`tests/mod.rs` defines the shared `TestSuite` used by resolved-ts integration and failpoint tests. It wraps a `Cluster<ServerCluster>`, lazily built `TikvClient` and `ImportSstClient` maps, and a grpc `Environment`. `init` runs `test_util::setup_for_ci` once.

`TestSuite::new` constructs a server cluster, configures lease-read timing, enables resolved-ts, and sets a default 10 ms advance interval. Helper methods start and stop the cluster, schedule endpoint `Task`s through the simulated store's resolved-ts scheduler, apply online config changes for advance interval and memory quota, and build correct request contexts from the current region epoch and leader peer.

KV helpers issue prewrite, commit, and rollback RPCs with assertions that region and key errors are absent. Client helpers create TiKV and import clients for the current region leader. Diagnosis helpers read resolved-ts and tracked indexes from leader store metadata, with retry loops for asynchronous advancement. `must_get_rts` and `must_get_rts_ge` poll up to 50 times with sleeps.

There is no production state here, but it is an integration point into test raftstore internals and resolved-ts task scheduling. Risks are test flakiness due to timing, leader movement, and fixed retry windows. Its presence makes tests concise and consistently validates public behavior through real RPCs rather than only unit-level resolver calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resolved_ts/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/Cargo.toml -->
# sources/storage-engines/tikv/components/resource_control/Cargo.toml

This manifest defines the `resource_control` crate, an unpublished Apache-2.0 TiKV component using Rust edition 2024. It exposes one optional feature, `failpoints`, mapped to `fail/failpoints`, which enables failpoint-driven tests in the future limiter path.

Dependencies show the crate's integration surface: `pd_client` and `kvproto` for resource-group metadata and RPCs, `tikv_util` for resource-control primitives and workers, `file_system` for IO byte accounting, `futures` and `tokio-timer` for async throttling, `crossbeam` and priority queues for channels, `online_config` and `serde` for dynamic configuration, `prometheus` for metrics, and `yatp` for pool integration. Dev dependencies include `test_pd`, `rand`, and test-exported `file_system`.

There is no runtime control flow in the manifest, but it is a risk signal: `yatp` is pulled from a Git branch rather than a versioned crate, and `dashmap` is pinned directly while most dependencies use workspace versions. Build/test behavior depends on nightly features used by the crate source and on feature-gated failpoints for some tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/channel.rs -->
# sources/storage-engines/tikv/components/resource_control/src/channel.rs

`channel.rs` wraps normal crossbeam channels and TiKV priority queues behind a common `Sender`/`Receiver` API. When no `ResourceController` is supplied, `bounded` and `unbounded` return vanilla crossbeam channels. When resource control is enabled, both functions currently use an unbounded priority queue; the bounded path has a TODO noting it is not actually bounded.

`ResourceMetered` lets messages report resource consumption and return the dominant resource group name. `Sender::consume_msg_resource` calls that hook and records the last group in a `RefCell<String>`. Subsequent `send` and `try_send` ask `ResourceController::get_priority(last_msg_group, CommandPri::Normal)` and submit the message with that priority, optionally respecting a `low_bound` to preserve ordering for messages from one peer. Receivers expose only `recv` and `try_recv`.

State is per-sender and volatile: cloned priority senders get their own empty `last_msg_group`, while the queue and controller are shared. Dependencies include `kvproto::CommandPri`, `tikv_util::mpsc::priority_queue`, and the crate's `ResourceController`. Risks include priority decisions based on the previous consumed message rather than the current message unless callers invoke `consume_msg_resource` in the right order, unbounded memory growth in resource-controlled `bounded`, and `RefCell` runtime borrow constraints. A benchmark test verifies resource consumption and message delivery through the priority path.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/config.rs -->
# sources/storage-engines/tikv/components/resource_control/src/config.rs

`config.rs` defines dynamic resource-control configuration. `Config` is serde-deserializable, kebab-case, and derives `OnlineConfig`. It controls whether resource control is enabled, priority strategy, CPU thresholds for background and foreground throttling, compaction pressure thresholds, background write IO ceiling/floor, fair scheduling, read/write admission control, historical RU baseline window, burst percentage, and maximum delayed admission count. `enabled` and `historical_usage_window_mins` are marked non-online.

Defaults enable resource control with `Moderate` priority control, 60 percent background CPU throttle threshold, 70 percent foreground threshold, 70 percent compaction pressure threshold, 100 GB background write IO ceiling, 10 MB floor, fair scheduling and admission disabled, a 15 minute history window, 20 percent burst allowance, and 10,000 delayed admission slots.

`PriorityCtlStrategy` maps `Aggressive`, `Moderate`, and `Conservative` to resource utilization percentages 0.5, 0.7, and 0.9. It supports display and conversion to/from `online_config::ConfigValue::String`; invalid string values return errors while non-string values panic. `ResourceContrlCfgMgr` wraps `Arc<VersionTrack<Config>>` and applies online changes through `ConfigManager::dispatch`.

State is maintained in `VersionTrack`, not persisted here. Risks include the typo in `ResourceContrlCfgMgr`, panic on wrong `ConfigValue` type, and skipped online fields requiring restart. Tests are not local in this file, so validation is mostly by serde/online-config integration elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/future.rs -->
# sources/storage-engines/tikv/components/resource_control/src/future.rs

`future.rs` provides async wrappers that measure and optionally throttle resource use. `ControlledFuture<F>` wraps any future and, after each poll, charges elapsed CPU time to a `ResourceController` for a named group. `LimitedFuture<F>` wraps a future with a `ResourceLimiter`, measuring CPU duration and IO bytes per poll and converting limiter debt into timer delays unless `measure_only` is true.

`LimitedFuture::poll` first pays existing token-bucket debt with `pre_delay` on the first poll for throttling mode. It then polls delay futures if active, samples IO bytes only when the IO limiter is finite, times the wrapped future poll, optionally replaces write IO with known request `write_bytes` on completion, and calls `resource_limiter.consume(dur, io_bytes, res.is_pending(), skip_compaction_pressure)`. Foreground non-background limiters can feed `ResourceGroupManager::record_ru_consumption` for baseline/admission logic. If the wrapped future is pending and limiter debt exists, a capped `post_delay` is scheduled, with `MAX_WAIT_DURATION` limiting any single wait to 10 seconds.

`measure_only` mode is important for read/write pools: it accumulates debt and RU history but never sleeps in the pool, leaving admission control to throttle before submission. Background jobs use in-pool sleeping. `OptionalFuture` is a local helper tracking whether a timer future still needs polling. `with_resource_limiter` conditionally wraps a future or awaits it directly.

Risks include poll-level accounting overhead, IO tracker noise for shared threads, double-counting if `write_bytes` were charged on pending polls, and delayed tasks occupying worker threads in throttling mode. Failpoint tests validate IO-byte delay behavior, wait duration bounds, and fallback when thread IO stats fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/future.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/lib.rs -->
# sources/storage-engines/tikv/components/resource_control/src/lib.rs

`lib.rs` is the public facade and periodic-task bootstrap for the `resource_control` crate. It re-exports resource-group types such as `AdmissionDecision`, `DelaySlotGuard`, `ResourceConsumeType`, `ResourceController`, and `ResourceGroupManager`, plus `tikv_util::resource_control::*`, `ControlledFuture`, `with_resource_limiter`, `ResourceManagerService`, `ResourceMetered`, `Config`, and `ResourceLimiter`. It exposes `channel`, `config`, and `worker` modules, while keeping `resource_group`, `service`, `resource_limiter`, and `metrics` internal.

`start_periodic_tasks` wires runtime background behavior. It creates a `ResourceManagerService`, schedules periodic advancement of minimal virtual time across resource groups, spawns an async watch for PD resource-group updates, starts `GroupQuotaAdjustWorker` to adjust background quota and priority quota limiters using IO bandwidth and compaction pressure, and spawns periodic RU metric reporting to PD. A priority adjust worker is intentionally disabled by comment because the algorithm is described as buggy.

State lives in the shared `ResourceGroupManager`, PD service watch, worker intervals, and atomic compaction pressure ratio. This module is an integration point between PD, TiKV worker scheduling, quota adjustment, and resource metrics. Risks include long-running async tasks tied to background worker lifetime, disabled priority adjustment leaving only background quota adjustment active, and facade stability due to broad re-exports.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/metrics.rs -->
# sources/storage-engines/tikv/components/resource_control/src/metrics.rs

`metrics.rs` registers Prometheus metrics for resource-control behavior. It covers background quota limits, aggregate background resource consumption, background task wait duration, priority quota limits, per-priority CPU time and wait histograms, background utilization, two-phase scheduling throttles, per-group historical/current RU rates, per-group quota limits, and admission-control delayed/rejected request counters and delay histograms.

All metrics are lazy static globals using Prometheus registration macros. Labels are intentionally bounded by resource type, priority, and resource group. `deregister_metrics(name)` removes per-resource-group label values for two-phase scheduling, quota, RU rates, and admission metrics, and also removes `"background"` admission labels. This supports cleanup when resource groups are deleted or refreshed.

No persistent state is stored here; metric series live in process memory and the Prometheus registry. Integration points include resource group manager, quota workers, admission control, and limiter code that update these series. Risks include stale time series if deregistration is missed, mismatch between dynamic group names and monitoring retention, and global registry panics if duplicate metric names are introduced. There are no direct tests in this file; validation is indirect through components that update and remove metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/metrics.rs -->
