# subset-b-008228 Research

Grouped research for the RustFS audit, checksums, and common crate files in work item `subset-b-008228`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/registry.rs -->
# sources/object-store/rustfs/crates/audit/src/registry.rs

## Purpose
`registry.rs` defines `AuditRegistry`, the audit crate's target registry and target factory façade. It owns a `TargetRuntimeManager<AuditEntry>` for live targets and a `TargetPluginRegistry<AuditEntry>` seeded with `builtin_target_plugins()`. Its role is to bridge RustFS audit configuration (`rustfs_config::server_config::Config` and `KVS`) to concrete `rustfs_targets::Target` implementations and to provide runtime target lookup, insertion, removal, and shutdown operations.

## Important APIs, Types, and Functions
`AuditRegistry::new` registers all built-in audit target plugins. `supports_target_type` and `create_target` expose plugin registry capabilities. `create_audit_targets_from_config` delegates bulk config/env parsing to `TargetPluginRegistry::create_targets_from_config(config, AUDIT_ROUTE_PREFIX)`, mapping `TargetError` into `AuditError`. Runtime APIs include `add_target`, `add_shared_target`, `remove_target`, `get_target`, `list_target_values`, `runtime_manager`, `runtime_manager_mut`, and `list_targets`. `close_all` removes and closes every live target, returning the first close error while still attempting all closes. `create_key` builds canonical `TargetID` strings from target type and target id. The older `enable_target`, `disable_target`, and `upsert_target` helpers create/check keys but only log state or insert into the runtime manager; actual enable/disable mutation is implemented by lower runtime abstractions in pipeline/runtime layers.

## Control Flow
Creation flow is plugin-driven: registered plugins interpret the audit config namespace and produce boxed `Target<AuditEntry>` values. Runtime mutation flow is manager-driven: boxed or shared targets are inserted into `TargetRuntimeManager`; removals call `remove_and_close`. Shutdown loops over a snapshot of keys, removes each target, awaits `close`, logs failed closes, and preserves only the first error for the return value.

## State and Persistence Behavior
State is in-memory only: plugin registrations and live target handles. Persistence, queues, and replay stores belong to target implementations and `rustfs_targets`. The registry does not persist target definitions itself. Debug assertions verify passed ids match target ids but are not runtime validation in release builds.

## Dependencies and Integration Points
The file depends on `rustfs_targets` for `TargetID`, target traits, shared target handles, plugin registry, runtime manager, and target errors. It depends on `rustfs_config` for the audit route prefix and config shape. It integrates upward with `AuditSystem`, `AuditRuntimeView`, `AuditRuntimeFacade`, and `AuditPipeline`, which wrap the registry behind locks.

## Risks and Edge Cases
`enable_target` and `disable_target` only check existence and log, so callers expecting state mutation must use runtime-layer APIs. `upsert_target` computes a key from separate type/id arguments but inserts the target under its own id via the manager, so mismatches are caught only by `debug_assert_eq!` in debug builds. `close_all` drains targets and returns the first close error; later errors are logged but not aggregated. Ordering depends on runtime manager key ordering.

## Test Signals
Unit tests assert that the AMQP factory is registered by default and that `close_all` calls close on both successful and failing targets, returns `AuditError::Target`, and clears registry contents. Integration tests exercise registry creation, config/env-only target creation, multiple webhook instance parsing, and fast empty-registry operations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/registry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/system.rs -->
# sources/object-store/rustfs/crates/audit/src/system.rs

## Purpose
`system.rs` defines `AuditSystem`, the high-level lifecycle manager for audit logging. It coordinates target registry access, system state, current configuration, replay worker cancellation, dispatch, reload, pause/resume, shutdown, runtime inspection, metrics, and performance validation.

## Important APIs, Types, and Functions
`AuditTargetMetricSnapshot` is a simple per-target metric DTO. `AuditSystemState` models `Stopped`, `Starting`, `Running`, `Paused`, and `Stopping`. `AuditSystem` stores `Arc<Mutex<AuditRegistry>>`, `Arc<RwLock<AuditSystemState>>`, `Arc<RwLock<Option<Config>>>`, and `Arc<RwLock<ReplayWorkerManager>>`. Public lifecycle methods are `start`, `pause`, `resume`, `close`, `reload_config`, `get_state`, and `is_running`. Dispatch APIs are `dispatch` and `dispatch_batch`. Target APIs include `enable_target`, `disable_target`, `remove_target`, `upsert_target`, `list_targets`, `get_target_values`, `get_target`, `snapshot_target_metrics`, `snapshot_target_health`, and `runtime_status_snapshot`. Observability APIs delegate to `observability::{get_metrics_report, validate_performance, reset_metrics}`.

## Control Flow
`start` rejects an already running system, tolerates concurrent starting with a warning, records metrics, stores the config, creates targets from config, sets `Starting`, and commits runtime targets to `Running`. `commit_runtime_targets` treats an empty target set as a stopped runtime: it clears current runtime targets and sets state to `Stopped`. Non-empty targets are activated through `AuditRuntimeFacade::activate_targets_with_replay` and swapped into the runtime via `replace_targets`. `dispatch` permits only `Running`, silently drops when `Paused`, and errors with `NotInitialized` otherwise. `dispatch_batch` is stricter and errors for any non-running state, including paused. `reload_config` stores the new config, records reload metrics, creates targets, and preserves `Paused` as the final state if the system was paused; otherwise the intended final state is `Running`, unless the target set is empty and `commit_runtime_targets` stops it. `close` transitions to `Stopping`, shuts down runtime targets and replay workers, clears config, logs stopped, and returns `Ok` even if shutdown logged an error.

## State and Persistence Behavior
All system state is in-memory and asynchronously locked. The saved config is a clone of the most recent config, including reload configs that stop the runtime. Replay worker state is held in `ReplayWorkerManager` and replaced or cleared with target runtime swaps. There is no direct disk persistence here; persistence is delegated to target queues/stores.

## Dependencies and Integration Points
The system depends on `AuditRegistry`, `AuditPipeline`, `AuditRuntimeFacade`, and `AuditRuntimeView`. It integrates with `rustfs_targets::ReplayWorkerManager` for replay lifecycle, `rustfs_config::Config` for target creation, and crate-level `observability` for metrics. It is the likely backend for global audit logger functions in the audit crate.

## Risks and Edge Cases
An empty config can make `start` return `Ok` but leave the system `Stopped`; tests document this as intended. `dispatch` and `dispatch_batch` have different paused behavior. `close` suppresses shutdown errors after logging, which simplifies callers but can hide partial close failures. `reload_config` writes the new config before target creation succeeds, so failed reloads can leave `config` reflecting a config that was not activated. Long target creation is done while holding the registry mutex because creation is called through a locked registry reference.

## Test Signals
The unit test `reload_with_empty_config_stops_existing_runtime` verifies that reload with empty config closes an existing target, clears replay workers, sets state to `Stopped`, and retains the new empty config. Integration/performance tests verify initial state, empty-config lifecycle, global metric increments, dispatch fast failure when stopped, concurrent state reads, and that close is idempotent for stopped systems.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/system.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/config_parsing_test.rs -->
# sources/object-store/rustfs/crates/audit/tests/config_parsing_test.rs

## Purpose
This test file documents audit target configuration conventions independently from concrete target implementations. It checks supported field names, section naming, environment variable shape, merge precedence, duration parsing expectations, URL syntax validation, and MQTT QoS parsing.

## Important APIs, Types, and Functions
Tests use `rustfs_config::server_config::KVS` and a local `parse_duration_test` helper. Covered webhook fields include `enable`, `endpoint`, TLS/client auth fields, batch/queue settings, retry settings, and timeout. MQTT fields cover broker/topic/auth, QoS, keepalive/reconnect intervals, queue settings, TLS options, and websocket path allowlist.

## Control Flow
The tests are pure unit checks. Config merge is simulated by extending default KVS with instance KVS, then environment KVS, establishing precedence as default < instance < environment. Duration parsing checks suffixes `ms`, `s`, `m`, and bare seconds. Environment parsing splits `RUSTFS_AUDIT_WEBHOOK_ENABLE_PRIMARY` into field `ENABLE` and instance `PRIMARY` at the last underscore.

## State and Persistence Behavior
No shared state or persistence is used. The file creates temporary KVS maps and parses literal strings.

## Dependencies and Integration Points
The tests reflect contracts consumed by `TargetPluginRegistry::create_targets_from_config` through `AuditRegistry`. URL validation uses the `url` crate. Field naming aligns with audit webhook and MQTT plugin expectations in `rustfs_targets`/audit factory code.

## Risks and Edge Cases
The tests validate conventions rather than invoking actual parser code for most cases, so they can drift from implementation. Duration behavior truncates `1000ms` to one second and would treat subsecond millisecond values as `Duration::from_millis`, but only seconds are asserted. FTP is noted as syntactically valid but likely unsupported. Environment variable parsing with fields containing underscores depends on splitting at the last underscore.

## Test Signals
Passing tests signal stable config field vocabulary, audit section prefixes (`audit_webhook`, `audit_mqtt`), env prefix construction (`RUSTFS_AUDIT_*`), merge precedence, accepted duration suffixes, basic URL syntax handling, and MQTT QoS limited to 0, 1, or 2.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/config_parsing_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/integration_test.rs -->
# sources/object-store/rustfs/crates/audit/tests/integration_test.rs

## Purpose
This integration test file exercises basic audit crate construction and parsing paths through public APIs. It verifies that `AuditSystem` and `AuditRegistry` can be created, that webhook config/env target creation does not require server storage in the covered cases, and that event/enable parsing conventions behave as expected.

## Important APIs, Types, and Functions
Tests use `rustfs_audit::*`, `AuditSystem::new`, `AuditRegistry::new`, `AuditRegistry::create_audit_targets_from_config`, `rustfs_config::server_config::{Config, KVS}`, `temp_env::with_vars`, and `rustfs_targets::EventName`. They construct `audit_webhook` config sections with `_` defaults and named `primary` instances.

## Control Flow
Async tests create empty or webhook-populated configs and call registry/system methods. The env-only test sets `RUSTFS_AUDIT_WEBHOOK_ENABLE_PRIMARY` and `RUSTFS_AUDIT_WEBHOOK_ENDPOINT_PRIMARY`, builds a single-thread Tokio runtime, and invokes target creation from an empty file config. Event parsing tests parse and expand S3 event names. Enable parsing tests lower-case strings and match truthy values.

## State and Persistence Behavior
State is temporary, except environment variables are scoped by `temp_env`. No target data is persisted. The tests intentionally avoid requiring server storage for basic target creation paths.

## Dependencies and Integration Points
These tests are cross-crate integration signals between audit, config, target event parsing, and environment-variable parsing. They are relevant to `AuditRegistry::create_audit_targets_from_config` and public audit initialization behavior.

## Risks and Edge Cases
The env-only test relies on process environment isolation from `temp_env`; parallel tests that use the same variables could interfere if not properly isolated. Assertions mostly check `is_ok` rather than inspecting produced targets, so they catch gross parser failures but not detailed target configuration regressions. Truthy enable parsing treats invalid values as false.

## Test Signals
The tests confirm initial `AuditSystem` state is `Stopped`, new registries are empty, webhook config/env parsing can succeed without initialized server storage for these paths, event names parse/expand/mask, and enable strings `1/on/true/yes` are truthy while `0/off/false/no/invalid` are false.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/integration_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/observability_test.rs -->
# sources/object-store/rustfs/crates/audit/tests/observability_test.rs

## Purpose
This file validates the audit observability API: event counters, target success/failure counters, EPS calculation, latency and error-rate reporting, global metric wrappers, reset behavior, and human-readable formatting for metric and performance reports.

## Important APIs, Types, and Functions
Tests use `rustfs_audit::observability::*`, including `AuditMetrics`, `AuditMetricsReport`, `PerformanceValidation`, global `record_*` functions, `get_metrics_report`, and `reset_metrics`. Important methods include `record_event_success`, `record_event_failure`, `record_target_success`, `record_target_failure`, `generate_report`, `get_target_success_rate`, `validate_performance_requirements`, `get_events_per_second`, `get_error_rate`, `reset`, `format`, and `all_requirements_met`.

## Control Flow
Most tests instantiate `AuditMetrics`, record synthetic successes/failures with `Duration` values, and assert derived report fields. Performance validation compares average latency against a 30 ms requirement and error rate against a 1% threshold. EPS tests record 100 events, sleep briefly, then require a positive/high EPS. Formatting tests check expected numeric formatting and pass/fail symbols in rendered strings.

## State and Persistence Behavior
`AuditMetrics::new` is local to each test. Global metric functions mutate process-global observability state and are reset in the test. There is no persistence beyond in-memory counters and timestamps.

## Dependencies and Integration Points
The observability layer is used by `AuditSystem::start`, `reload_config`, `get_metrics`, `validate_performance`, and `reset_metrics`. These tests define expected metric semantics for system-level reporting and performance gates.

## Risks and Edge Cases
Global metrics can leak across tests unless reset. EPS tests depend on wall-clock timing and can be sensitive to overloaded CI. Exact floating point equality is asserted for some simple ratios, so implementation changes to rounding could break tests. The formatted strings include Unicode pass/fail symbols, which callers parsing output should treat as presentation, not stable machine API.

## Test Signals
Signals include zero initial metrics, success/failure counts, error rate `(failures / all events) * 100`, latency averaged across successes and failures, default target success rate of 100% when no operations exist, reset clearing all counters, and performance validation producing recommendations on failed requirements.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/observability_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/performance_test.rs -->
# sources/object-store/rustfs/crates/audit/tests/performance_test.rs

## Purpose
This file provides synthetic performance and lifecycle checks for audit startup, target creation, dispatch, state transitions, registry operations, event mask/expansion helpers, and baseline throughput assumptions.

## Important APIs, Types, and Functions
Tests use `AuditSystem`, `AuditRegistry`, `AuditError`, `AuditEntry`, `ApiDetails`, `rustfs_targets::EventName`, Tokio `timeout`, and `Instant`. The main public methods covered are `start`, `close`, `dispatch`, `get_state`, `create_audit_targets_from_config`, `list_targets`, and `get_target`.

## Control Flow
Startup is timed with an empty config and must finish within five seconds. Target creation builds five webhook instances and allows either storage-related failure, other logged errors, or success, while still requiring completion within ten seconds. Dispatch builds a representative S3 `AuditEntry`; because empty config leaves the system stopped, dispatch must fail fast with `NotInitialized` in under 100 ms. Event mask and expansion helpers are called thousands of times and must stay under 100 ms. A synthetic 3000-event loop validates low CPU overhead relative to the 3k EPS/node target.

## State and Persistence Behavior
The tests use in-memory systems and configs only. No real target storage or network target is required. Cleanup calls `close` where applicable.

## Dependencies and Integration Points
This file connects audit performance expectations to `rustfs_targets::EventName`, config parsing, and the target registry. It also documents that actual EPS is expected to be constrained by network I/O rather than basic audit-entry construction or event helper logic.

## Risks and Edge Cases
Timing tests can be noisy in CI or under heavy load. Several tests print unexpected errors rather than failing, so they are coarse performance smoke tests rather than strict behavioral checks. The dispatch performance test intentionally depends on empty config leaving the system stopped; if lifecycle semantics change, this assertion must change.

## Test Signals
Expected signals are fast startup/close, fast target creation attempts, stopped state after empty-config start, fast dispatch failure when stopped, efficient event mask/expansion and empty registry operations, and synthetic core processing above 10k EPS with average latency below 1 ms.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/performance_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/pipeline_layer_test.rs -->
# sources/object-store/rustfs/crates/audit/tests/pipeline_layer_test.rs

## Purpose
This test file validates the audit pipeline/runtime abstraction layer around `AuditRegistry`: read-only runtime views, empty metric/health snapshots, replay worker stopping, empty activation, upsert/remove behavior, and replacement of runtime target sets.

## Important APIs, Types, and Functions
The tests use `AuditPipeline`, `AuditRegistry`, `AuditRuntimeFacade`, `AuditRuntimeView`, `ReplayWorkerManager`, `RuntimeActivation`, and the generic `rustfs_targets::Target` trait. A local `TestTarget` implements `Target<E>` with counters for `init` and `close`, plus no-op save/store methods.

## Control Flow
Empty registry tests assert list/get/snapshot APIs return empty values. Facade tests verify stopping replay workers is safe when none exist and activation of an empty list yields no targets/workers. Upsert tests call `AuditRuntimeView::upsert_target`, expect target initialization, list the canonical id, then remove and expect close. Replacement tests pass a `RuntimeActivation` containing one shared target and an empty replay manager, then confirm the registry and replay worker lock reflect the new state.

## State and Persistence Behavior
All state is held in `Arc<Mutex<AuditRegistry>>` and `Arc<RwLock<ReplayWorkerManager>>`. The local target has atomic counters, no persistent store, and always reports enabled/active.

## Dependencies and Integration Points
These tests are the most direct contract for `AuditRuntimeView`, `AuditRuntimeFacade`, and `AuditPipeline`, which are used by `AuditSystem` for target mutation, dispatch snapshots, replay activation, and runtime replacement.

## Risks and Edge Cases
The local target's id string must match runtime expectations (`primary:webhook`). Tests do not exercise failure from `init`, `close`, target stores, or replay workers, so error-path coverage is elsewhere or missing. Since the test target is generic over event type, trait bound changes in `rustfs_targets::Target` can break this file.

## Test Signals
Signals include safe empty operations, empty runtime snapshot behavior, upsert calling `init` exactly once, remove calling `close` exactly once, and facade replacement committing shared targets plus replay worker state.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/pipeline_layer_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/system_integration_test.rs -->
# sources/object-store/rustfs/crates/audit/tests/system_integration_test.rs

## Purpose
This file contains broader integration tests for the audit system lifecycle, metrics wiring, no-target dispatch, global audit functions, multi-instance config parsing, target type constants, concurrent state reads, and concurrent dispatch under load.

## Important APIs, Types, and Functions
Tests use `rustfs_audit::*`, `AuditSystem`, global functions such as `init_audit_system`, `dispatch_audit_log`, `is_audit_system_running`, `AuditLogger::instance`, `AuditLogger::is_enabled`, and `AuditLogger::log`. Helpers construct representative `AuditEntry` values with `ApiDetails`, headers, tags, request metadata, and `EventName::ObjectCreatedPut`.

## Control Flow
Lifecycle tests start with empty config and accept either storage-unavailable failure or success that leaves state `Stopped`. Metrics tests reset metrics, start the system, then assert system-start count increments and validation values are nonnegative. No-target dispatch accepts either success or `NotInitialized`. Global audit function tests ensure logging APIs do not panic when the system is not running. Multi-instance config creates default, primary, and secondary webhook entries and tolerates expected storage failure after parsing. Concurrent tests spawn ten state readers and one hundred dispatch tasks.

## State and Persistence Behavior
The system is in-memory. Global audit functions may touch singleton/global audit logger state. Config KVS maps are local. No real network or storage target is required.

## Dependencies and Integration Points
This file exercises public audit crate exports and their interaction with `rustfs_config`, `rustfs_targets::TargetType`, and global logger infrastructure. It is a consumer-facing safety net for API behavior under uninitialized/no-target conditions.

## Risks and Edge Cases
Several tests allow multiple outcomes to accommodate test environments without server storage, so they may miss detailed regressions. Global singleton state can cause ordering sensitivity if tests are run concurrently. Concurrent dispatch tests only require completion and consistent accounting, not a specific success/error distribution.

## Test Signals
Signals include `Stopped` initial and empty-config states, `close` idempotence, metric recording on start attempts, global logging safety when disabled, distinct `audit_log` and `notify_event` target types, safe concurrent state reads, and 100 concurrent dispatch attempts completing within five seconds.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/tests/system_integration_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/Cargo.toml -->
# sources/object-store/rustfs/crates/checksums/Cargo.toml

## Purpose
This manifest defines the `rustfs-checksums` library crate, described as checksum calculation and verification callbacks for HTTP request/response bodies generated by RustFS service clients. It packages checksum algorithms and HTTP checksum header/trailer helpers.

## Important APIs, Types, and Functions
The manifest exposes a library crate with doctests disabled. Metadata uses workspace edition, license, repository, rust version, version, and homepage. Runtime dependencies are `bytes`, `crc-fast`, `http`, `base64-simd`, `md-5`, `sha1`, and `sha2`. Dev dependency `pretty_assertions` supports unit tests.

## Control Flow
No executable control flow is present, but dependencies map directly to implementation: CRC algorithms from `crc-fast`, digest algorithms from hash crates, byte buffers from `bytes`, HTTP header types from `http`, and base64 encoding from `base64-simd`.

## State and Persistence Behavior
The crate has no configured persistence. Checksum state is in-memory digest state in code.

## Dependencies and Integration Points
The crate is intended to integrate with generated RustFS HTTP clients and S3-compatible checksum headers. Workspace dependency versions keep it aligned with the broader RustFS workspace.

## Risks and Edge Cases
The documentation URL uses `rustfs_checksum` singular while the crate name is `rustfs-checksums`; this may be intentional docs.rs naming or stale metadata. The manifest still includes `md-5` even though the public parser maps `md5` to CRC32, because internal MD5 tests/helper type remain.

## Test Signals
Tests are in source files and validate checksum values, HTTP header names/values, trailer sizes, and unknown algorithm errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/base64.rs -->
# sources/object-store/rustfs/crates/checksums/src/base64.rs

## Purpose
`base64.rs` is a small internal wrapper around `base64-simd` standard base64 encoding. It centralizes encoding, decoding, encoded-length calculation, and error presentation for checksum header values.

## Important APIs, Types, and Functions
`DecodeError` wraps `base64_simd::Error`, implements `std::error::Error`, and displays a stable `"failed to decode base64"` message while exposing the source error. `decode` returns decoded bytes from an input string. `encode` returns a standard base64 string for bytes. `encoded_length` returns the encoded length for a byte length.

## Control Flow
All functions delegate directly to `base64_simd::STANDARD`. `decode` maps the external error into `DecodeError`; `encode` and `encoded_length` are infallible wrappers.

## State and Persistence Behavior
No mutable state or persistence. All operations are pure conversions.

## Dependencies and Integration Points
Used by checksum tests and `http::HttpChecksum::header_value`/`size` to encode digest bytes and estimate trailer sizes. It hides the chosen base64 implementation from the rest of the crate.

## Risks and Edge Cases
The module is `pub(crate)` and marked `#![allow(dead_code)]`, so unused functions may remain for tests or future verification paths. Decode error display intentionally omits the detailed source text, which is available only through `source()`.

## Test Signals
No direct tests live in this file, but checksum tests use `base64::decode` to verify hex digest values and HTTP tests use `base64::encode` for expected empty-body digest headers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/base64.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/error.rs -->
# sources/object-store/rustfs/crates/checksums/src/error.rs

## Purpose
`error.rs` defines the public error type returned when a requested checksum algorithm name is not recognized.

## Important APIs, Types, and Functions
`UnknownChecksumAlgorithmError` stores the original algorithm string. `new` is crate-private and constructs the error. `checksum_algorithm` exposes the unknown value. `Display` renders a message listing accepted names: `crc32`, `crc32c`, `sha1`, `sha256`, and `md5`. It implements `std::error::Error`.

## Control Flow
The type is constructed by `ChecksumAlgorithm::from_str` in `lib.rs` when no case-insensitive match is found.

## State and Persistence Behavior
The only state is the owned algorithm string captured at parse time. No persistence.

## Dependencies and Integration Points
Integrated with Rust's `FromStr` trait for `ChecksumAlgorithm`; callers parsing algorithm strings can inspect the unknown value for diagnostics.

## Risks and Edge Cases
The display message includes `md5` as a known name even though parsing `md5` currently aliases to CRC32 instead of returning the deprecated `Md5` variant. If supported names change, this message must stay synchronized.

## Test Signals
`test_checksum_algorithm_returns_error_for_unknown` checks that the unknown string is preserved by `checksum_algorithm()`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/http.rs -->
# sources/object-store/rustfs/crates/checksums/src/http.rs

## Purpose
`http.rs` maps checksum implementations to S3/AWS-style HTTP checksum header names and values. It defines the `HttpChecksum` trait layered on top of the core `Checksum` trait.

## Important APIs, Types, and Functions
Public header constants include `x-amz-checksum-crc32`, `x-amz-checksum-crc32c`, `x-amz-checksum-sha1`, `x-amz-checksum-sha256`, and `x-amz-checksum-crc64nvme`. `MD5_HEADER_NAME` is crate-visible/dead-code allowed and maps to `content-md5`. `CHECKSUM_ALGORITHMS_IN_PRIORITY_ORDER` prefers CRC64NVME, CRC32C, CRC32, SHA1, then SHA256. `HttpChecksum` provides `headers`, `header_name`, `header_value`, and `size`. Implementations bind `Crc32`, `Crc32c`, `Crc64Nvme`, `Sha1`, `Sha256`, and `Md5` to their header names.

## Control Flow
`headers` consumes a boxed checksum, finalizes it through `header_value`, and inserts one header into a new `HeaderMap`. `header_value` finalizes digest bytes and base64-encodes them into a `HeaderValue`, expecting base64 output to always be header-safe. `size` estimates trailer field size as header-name length plus colon plus base64-encoded digest length.

## State and Persistence Behavior
State lives in the consumed checksum object until finalization. Header maps are newly allocated. No persistence.

## Dependencies and Integration Points
Depends on `http::HeaderMap/HeaderValue`, internal `base64`, and algorithm implementations from `lib.rs`. It is the HTTP-facing adapter for generated clients or S3-compatible body checksum/trailer code.

## Risks and Edge Cases
`header_value` consumes the checksum, so callers cannot update after header generation. `size` omits CRLF and optional whitespace; it models `name:value` bytes only. `HeaderValue::from_str(...).expect` is safe for standard base64 but would panic if the encoding implementation changed to emit invalid header bytes. MD5 support is internal/deprecated and public parsing of `md5` currently returns CRC32.

## Test Signals
Tests assert exact trailer sizes and empty-body header values for CRC32, CRC32C, CRC64NVME, SHA1, and SHA256. They verify canonical zero or known digest bytes after base64 encoding.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/http.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/lib.rs -->
# sources/object-store/rustfs/crates/checksums/src/lib.rs

## Purpose
`lib.rs` is the main implementation of the `rustfs-checksums` crate. It defines supported checksum algorithm names, algorithm parsing, the core `Checksum` trait, concrete checksum implementations, and public module exports.

## Important APIs, Types, and Functions
Public constants define names for CRC32, CRC32C, CRC64NVME, SHA1, SHA256, and MD5. `ChecksumAlgorithm` is a non-exhaustive enum defaulting to `Crc32`; `Md5` is deprecated. `FromStr` performs case-insensitive parsing and maps `md5` to `Crc32`. `into_impl` returns `Box<dyn http::HttpChecksum>`. `as_str` returns canonical names. The `Checksum` trait requires `update`, consuming `finalize`, and `size`. Private structs `Crc32`, `Crc32c`, `Crc64Nvme`, `Sha1`, `Sha256`, and `Md5` implement the trait.

## Control Flow
Parsing checks known names in sequence and returns an `UnknownChecksumAlgorithmError` if none match. `into_impl` constructs default digest state for the selected algorithm. CRC implementations use `crc_fast::Digest` with ISO-HDLC, iSCSI, and NVMe algorithms and return big-endian checksum bytes. SHA and MD5 implementations delegate to digest crates and copy finalized bytes into `Bytes`.

## State and Persistence Behavior
Each checksum struct owns incremental hasher state and is consumed on finalization. No global state or persistence is used.

## Dependencies and Integration Points
Exports `error` and `http` modules and keeps `base64` internal. Integrates with `bytes::Bytes`, `crc-fast`, `sha1`, `sha2`, `md-5`, and HTTP header helpers. Consumers typically parse a `ChecksumAlgorithm`, call `into_impl`, stream `update` calls, then produce HTTP headers through `HttpChecksum`.

## Risks and Edge Cases
`md5` parsing as CRC32 is a compatibility/security policy that may surprise callers expecting Content-MD5. The deprecated `Md5` enum variant still exists but is never returned by `FromStr`. CRC32C test is disabled on PowerPC/PowerPC64, implying architecture-specific concerns in the dependency. `sha1::Digest::as_slice`/`sha2::Digest::as_slice` may produce deprecation warnings depending on dependency versions. `ChecksumAlgorithm` is non-exhaustive, so downstream exhaustive matches are intentionally discouraged.

## Test Signals
Unit tests verify known digest outputs for `"test data"` across CRC32, CRC32C, CRC64NVME, SHA1, SHA256, and internal MD5, plus unknown algorithm error preservation. HTTP tests verify empty-body digest headers and trailer sizes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/checksums/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/Cargo.toml -->
# sources/object-store/rustfs/crates/common/Cargo.toml

## Purpose
This manifest defines the `rustfs-common` crate, a shared utility/data-structure crate for RustFS. It packages global state helpers, healing channel DTOs and messaging, last-minute metrics helpers, readiness exports, and other common modules.

## Important APIs, Types, and Functions
The crate uses workspace metadata and lints, disables doctests, and depends on `tokio`, `tonic`, `uuid`, `chrono`, `metrics`, `serde`, `rmp-serde`, `s3s`, and `tracing`. These dependencies correspond to async global locks/channels, gRPC channels, IDs, timestamps, serialization, S3 lifecycle/replication DTOs, and logging.

## Control Flow
No runtime flow is in the manifest. Dependency selection enables the code paths in `globals.rs`, `heal_channel.rs`, `last_minute.rs`, and exported readiness/metrics modules.

## State and Persistence Behavior
The manifest does not configure persistence. The crate's stateful behavior is process-global in code via `LazyLock`, `OnceLock`, async locks, atomics, and channels.

## Dependencies and Integration Points
`rustfs-common` is a foundational internal crate. Its dependencies suggest integration with server startup/readiness, cluster gRPC clients, S3 admin/heal logic, lifecycle/replication rules, and metrics reporting.

## Risks and Edge Cases
Because this crate carries global state utilities, dependency or API changes can have broad workspace impact. The `rmp-serde` and `metrics` dependencies are not visible in the researched files but likely support other modules not in this subset.

## Test Signals
Tests in researched modules validate heal channel labels/broadcasting and last-minute metric math. Manifest-level health depends on workspace dependency compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/bucket_stats.rs -->
# sources/object-store/rustfs/crates/common/src/bucket_stats.rs

## Purpose
`bucket_stats.rs` defines `ReplicationLatency`, a helper for tracking recent replication upload latency by object size category.

## Important APIs, Types, and Functions
`ReplicationLatency` owns a `last_minute::LastMinuteHistogram` named `upload_histogram`. `merge` merges another latency histogram into this one. `get_upload_latency` returns a `HashMap<String, u64>` from size bucket label to average latency in milliseconds. `update` records a size/duration sample. `size_tag_to_string` maps histogram indexes to human-readable size buckets from `<1 KiB` through `>1 GiB`.

## Control Flow
Updates go to the underlying histogram using `size` to choose a bucket. Reads call `get_avg_data`, iterate every returned `AccElem`, compute `avg()`, convert to milliseconds, and label each bucket. Merges delegate to `LastMinuteHistogram::merge`.

## State and Persistence Behavior
State is in-memory rolling histogram data. No persistence or synchronization is provided in this type; callers must handle sharing/mutability.

## Dependencies and Integration Points
Depends on `crate::last_minute`. It likely feeds bucket or replication metrics APIs elsewhere in RustFS. The returned `HashMap` is suitable for JSON/metrics reporting.

## Risks and Edge Cases
`ReplicationLatency` has no `Default` implementation in this file despite owning a private histogram, so construction may happen elsewhere or be incomplete. `get_upload_latency` returns labels for every histogram element; `LastMinuteHistogram` currently returns ten elements while `size_tag_to_string` only defines six explicit labels and maps the rest to `Size > 1 GiB`, causing duplicate labels to overwrite in the `HashMap`. Duration precision depends on `LastMinuteHistogram`/`AccElem`, which stores seconds, so millisecond output may be coarse or zero for subsecond durations.

## Test Signals
No tests live in this file. Behavior is indirectly constrained by extensive `last_minute.rs` tests for bucket windowing, averages, wraparound, and overflow.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/bucket_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/globals.rs -->
# sources/object-store/rustfs/crates/common/src/globals.rs

## Purpose
`globals.rs` provides process-global RustFS node settings and caches, including local node name, host/port/address, gRPC connection cache, TLS root certificate, outbound mTLS identity, TLS generation, and node initialization time.

## Important APIs, Types, and Functions
Global statics use `LazyLock<RwLock<...>>` for strings, optional cert/identity, connection map, and init time, plus `AtomicU64` for outbound TLS generation. Public setters/getters include `set_global_local_node_name`, `get_global_local_node_name`, `set_global_init_time_now`, `get_global_init_time`, `set_global_addr`, `set_global_root_cert`, `set_global_mtls_identity`, `set_global_outbound_tls_generation`, and `get_global_outbound_tls_generation`. Connection cache helpers are `evict_connection`, `has_cached_connection`, and `clear_all_connections`. `MtlsIdentityPem` stores cert and key PEM bytes.

## Control Flow
Setters acquire write locks and replace values. Getters acquire read locks and clone/copy values. Connection eviction removes one channel and logs if present. Clearing removes all cached channels and warns when anything was cleared. TLS generation uses relaxed atomic store/load.

## State and Persistence Behavior
All state is process-global and in-memory. There is no reset-all helper for every global; connection cache can be cleared explicitly. `GLOBAL_INIT_TIME` is optional until set. `GLOBAL_CONN_MAP` stores `tonic::transport::Channel` values by address.

## Dependencies and Integration Points
The file integrates with Tokio async synchronization, Tonic gRPC clients, Chrono UTC timestamps, and tracing. It is re-exported by `common/src/lib.rs`, making these globals part of the common crate public surface.

## Risks and Edge Cases
Global mutable state can create test ordering and multi-tenant issues. `set_global_root_cert` only sets `Some(cert)` and has no public clear function, while mTLS identity can be set to `None`. Relaxed ordering for TLS generation is enough for a simple version counter only if callers do not rely on memory synchronization. Connection cache invalidation must be called on node failure or TLS config changes to avoid stale channels.

## Test Signals
No tests are in this file. Expected behavior is inferred from simple setters/getters and logging on cache eviction/clear.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/globals.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/heal_channel.rs -->
# sources/object-store/rustfs/crates/common/src/heal_channel.rs

## Purpose
`heal_channel.rs` defines shared types and global messaging helpers for RustFS heal operations, plus lifecycle and replication rule helper functions used to decide whether healing-related work is active for prefixes.

## Important APIs, Types, and Functions
Constants include `HEAL_DELETE_DANGLING`, `RUSTFS_RESERVED_BUCKET`, and `RUSTFS_RESERVED_BUCKET_PATH`. Domain enums include `HealItemType`, `DriveState`, `HealScanMode`, `HealAdmissionDropReason`, `HealAdmissionResult`, and `HealChannelPriority`. DTOs are `HealOpts`, `HealChannelRequest`, and `HealChannelResponse`. `HealChannelCommand` has `Start`, `Query`, and `Cancel` variants with oneshot response senders. Global channel APIs are `init_heal_channel`, `get_heal_channel_sender`, `send_heal_command`, `send_heal_request_with_admission`, `send_heal_request`, `query_heal_status`, `cancel_heal_task`, `send_heal_disk`, `publish_heal_response`, and `subscribe_heal_responses`. Helper constructors create requests and responses. Rule helpers include `lc_has_active_rules` and `rep_has_active_rules`.

## Control Flow
`init_heal_channel` creates one unbounded mpsc command channel and stores the sender in a `OnceLock`; subsequent calls fail. Command send helpers package a command with a oneshot sender, send through the global channel, and await the response. Admission results are translated to `Ok(())` for accepted/merged or string errors for full/dropped. Broadcast responses use a lazily initialized broadcast channel of size 1024; `publish_heal_response` ignores the returned receiver count and reports success even with no subscribers. Lifecycle rule checks skip disabled rules, match prefixes, then look for expiration, noncurrent expiration, transitions, or delete-marker settings. Replication rule checks skip disabled rules and apply recursive/non-recursive prefix matching.

## State and Persistence Behavior
The command sender and response broadcaster are process-global `OnceLock`s. Requests/responses are in-memory channel messages; no persistence is performed. Request ids are generated with UUIDs in constructors. Heal options are serializable/deserializable and use serde renames for admin/API compatibility.

## Dependencies and Integration Points
Uses `tokio::sync::{mpsc, oneshot, broadcast}`, `uuid`, `serde`, and `s3s::dto` lifecycle/replication types. This file is a boundary between admin/API code that submits heal operations and the background heal manager that consumes commands.

## Risks and Edge Cases
The command channel is unbounded, so backpressure must be implemented by the consumer/admission policy, not the channel. The global command sender cannot be reset, which affects tests and process lifecycle. `HealScanMode` supports numeric and string deserialization, but invalid values fail. `publish_heal_response` discards broadcast send errors and always returns `Ok(())`; lagged subscribers must handle broadcast receiver errors. Prefix matching in lifecycle/replication helpers is subtle and may over/under-match if S3 rule semantics change.

## Test Signals
Unit tests validate stable admission labels/reasons and `is_admitted`. They also verify that a subscriber receives published heal responses and that publishing without subscribers is treated as success.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/heal_channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/last_minute.rs -->
# sources/object-store/rustfs/crates/common/src/last_minute.rs

## Purpose
`last_minute.rs` implements rolling last-minute accumulation primitives for latency/size statistics. It provides per-second ring-buffer accumulation (`LastMinuteLatency`) and size-bucketed histograms (`LastMinuteHistogram`).

## Important APIs, Types, and Functions
`AccElem` stores `total`, `size`, and count `n`, with `add`, `merge`, and `avg`. `LastMinuteLatency` stores 60 `AccElem` slots plus `last_sec`, with `merge`, `add`, `add_all`, `get_total`, and `forward_to`. `LastMinuteHistogram` stores a vector of `LastMinuteLatency` buckets and exposes `merge`, `add`, and `get_avg_data`. `size_to_tag` maps sizes to six categories. Private/dead-code types `TimedAction` and `SizeCategory` appear to be earlier or future helpers.

## Control Flow
`LastMinuteLatency::forward_to` advances the ring to a target timestamp: no-op for same/past time, clears all slots for gaps of 60 seconds or more, and otherwise clears each newly entered slot one second at a time. `add` uses current UNIX seconds, forwards, and adds a duration to the current slot. `add_all` does the same for an explicit timestamp and `AccElem`. `get_total` forwards to current time and merges all slots. `merge` aligns two windows to the later `last_sec`, then sums corresponding slots into a new `LastMinuteLatency`. Histogram `add` chooses a size bucket and records duration in that bucket.

## State and Persistence Behavior
State is in-memory and mutable. `AccElem::add` stores duration seconds only (`as_secs`), truncating subsecond data. `AccElem::merge` uses wrapping arithmetic for all fields, while `LastMinuteLatency::merge` sums fields with normal `+`, which can panic in debug on overflow. No synchronization is built in.

## Dependencies and Integration Points
Used by `bucket_stats::ReplicationLatency` for upload latency summaries. It depends only on `std::time`. The tests form a detailed behavior contract for rolling windows.

## Risks and Edge Cases
`LastMinuteHistogram` derives `Default`, leaving `histogram` empty; calling `add` on a default value indexes into an empty vector and will panic unless constructed elsewhere with buckets. `SIZE_LAST_ELEM_MARKER` is 10 while `size_to_tag` returns only 0-5, creating unused buckets if initialized to length 10. `LastMinuteHistogram::merge` ignores the returned merged latency from `LastMinuteLatency::merge`, so it may not actually update buckets as intended. Subsecond durations are truncated to zero in `AccElem`. Time moving backward is ignored by `forward_to`.

## Test Signals
Extensive tests cover `AccElem` defaults, add/merge/avg, subsecond truncation, wrapping overflow in `AccElem::merge`, ring forwarding for same/past/small/large gaps, explicit timestamp addition, same/different-time merges, wraparound, realistic 60-second windows, clone/debug behavior, boundary clearing at exactly 60 seconds, `get_total` with current timestamps, index calculation, concurrent-pattern simulation, and large values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/last_minute.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/lib.rs -->
# sources/object-store/rustfs/crates/common/src/lib.rs

## Purpose
`lib.rs` is the public entry point for `rustfs-common`. It declares common modules, re-exports global/readiness APIs, defines a default delimiter constant, and provides a `defer!` macro for scope-exit cleanup.

## Important APIs, Types, and Functions
Public modules are `bucket_stats`, `globals`, `heal_channel`, `last_minute`, and `metrics`; `readiness` is private but re-exported as `GlobalReadiness` and `SystemStage`. `DEFAULT_DELIMITER` is byte value `44` (`,`). `defer!` creates a local guard whose `Drop` runs a captured block at end of scope.

## Control Flow
Module declarations make submodules available to downstream crates. The `defer!` macro expands to a local `Guard<F: FnOnce()>` with an `Option<F>`; on drop it takes and invokes the closure, discarding the block's return value.

## State and Persistence Behavior
No state is stored in this file beyond constants. State comes from submodules and macro-created stack guards.

## Dependencies and Integration Points
Re-exporting `globals::*` makes process-global setters/getters available through `rustfs_common`. Re-exporting readiness types exposes system readiness coordination. `defer!` can be used throughout the workspace for cleanup patterns without adding a crate dependency.

## Risks and Edge Cases
The macro names its binding `_guard`; multiple `defer!` calls in the same scope may conflict or shadow in ways that affect drop order. Because the macro uses a local type named `Guard`, expansion hygiene should keep it scoped but diagnostics may be less clear. `DEFAULT_DELIMITER` uses a numeric literal rather than `b','`, which is less self-documenting.

## Test Signals
No tests are in this file. Submodule tests validate exported behavior for heal channels and last-minute metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/common/src/lib.rs -->
