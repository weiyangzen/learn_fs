# subset-b-008229 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/metrics.rs -->
# sources/object-store/rustfs/crates/common/src/metrics.rs

## Purpose
Central scanner and lifecycle metrics implementation for `rustfs-common`. It owns the process-wide `GLOBAL_METRICS`, records lifetime and last-minute scanner activity, tracks active scan paths and cycle state, emits selected `metrics` crate counters/histograms, and serializes report structs consumed by observability/admin layers.

## Important APIs, types, and functions
Key enums are `Metric`, `IlmAction`, `ScannerWorkSource`, and `ScanCyclePartialReason`. `Metrics` exposes synchronous recorders (`log`, `time`, `time_size`, `time_n`, `time_ilm`, `inc_time`), scanner-specific recorders for yield/throttle/ILM/transition/checkpoint/source work, async cycle/path accessors, and `report() -> ScannerMetricsReport`. `CurrentCycle::marshal/unmarshal` persists cycle metadata with `rmp_serde`. `current_path_updater` and `CloseDiskGuard` provide async callbacks for per-disk path tracking.

## Control flow
Callers either obtain `global_metrics()` or create a local `Metrics`. Operation timing APIs capture `SystemTime::now()` and return closures that update atomics and last-minute latency when invoked. Scanner cycles call `start_scan_cycle_work`, accumulate global counters during work, then `finish_scan_cycle_work` computes saturating deltas and stores last-cycle snapshots. `report()` gathers async cycle/path state, atomic counters, scanner pressure, maintenance-control status, lifetime maps, and last-minute maps into one serializable snapshot.

## State and persistence behavior
State is in memory: `AtomicU64`/`AtomicU8`/`AtomicBool` counters, `std::sync::Mutex` maps/options for short critical sections, and `tokio::sync::RwLock` maps for async path/cycle state. Only `CurrentCycle` has explicit binary marshal/unmarshal support. Ordering is mostly relaxed because these are telemetry counters, so report readers can observe mixed snapshots. `LockedLastMinuteLatency` intentionally clones into independent mutex-protected latency slots to avoid aliasing metrics.

## Dependencies and integration points
Depends on `crate::heal_channel::HealScanMode`, `crate::last_minute`, global init time, `chrono`, `serde`, `rmp_serde`, `tokio`, and the `metrics` facade. Scanner lifecycle, healing, replication, usage, and ILM code are expected to call the specific recorders. Observability exporters consume `ScannerMetricsReport` fields and OpenTelemetry metric names such as `rustfs_scanner_cycles_total`.

## Risks and edge cases
Relaxed atomics are appropriate for telemetry but not transactionally consistent. `current_path_updater` inserts the disk asynchronously with `tokio::spawn`, so very early reads can miss a newly registered path. `CloseDiskGuard::drop` silently skips cleanup without a Tokio runtime. `time_n` uses the original start time for all returned closures, which is correct for batch timing but surprising if reused. String labels and enum numeric indexes are compatibility-sensitive because reports expose both names and codes.

## Test signals
The module has broad Tokio/unit tests covering active path age, queue state, pacing pressure, checkpoint lifecycle, source-work accounting, lifecycle expiry/transition splits, transition queue snapshots, maintenance-control derivation, current/last cycle deltas, scan result labels, throttle config sanitization, cycle config, yield/throttle counters, and global metric-to-source mapping.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/readiness.rs -->
# sources/object-store/rustfs/crates/common/src/readiness.rs

## Purpose
Provides a tiny atomic readiness state machine for process startup, separating boot, storage readiness, IAM readiness, and full serving readiness.

## Important APIs, types, and functions
`SystemStage` is a `repr(u8)` enum with `Booting`, `StorageReady`, `IamReady`, and `FullReady`. `GlobalReadiness` wraps an `AtomicU8` and exposes `new`, `mark_stage`, `is_ready`, and `current_stage`.

## Control flow
`new` initializes the status to `Booting`. Components call `mark_stage`, which uses `fetch_max` to advance monotonically. Readers call `is_ready` for a strict full-ready check or `current_stage` for the decoded stage.

## State and persistence behavior
The only state is an in-memory atomic byte. `SeqCst` ordering is used for both updates and reads. State cannot regress through the public API, and invalid raw values fall back to `Booting` after a debug assertion.

## Dependencies and integration points
The file only depends on the standard atomic library. Higher-level readiness/liveness handlers can share a `GlobalReadiness` to gate traffic while storage and IAM caches initialize.

## Risks and edge cases
The monotonic `fetch_max` model cannot represent a later loss of readiness. `is_ready` only returns true for exactly `FullReady`, so future enum variants would need explicit handling. There is no global singleton here; integration code must decide ownership.

## Test signals
Tests cover the initial state, normal progression, no regression after full readiness, concurrent marking from threads, and `is_ready` returning true only at `FullReady`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/readiness.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/Cargo.toml -->
# sources/object-store/rustfs/crates/concurrency/Cargo.toml

## Purpose
Defines the `rustfs-concurrency` crate, a feature-gated facade for timeout, lock, deadlock, backpressure, and scheduler behavior used by RustFS I/O paths.

## Important APIs, types, and functions
The manifest enables default features `timeout`, `lock`, `deadlock`, `backpressure`, and `scheduler`. It depends on internal crates `rustfs-io-core` and `rustfs-io-metrics`, `tokio` with sync/time/rt, `tokio-util`, `thiserror`, and `tracing`.

## Control flow
Compile-time feature selection controls which modules in `src/lib.rs` are built and re-exported. Docs.rs is configured to build all features.

## State and persistence behavior
No runtime state is defined in the manifest. The relevant behavior is build-time dependency and feature resolution.

## Dependencies and integration points
This crate is the business-layer wrapper around shared I/O algorithms and metrics. Downstream crates import the facade while the manifest keeps reusable algorithms in `io-core` and instrumentation in `io-metrics`.

## Risks and edge cases
Default-enabling every feature means most consumers pay for all facade modules unless they opt out. Feature-dependent imports in `config.rs` assume the corresponding modules are available, so non-default feature combinations need compile coverage. Tokio dev features support tests only.

## Test signals
Manifest-level validation is indirect through `cargo test`/`cargo check` across feature combinations and docs.rs all-feature builds.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/backpressure.rs -->
# sources/object-store/rustfs/crates/concurrency/src/backpressure.rs

## Purpose
Implements the concurrency-layer backpressure facade for duplex pipes and maps simple buffer/watermark policy into `rustfs-io-core` admission pressure monitoring.

## Important APIs, types, and functions
`PipeBackpressurePolicy` stores `buffer_size`, `high_watermark`, and `low_watermark` and computes byte thresholds plus `to_core_config`. `BackpressureManager` owns the policy, derived `CoreBackpressureConfig`, and shared `CoreBackpressureMonitor`. `BackpressurePipe` wraps Tokio `DuplexStream` endpoints and exposes reader/writer/split/state/age/meta/backpressure checks. `BackpressurePipeMeta` is the compact snapshot.

## Control flow
Constructing a manager derives core config and monitor. `create_pipe` creates a Tokio duplex stream using the configured buffer size and shares the monitor. `should_apply_backpressure` delegates to the core monitor and records a backpressure activation metric when true.

## State and persistence behavior
State is in memory: manager policy/config, an `Arc` monitor, pipe endpoints, and pipe creation time. There is no persisted configuration or queue state in this facade.

## Dependencies and integration points
Integrates `rustfs_io_core::{BackpressureConfig, BackpressureMonitor, BackpressureState}`, `rustfs_io_metrics::backpressure_metrics`, Tokio I/O duplex streams, and any I/O code that wants pipe-level flow control.

## Risks and edge cases
`to_core_config` hard-codes `max_concurrent = 32` and 100 ms cooldown, so facade users cannot tune those core dimensions. The policy itself does not validate high/low watermarks; validation happens in `ConcurrencyConfig`. Duplex buffer occupancy is not directly fed into the core monitor in this file, so correctness depends on how the monitor is updated elsewhere.

## Test signals
Unit tests check default policy shape, conversion to core watermarks, default manager state, and pipe metadata/state creation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/backpressure.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/config.rs -->
# sources/object-store/rustfs/crates/concurrency/src/config.rs

## Purpose
Defines the top-level configuration object and validation rules for the concurrency facade.

## Important APIs, types, and functions
`ConcurrencyFeatures` carries booleans for timeout, lock, deadlock, backpressure, and scheduler with `all`, `none`, and `any_enabled`. `LockManagerPolicy` stores lock enablement and acquisition timeout. `ConcurrencyConfig` aggregates feature flags and each module policy. `from_env` reads selected environment variables. `validate` returns `ConfigError` variants for timeout, backpressure, and scheduler errors.

## Control flow
`Default` feature flags use `cfg!(feature = "...")`; policy defaults come from their module types. `from_env` overlays timeout defaults/max, backpressure buffer size, and scheduler base buffer size. `validate` enforces timeout ordering, high watermark greater than low and at most 100, and base buffer not exceeding max buffer.

## State and persistence behavior
The file defines cloneable in-memory config. Environment variables are read at construction time; there is no dynamic reload or persistence.

## Dependencies and integration points
Pulls policy types from `timeout`, `deadlock`, `backpressure`, and `scheduler`. `ConcurrencyManager::new` calls `validate` and panics on errors, making this the primary safety gate for facade construction.

## Risks and edge cases
Only four env vars are supported, leaving many policy fields unconfigurable from environment. `lock_policy.enabled` and `features.lock` can diverge. `validate` does not check low watermark bounds, zero buffer sizes, deadlock interval thresholds, or scheduler priority threshold ordering.

## Test signals
Tests cover default validation success, invalid default/max timeout, invalid min/max timeout, and feature helper behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/deadlock.rs -->
# sources/object-store/rustfs/crates/concurrency/src/deadlock.rs

## Purpose
Provides the concurrency-layer deadlock manager and lightweight request tracker around `rustfs-io-core` deadlock detection.

## Important APIs, types, and functions
`DeadlockMonitorPolicy` carries enablement, check interval, and hang threshold with `to_core_config`. `DeadlockManager` owns the policy, `Arc<CoreDeadlockDetector>`, and a Tokio mutex `running` flag. It exposes lifecycle, lock registration, request tracking, and `detect_deadlock`. `RequestTracker` records request metadata and lock resource names, forwarding acquire/release events to the core detector.

## Control flow
`from_policy` creates the core detector. `start` is no-op when disabled and otherwise idempotently flips `running` while logging lifecycle state. `track_request` registers a request with placeholder thread id `1`; tracker methods record lock acquire/release, and `Drop` unregisters the request.

## State and persistence behavior
All state is in memory inside the core detector, the manager running flag, and tracker-local resource map. There is no background loop implemented here despite the lifecycle naming.

## Dependencies and integration points
Integrates `rustfs_io_core::{DeadlockDetector, DeadlockDetectorConfig, LockType}`, `rustfs_io_metrics::deadlock_metrics`, Tokio mutexes, and `tracing`. Richer request-resource diagnostics are explicitly delegated to `rustfs::storage::deadlock_detector::RequestResourceTracker`.

## Risks and edge cases
The placeholder thread id means all acquisitions are attributed to one logical thread unless the core detector treats it abstractly. `start` logs but does not spawn periodic checks. `record_lock_acquire` always records lock type label `"read"` to metrics regardless of actual lock type. Consumers must call `record_lock_release` correctly.

## Test signals
Tests cover disabled manager creation, policy-to-core conversion, request tracking, lock registration, acquisition recording, and resource map visibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/deadlock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/lib.rs -->
# sources/object-store/rustfs/crates/concurrency/src/lib.rs

## Purpose
Crate root for RustFS concurrency management. It documents the facade architecture, denies missing docs and unsafe code, re-exports core I/O primitives, gates feature modules, and publishes a prelude.

## Important APIs, types, and functions
Public re-exports include `ConcurrencyConfig`, `ConcurrencyFeatures`, `ConcurrencyManager`, `GetObjectQueueSnapshot`, feature-specific managers/guards/policies, and selected `rustfs_io_core` types such as timeout errors, lock stats, backpressure state, scheduler types, and helper functions.

## Control flow
Compile-time `cfg(feature = "...")` declarations decide which modules and exports exist. The prelude mirrors those feature-gated exports plus the top-level manager/config types.

## State and persistence behavior
The crate root has no runtime state; it defines module boundaries and public API surface.

## Dependencies and integration points
This is the integration point between downstream RustFS services and lower-level `rustfs-io-core`/`rustfs-io-metrics`. The `workers` module is always public, while timeout/lock/deadlock/backpressure/scheduler are feature-gated.

## Risks and edge cases
`#![deny(missing_docs)]` makes new public exports fail compilation without docs. `config.rs` imports feature modules directly, so unusual feature sets should be checked. Broad re-exports couple the facade's semver surface to `io-core` types.

## Test signals
No direct tests in this file; compile tests across feature sets and downstream imports are the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/lock.rs -->
# sources/object-store/rustfs/crates/concurrency/src/lock.rs

## Purpose
Wraps core lock optimization with facade-level configuration, RAII guards, early release support, metrics, and tracing.

## Important APIs, types, and functions
`LockConfig` stores enablement and acquire timeout. `LockManager::new` creates `CoreLockOptimizer` with `LockOptimizeConfig`; accessors expose config, optimizer, stats, `optimize`, and enablement. `OptimizedLockGuard<G>` owns an optional underlying guard and can `early_release`. `LockScopeGuard<G>` is a minimal RAII wrapper.

## Control flow
Optimizing a guard calls `optimizer.on_acquire` and records whether optimization is enabled. Early release or drop takes the guard, computes hold time, calls `optimizer.on_release`, records lock hold time metrics, and logs release mode.

## State and persistence behavior
State is in memory: optimizer stats and guard-local acquisition time/release flag/resource string. There is no persisted lock state.

## Dependencies and integration points
Uses `rustfs_io_core::{LockOptimizer, LockStats}`, `rustfs_io_metrics::lock_metrics`, `tracing`, and caller-provided lock guard types such as mutex guards.

## Risks and edge cases
The manager ignores the separate `LockManagerPolicy` type and constructs `LockConfig` directly. Core options like max hold warning, adaptive spin, and max spin iterations are hard-coded. `as_ref` returns `None` after early release, so callers must handle optional access.

## Test signals
Tests create a manager and optimize a standard `Mutex` guard, then verify early release changes guard state.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/manager.rs -->
# sources/object-store/rustfs/crates/concurrency/src/manager.rs

## Purpose
Composes all feature-specific concurrency facades behind a single `ConcurrencyManager` and provides a small queue-utilization snapshot type for GetObject orchestration.

## Important APIs, types, and functions
`GetObjectQueueSnapshot` exposes `from_available_permits`, `permits_available`, `utilization_percent`, and `is_congested`. `ConcurrencyManager` stores `ConcurrencyConfig` and feature-gated `Arc` managers for timeout, lock, deadlock, backpressure, and scheduler. Constructors are `new`, `with_defaults`, and `from_env`; accessors and feature checks mirror enabled modules.

## Control flow
`new` validates config and panics if invalid, then builds each compiled feature manager from its policy. `start` starts deadlock monitoring only when the deadlock policy is enabled and logs feature status. `stop` stops the deadlock manager and logs shutdown.

## State and persistence behavior
Runtime state is in-memory manager arcs plus any state inside child managers. No config persistence or reload is implemented.

## Dependencies and integration points
Integrates all modules in the `rustfs-concurrency` crate and uses `tracing` for lifecycle events. Downstream services can keep one manager and pull subsystem managers as needed.

## Risks and edge cases
Invalid config causes a panic rather than a recoverable `Result`. Feature checks return config booleans, which can diverge from policy enablement and compile-time availability. `start` does not start scheduler/backpressure workers because those modules are passive facades.

## Test signals
Tests cover queue snapshot math, default manager creation, async lifecycle start/stop, and feature check calls.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/scheduler.rs -->
# sources/object-store/rustfs/crates/concurrency/src/scheduler.rs

## Purpose
Implements adaptive I/O scheduling facade logic: policy conversion, priority selection, and multi-factor buffer sizing.

## Important APIs, types, and functions
`SchedulerPolicy` defines base/max buffer sizes and high/low priority thresholds with `to_core_config`. `SchedulerManager` owns the policy, derived `IoSchedulerConfig`, and `CoreIoScheduler`; it exposes scheduler access, strategy creation, `calculate_buffer_size`, and `get_priority`. `IoStrategy` applies media, access-pattern, load, and concurrency adjustments.

## Control flow
The manager builds a core scheduler from derived config. Buffer calculation creates an `IoSchedulingContext`, asks core scheduler for a base strategy using file size, a 10 ms permit wait, and sequential flag, applies facade adjustments, records a scheduler-decision metric, and caps at max buffer size.

## State and persistence behavior
State is in-memory policy/core scheduler data. Each calculation is stateless except for metrics emitted by `rustfs-io-metrics`.

## Dependencies and integration points
Uses `rustfs_io_core` scheduler, `IoLoadLevel`, `IoPriority`, `AccessPattern`, `StorageMedia`, and `rustfs_io_metrics::io_metrics`. Consumers are read/write paths that need dynamic buffer sizes and priority classes.

## Risks and edge cases
The constructed `IoSchedulingContext` is currently unused after creation. Multiplicative adjustments can reduce sizes substantially and are cast through `f64` to `usize`. `low_priority_threshold` can be lower than high threshold unless config validation is expanded. The 10 ms permit wait is hard-coded.

## Test signals
Tests validate default config ordering, policy-to-core mapping, high-priority classification for small size, and positive buffer-size calculation for SSD sequential low-load reads.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/scheduler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/timeout.rs -->
# sources/object-store/rustfs/crates/concurrency/src/timeout.rs

## Purpose
Provides timeout policy conversion, adaptive timeout calculation, async operation wrapping, and manual cancellation guards for the concurrency facade.

## Important APIs, types, and functions
`TimeoutManagerPolicy` carries default/max/min timeout and dynamic enablement, with `to_core_config`. `TimeoutManager` exposes constructors, config/core-config accessors, `calculate_timeout`, `wrap_operation`, and `create_guard`. `TimeoutGuard` exposes elapsed timeout checks, remaining time, cancellation token cloning, and cancellation.

## Control flow
`new` derives `min_timeout` from default/max. `from_policy` clamps min to max before deriving core config. `calculate_timeout` returns default timeout when dynamic mode is disabled, otherwise calls `calculate_adaptive_timeout` and clamps to min/max. `wrap_operation` delegates to `tokio::time::timeout` and normalizes elapsed timeout to `TimeoutError::TimedOut`.

## State and persistence behavior
Manager state is immutable in memory. `TimeoutGuard` stores start time, timeout, and a `CancellationToken`; it does not spawn tasks or persist progress.

## Dependencies and integration points
Uses `rustfs_io_core::{TimeoutConfig, TimeoutError, calculate_adaptive_timeout}`, Tokio timeouts, and `tokio_util::sync::CancellationToken`. I/O operations can use either wrapping or cooperative cancellation.

## Risks and edge cases
The `history` argument to `calculate_timeout` is unused. `timeout_per_mb` is set to zero in core config, so adaptive behavior depends entirely on `calculate_adaptive_timeout` defaults. Wrapped futures must map errors into `TimeoutError`. Cancellation guards require callers to observe the token.

## Test signals
Tests cover default policy ordering, policy-to-core mapping, min-timeout sanitization for small max values, successful wrapped operations, and adaptive clamp behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/timeout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/workers.rs -->
# sources/object-store/rustfs/crates/concurrency/src/workers.rs

## Purpose
Implements a cooperative async worker-slot limiter for long-running background workflows.

## Important APIs, types, and functions
`Workers` contains a Tokio `Mutex<usize>` for available slots, `Notify` for waiters, and fixed `limit`. Public methods are `new`, `take`, `give`, `wait`, and `available`.

## Control flow
`new` rejects zero capacity and returns an `Arc<Self>`. `take` loops until a slot is available, otherwise waits on `Notify`. `give` saturating-adds a slot, clamps to the limit, and notifies one waiter. `wait` loops until all slots are available, waiting on notifications between checks.

## State and persistence behavior
All state is in-memory slot count. Over-release is clamped, preventing the available count from exceeding the configured limit.

## Dependencies and integration points
Uses Tokio synchronization primitives and `tracing` debug/trace events. Background scanners, healers, or migration jobs can share an `Arc<Workers>` to bound concurrency.

## Risks and edge cases
This is not a fair semaphore; notified task ordering is Tokio scheduling dependent. If a task takes a slot and exits without `give`, `wait` can block forever. The test intentionally over-releases, so callers should still pair take/give carefully.

## Test signals
Tests cover concurrent task slot use and `wait`, plus over-release clamping to the limit.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/concurrency/src/workers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/Cargo.toml -->
# sources/object-store/rustfs/crates/config/Cargo.toml

## Purpose
Defines the `rustfs-config` crate, which centralizes application constants and feature-gated configuration key sets for audit, notify, observability, OPA, and server config models.

## Important APIs, types, and functions
Default feature is `constants`. Optional features enable `const-str`, `serde`, and `serde_json` dependencies as needed. Package metadata identifies the crate as configuration management for RustFS.

## Control flow
Feature resolution controls which modules can compile. The `audit`, `notify`, and `constants` features enable compile-time string concatenation; `server-config-model` enables serialization dependencies.

## State and persistence behavior
No runtime state is defined. The manifest controls compile-time availability and dependency inclusion.

## Dependencies and integration points
This crate feeds constants to server startup, admin config, audit target parsing, observability setup, and model serialization code. Workspace lint settings apply.

## Risks and edge cases
Consumers that expect audit constants need the `audit` feature, while default builds only include constants. Doctests are disabled for the library, so example drift would not be caught by doctest.

## Test signals
Validation is through cargo feature builds and the unit tests in constant modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/amqp.rs -->
# sources/object-store/rustfs/crates/config/src/audit/amqp.rs

## Purpose
Declares valid config keys and environment variable names for AMQP audit targets.

## Important APIs, types, and functions
`AUDIT_AMQP_KEYS` lists config keys for enablement, URL, exchange, routing, mandatory/persistent flags, credentials, TLS material, queue directory/limit, and comments. `ENV_AUDIT_AMQP_*` constants and `ENV_AUDIT_AMQP_KEYS` provide the environment mapping.

## Control flow
There is no executable control flow; consumers iterate the key slices to validate config or bind env vars.

## State and persistence behavior
All values are compile-time string constants.

## Dependencies and integration points
Depends on shared config key constants such as `AMQP_URL`, `ENABLE_KEY`, and `COMMENT_KEY`. Re-exported by `audit/mod.rs` for audit subsystem parsers.

## Risks and edge cases
The env key array length must stay synchronized with individual constants. Secrets such as password and TLS key are included as env names, so downstream logging must avoid values. Config key and env key order differences could affect code that relies on positional mapping.

## Test signals
No local tests; compile-time references catch renamed shared keys, and integration tests should verify AMQP audit config/env parsing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/amqp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/kafka.rs -->
# sources/object-store/rustfs/crates/config/src/audit/kafka.rs

## Purpose
Declares Kafka audit target environment variables and valid configuration keys.

## Important APIs, types, and functions
Exports `ENV_AUDIT_KAFKA_*` constants for enablement, brokers, topic, acknowledgements, TLS, SASL, queue directory, and queue limit. `ENV_AUDIT_KAFKA_KEYS` groups env vars; `AUDIT_KAFKA_KEYS` groups config keys plus `COMMENT_KEY`.

## Control flow
No runtime control flow. Config loaders use the slices to whitelist and bind Kafka audit settings.

## State and persistence behavior
All state is static string metadata.

## Dependencies and integration points
References shared Kafka key constants in the config crate and is re-exported by `audit/mod.rs`. Audit target implementation code should use these names to parse server config and environment overrides.

## Risks and edge cases
TLS/SASL credentials are represented by names only, but downstream value handling must be secret-safe. Array sizes must be maintained manually. There is no validation here for broker syntax, ack modes, or SASL mechanism values.

## Test signals
No local tests; integration coverage should verify config/env aliases and invalid key rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/kafka.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/mod.rs -->
# sources/object-store/rustfs/crates/config/src/audit/mod.rs

## Purpose
Aggregates audit configuration modules, re-exports their constants, and defines audit subsystem identifiers.

## Important APIs, types, and functions
Declares submodules for AMQP, Kafka, MQTT, MySQL, NATS, Postgres, Pulsar, Redis, and Webhook. Exports `AUDIT_PREFIX`, `AUDIT_ROUTE_PREFIX`, subsystem names, `AUDIT_REDIS_DEFAULT_CHANNEL`, `AUDIT_STORE_EXTENSION`, and `AUDIT_SUB_SYSTEMS`.

## Control flow
There is no runtime control flow. Compile-time module inclusion plus public re-exports create the audit configuration namespace.

## State and persistence behavior
All values are static constants. `AUDIT_ROUTE_PREFIX` is built at compile time with `const_str::concat!`.

## Dependencies and integration points
Uses `crate::DEFAULT_DELIMITER` and all target modules. Config routing, subsystem validation, and audit target discovery consume `AUDIT_SUB_SYSTEMS`.

## Risks and edge cases
Adding a new audit target requires updating module declarations, re-exports, subsystem constants, and `AUDIT_SUB_SYSTEMS`. The Redis default channel lives in the aggregate module, so Redis target code must import from here or duplicate it.

## Test signals
No local tests; compile-time module checks and audit config integration tests are the expected signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/mqtt.rs -->
# sources/object-store/rustfs/crates/config/src/audit/mqtt.rs

## Purpose
Declares MQTT audit target environment variables and config keys, including reconnect, keepalive, queue, TLS, and websocket path allowlist settings.

## Important APIs, types, and functions
Exports `ENV_AUDIT_MQTT_*`, `ENV_AUDIT_MQTT_KEYS`, and `AUDIT_MQTT_KEYS`. Config keys include broker, topic, QoS, username/password, reconnect/keepalive intervals, queue directory/limit, TLS policy/material, trust-leaf-as-CA, websocket path allowlist, and comments.

## Control flow
No runtime control flow; consumers iterate the static slices.

## State and persistence behavior
All values are compile-time string constants.

## Dependencies and integration points
Depends on shared MQTT key constants from the crate root and is re-exported by audit aggregation. MQTT audit publisher setup should consume these constants.

## Risks and edge cases
The env key slice omits `COMMENT_KEY` by design while config keys include it. QoS, TLS policy, and websocket allowlist are not validated here. Manual array length maintenance is required.

## Test signals
No local tests; parser integration should verify every key is accepted and values are validated downstream.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/mqtt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/mysql.rs -->
# sources/object-store/rustfs/crates/config/src/audit/mysql.rs

## Purpose
Declares MySQL audit target config keys and environment variables.

## Important APIs, types, and functions
`AUDIT_MYSQL_KEYS` covers enablement, DSN string, table, format, TLS CA/client cert/client key, queue directory/limit, max open connections, and comments. `ENV_AUDIT_MYSQL_*` and `ENV_AUDIT_MYSQL_KEYS` expose matching environment names except comments.

## Control flow
No executable flow; downstream config code consumes the key lists.

## State and persistence behavior
Static constants only.

## Dependencies and integration points
References shared MySQL key constants and is re-exported through the audit module. MySQL audit storage/publisher code should use these keys to configure connection pooling and durable queues.

## Risks and edge cases
DSN and TLS key values are sensitive downstream. This file does not validate table names, format names, queue limits, or connection counts. Env/config arrays must stay aligned with implementation support.

## Test signals
No local tests; coverage should come from audit config parsing and MySQL target initialization tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/mysql.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/nats.rs -->
# sources/object-store/rustfs/crates/config/src/audit/nats.rs

## Purpose
Declares NATS audit target environment variables and valid config keys.

## Important APIs, types, and functions
Exports env constants for enablement, server address, subject, username/password, token, credentials file, TLS CA/client cert/client key/required flag, queue directory, and queue limit. `AUDIT_NATS_KEYS` mirrors those config keys and includes comments.

## Control flow
No runtime flow; consumers use static slices for parsing and validation.

## State and persistence behavior
All state is compile-time metadata.

## Dependencies and integration points
References shared NATS key constants from the config crate and is re-exported by `audit/mod.rs`.

## Risks and edge cases
Multiple auth mechanisms can be configured simultaneously; conflict resolution is outside this file. TLS-required semantics and credential file readability are downstream concerns. Array lengths are manually maintained.

## Test signals
No local tests; integration tests should cover env/config loading for each auth mode.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/nats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/postgres.rs -->
# sources/object-store/rustfs/crates/config/src/audit/postgres.rs

## Purpose
Declares PostgreSQL audit target config keys and environment variable names.

## Important APIs, types, and functions
`AUDIT_POSTGRES_KEYS` covers enablement, DSN, table, format, TLS required/CA/client cert/client key, queue directory/limit, and comments. `ENV_AUDIT_POSTGRES_KEYS` groups matching environment variables except comments.

## Control flow
No executable flow; the constants are consumed by config loaders.

## State and persistence behavior
Static strings only.

## Dependencies and integration points
References shared Postgres key constants and is re-exported by audit aggregation. PostgreSQL audit sink setup uses these constants for DSN, TLS, and queue configuration.

## Risks and edge cases
No validation for DSN, table, format, TLS combinations, or queue settings. Secrets must be masked by downstream logging. Manual env array sizing can drift.

## Test signals
No local tests; audit config integration tests should validate accepted keys and environment overrides.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/postgres.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/pulsar.rs -->
# sources/object-store/rustfs/crates/config/src/audit/pulsar.rs

## Purpose
Declares Apache Pulsar audit target environment variables and valid config keys.

## Important APIs, types, and functions
Exports env constants for enablement, broker, topic, auth token, username/password, TLS CA, insecure TLS, hostname verification, queue directory, and queue limit. `AUDIT_PULSAR_KEYS` mirrors config keys and includes comments.

## Control flow
No runtime control flow; the file is a schema/key registry.

## State and persistence behavior
All values are static constants.

## Dependencies and integration points
Uses shared Pulsar constants from the config crate and is re-exported by the audit module. Pulsar audit publisher code should use these names for server config and env overrides.

## Risks and edge cases
Auth token and username/password may conflict; resolution is downstream. TLS allow-insecure and hostname verification are sensitive security controls with no validation here. Array lengths must stay synchronized.

## Test signals
No local tests; integration should verify env mapping and TLS/auth validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/pulsar.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/redis.rs -->
# sources/object-store/rustfs/crates/config/src/audit/redis.rs

## Purpose
Declares Redis audit target environment variables and configuration keys, including retry, timeout, pipeline, queue, and TLS options.

## Important APIs, types, and functions
Exports 20 `ENV_AUDIT_REDIS_*` constants and `ENV_AUDIT_REDIS_KEYS`. `AUDIT_REDIS_KEYS` covers enablement, URL, channel, username/password, keepalive, queue dir/limit, retry attempts, min/max retry delays, connection/response timeouts, pipeline buffer size, TLS policy/material, insecure TLS, and comments.

## Control flow
No runtime flow; consumers iterate static key arrays.

## State and persistence behavior
Static string metadata only. The default Redis channel is declared in `audit/mod.rs`, not here.

## Dependencies and integration points
References shared Redis config key constants and is re-exported through `audit/mod.rs`. Redis audit sink code consumes these for connection setup and buffering behavior.

## Risks and edge cases
Many numeric/time values require downstream parsing and bounds checks. TLS allow-insecure is security-sensitive. Array length and config/env parity are manually maintained. The default channel being outside this file can surprise maintainers.

## Test signals
No local tests; integration coverage should validate retry/timeout/env parsing and default channel behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/redis.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/webhook.rs -->
# sources/object-store/rustfs/crates/config/src/audit/webhook.rs

## Purpose
Declares webhook audit target environment variables and config keys.

## Important APIs, types, and functions
Exports env constants for enablement, endpoint, auth token, queue limit/dir, client cert/key/CA, and skip TLS verify. `AUDIT_WEBHOOK_KEYS` mirrors config keys plus comments.

## Control flow
No executable flow; constants are used for validation and environment binding.

## State and persistence behavior
All values are compile-time strings.

## Dependencies and integration points
References shared webhook key constants and is re-exported by audit aggregation. Webhook target setup uses these keys for endpoint auth, mTLS, CA, queueing, and TLS verification behavior.

## Risks and edge cases
`WEBHOOK_SKIP_TLS_VERIFY` is present in env and config and must be treated carefully. Auth token and TLS key material are sensitive. No validation exists here for URL syntax, certificate paths, or queue limits.

## Test signals
No local tests; webhook audit config parsing and TLS behavior tests are the expected coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/audit/webhook.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/app.rs -->
# sources/object-store/rustfs/crates/config/src/constants/app.rs

## Purpose
Central application/server/observability constants for RustFS defaults, environment variable names, ports, TLS filenames, docs/license URLs, KMS settings, buffer profile, and binary size units.

## Important APIs, types, and functions
Exports application identity (`APP_NAME`, `VERSION`, `SERVICE_VERSION`), observability defaults, console/server defaults, TLS/cert filenames, URL prefixes, docs/GitHub/license URLs, server env vars, unsupported filesystem policy constants, KMS env/defaults, buffer profile env/default, region/license env vars, logging rotation defaults, `KI_B`, and `MI_B`. `const_str::concat!` builds default addresses and log filename constants.

## Control flow
No runtime logic beyond compile-time constant concatenation. Consumers read constants during config parsing, startup, and observability initialization.

## State and persistence behavior
All values are compile-time constants. They represent defaults and env names rather than mutable runtime state.

## Dependencies and integration points
Uses `const_str::concat`. Integrated by server startup, console setup, TLS loading, disk checks, unsupported filesystem policy, KMS configuration, observability logging/tracing/metrics/profiling, region/license handling, and adaptive buffer profile selection.

## Risks and edge cases
Hard-coded `VERSION`/`SERVICE_VERSION` can drift from package version unless release tooling updates them. `DEFAULT_ADDRESS` and `DEFAULT_CONSOLE_ADDRESS` bind by colon-only host notation, so platform parsing assumptions matter. The MinIO CI compatibility alias can unintentionally bypass disk checks if set in inherited environments.

## Test signals
Unit tests validate basic identity, logging defaults, environment names, TLS filename shape, port separation, address formatting, const-str concatenation, non-empty strings, finite numeric constants, and version/address consistency.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/app.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/body_limits.rs -->
# sources/object-store/rustfs/crates/config/src/constants/body_limits.rs

## Purpose
Defines bounded request/response body sizes for admin APIs and external S3 client responses to reduce memory-exhaustion risk.

## Important APIs, types, and functions
Exports `MAX_ADMIN_REQUEST_BODY_SIZE` (1 MB), `MAX_IAM_IMPORT_SIZE` (10 MB), `MAX_BUCKET_METADATA_IMPORT_SIZE` (100 MB), `MAX_HEAL_REQUEST_SIZE` (1 MB), and `MAX_S3_CLIENT_RESPONSE_SIZE` (10 MB).

## Control flow
No executable flow. HTTP/admin/S3 client code imports these constants when configuring body readers or validators.

## State and persistence behavior
Static numeric constants only.

## Dependencies and integration points
Integrated by admin request handlers, IAM import/export, bucket metadata import, healing APIs, and S3-compatible remote response readers.

## Risks and edge cases
The 100 MB bucket metadata import allowance is intentionally large and should be paired with streaming or careful allocation. Limits are compile-time constants, so deployments cannot tune them without code changes unless higher layers add env overrides. Duplicate rationale comments for S3 response size indicate documentation drift.

## Test signals
No local tests in this file; tests should assert handlers enforce these maximums and reject oversized bodies.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/body_limits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/capacity.rs -->
# sources/object-store/rustfs/crates/config/src/constants/capacity.rs

## Purpose
Defines environment variable names and defaults for capacity calculation scheduling, sampling, symlink behavior, metrics, and timeout/stall detection.

## Important APIs, types, and functions
Environment constants include scheduled interval, write trigger delay, write frequency threshold, fast update threshold, max files threshold, stat timeout, sample rate, metrics interval, symlink following/depth, dynamic timeout, min/max timeout, and stall timeout. Defaults include 120 s scheduled updates, 5 s write trigger, 5 writes/min threshold, 30 s fast threshold, 200k max files, 3 s stat timeout, sample rate 200, 600 s metrics interval, symlink following disabled, max symlink depth 3, dynamic timeout enabled, 2 s min timeout, 15 s max timeout, and 20 s stall timeout.

## Control flow
No runtime flow; capacity service configuration code imports these constants and parses corresponding env vars.

## State and persistence behavior
Static constants only.

## Dependencies and integration points
Used by capacity/statistics scanners and metrics emitters that need safe defaults for expensive filesystem traversal and sampling.

## Risks and edge cases
Defaults trade accuracy for cost through sampling and thresholds. Following symlinks is disabled by default for safety; if enabled downstream must guard loops and depth. Timeout defaults may be too short on slow or remote filesystems. Env parsing and bounds validation are outside this file.

## Test signals
Unit tests assert exact env var names and default values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/capacity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/compress.rs -->
# sources/object-store/rustfs/crates/config/src/constants/compress.rs

## Purpose
Defines HTTP response compression configuration constants, defaulting compression off to align with MinIO behavior.

## Important APIs, types, and functions
Exports env names and defaults for compression enablement, extension allowlist, MIME type allowlist, and minimum compressed size. Defaults are disabled, empty extension list, MIME types `text/*,application/json,application/xml,application/javascript`, and 1000 byte minimum size.

## Control flow
No executable flow; HTTP response code reads these constants through configuration parsing.

## State and persistence behavior
Static constants only.

## Dependencies and integration points
Integrated by server HTTP middleware or response writers that decide whether to compress content by env configuration, file extension, MIME type, and size.

## Risks and edge cases
Compression is security/performance-sensitive; enabling it for authenticated or secret-adjacent responses can expose side channels if not considered by higher layers. Wildcard MIME matching and extension normalization must be implemented downstream. Static defaults cannot express per-bucket or per-route policy.

## Test signals
No local tests; compression parser and HTTP response tests should verify accepted boolean values, MIME wildcard matching, extension handling, min-size enforcement, and disabled default.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/compress.rs -->
