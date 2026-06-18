# subset-b-008227 Research

This grouped report covers the exact source files assigned to `subset-b-008227`. Each source file has its own marker-delimited section so the report can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/obj.py -->
# sources/object-store/openstack-swift/swift/proxy/controllers/obj.py

## Purpose

`obj.py` implements Swift proxy object request handling. It routes object operations to either replicated or erasure-coded storage-policy controllers, performs authorization-delayed request validation, fans out PUT/POST/DELETE requests to object servers and container-update targets, reconstructs EC GET responses, and hides backend implementation details from clients.

## Important APIs and Types

`check_content_type` rejects client `Content-Type` parameters beginning with `swift_` unless middleware intentionally overrode the header. `num_container_updates` computes how many object-server requests need container-update headers so successful object writes also make durable container listings.

`ObjectControllerRouter` maps storage policy types to concrete object controllers using class registration. `BaseObjectController` owns shared GET/HEAD/PUT/POST/DELETE setup: it resolves container info, policy and object ring, validates ACLs and object metadata, handles object expiration headers, computes container/shard update targets, constructs backend headers, opens PUT connections, collects backend responses, and delegates policy-specific data transfer.

`ReplicatedObjectController` handles replicated storage policies. It reads client bytes once and writes each chunk to all successful `Putter` connections, requires replica quorum, verifies consistent backend ETags, and returns the best backend response.

`ECObjectController` handles erasure-coded policies. Its GET path widens client ranges to EC segment/fragment ranges, collects fragment responses into timestamp buckets, selects a durable reconstructible bucket, and returns an `ECAppIter` that decodes fragments into client bytes. Its PUT path encodes client chunks into EC fragments, streams each fragment to the chosen node/frag index, sends EC metadata footers, waits for first-phase acknowledgements, then sends a multiphase commit confirmation.

`Putter` wraps a backend PUT connection, state machine, timeout handling, chunked transfer framing, and final response collection. `MIMEPutter` extends it for metadata footers and multiphase EC commits. `chunk_transformer`, `trailing_metadata`, `client_range_to_segment_range`, and `segment_range_to_fragment_range` are the key pure helpers for EC PUT/GET conversion. `ECGetResponseBucket`, `ECGetResponseCollection`, and `ECFragGetter` coordinate EC GET fragment discovery, alternate-node hints, retry/fast-forward behavior, and response-part iteration.

## Control Flow

GET and HEAD resolve the container, storage policy, object ring partition, and a `NodeIter`, then call the policy controller's `_get_or_head_response`. Replicated GET/HEAD delegates to the shared `GETorHEAD_base`; EC HEAD also uses that path but fixes EC headers, while EC GET starts concurrent fragment GETs, groups responses by data timestamp, requests extras or alternates until it has enough durable fragments, builds an `ECAppIter`, and fixes conditional/range/client-visible headers.

PUT validates `If-None-Match`, container existence, metadata, content type, request size, expiration headers, and container-update headers. Shared code opens object-server connections with `Expect: 100-continue`. Replicated PUT streams identical chunks to all active putters and needs replica quorum. EC PUT removes client `Content-Length`/ETag from backend headers, calculates expected fragment archive size when possible, erasure-encodes full segments through `chunk_transformer`, writes per-frag metadata footers, enforces quorum on the first phase, and sends commit confirmations before collecting final durable responses.

POST sends metadata updates to primaries, detects mixed accepted/not-found results, and may retry missing primaries on handoffs before computing the best response. DELETE computes write-affinity local handoff counts when enabled, sets container-update headers, and treats backend 404s as client 204s through status overrides.

## State and Persistence

The controller itself is request-scoped and persists no durable local state. Durable effects are remote: object data files, EC fragment archives, durable marker files, object metadata, container database updates, async-pending container updates, and expirer queue updates are written by backend servers. In-memory state includes shard-update namespace cache data in request infocache/memcache, per-request putter state, EC response buckets, timeout/watchdog state, and logger thread locals.

## Dependencies and Integration Points

The file depends on Swift's common concurrency primitives, HTTP helpers, constraints, storage policies, swob responses, request helpers, and base proxy controller machinery. It integrates with container info lookups, object rings, container rings, expirer config, memcache-backed shard-range caching, object-server multipart footer support, PyECLib EC drivers, middleware footer callbacks, authorization hooks, CORS/delay-denial decorators, and backend node error limiting exposed by the proxy `Application`.

## Risks and Edge Cases

The highest-risk areas are EC range conversion and reconstruction, because suffix and multipart ranges must be widened to fragments then trimmed back exactly. EC GET bucket selection must avoid mixing timestamps or mismatched EC ETags, and must not serve non-durable fragments as complete objects. PUT streaming must handle client disconnects, slow clients, backend write failures, `If-None-Match` races, oversized bodies, mismatched ETags, and quorum response timing. Container update durability depends on the quorum math in `num_container_updates` and on correct shard target selection/caching. MIME multipart support depends on backend capability negotiation; old or partial deployments can surface as footer or multiphase support failures. The file mutates request headers such as `Range`, `Content-Length`, and EC sysmeta exposure, so ordering of `_fix_ranges`, `kickoff`, and `_fix_response` matters.

## Test Signals

Important tests should cover content-type rejection, container update count math, shard-update cache hit/miss/disabled behavior, PUT quorum and failure paths, replicated ETag mismatch, object expiration headers, POST mixed 202/404 handoff behavior, DELETE write-affinity handoff selection, EC client-range to segment/fragment conversions, EC GET bucket/tombstone/durable selection, EC GET alternate-node injection, EC multipart and suffix range responses, EC PUT footer metadata and commit phases, client timeout/disconnect handling, and backend capability negotiation for MIME footers/multiphase commits.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/obj.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/server.py -->
# sources/object-store/openstack-swift/swift/proxy/server.py

## Purpose

`server.py` is the Swift proxy WSGI application. It initializes proxy-wide configuration, rings, policy-specific override options, mandatory middleware insertion, request routing, request normalization, backend node sorting/error limiting, and paste.deploy app startup.

## Important APIs and Types

`ProxyOverrideOptions` parses per-policy and default options for node sorting, read/write affinity, write-affinity handoff delete counts, rebalance-missing suppression, concurrent GET behavior, and EC extra requests. `Application` is the WSGI final app and central integration object used by account, container, object, and info controllers.

`Application.__init__` loads timeouts, chunk sizes, cache recheck intervals, skip-cache percentages, account/container/object rings, storage policies, expirer config, CORS and info settings, request node count functions, owner headers, policy overrides, Swift info registration, and the global watchdog. `get_controller` maps `/info`, account, container, and object paths to controller classes; object routing additionally reads container policy and uses `ObjectControllerRouter`.

`handle_request` performs timestamp/token normalization, UTF-8/path/API checks, host-header denial, controller instantiation, transaction id setup, allowed-method checks, authorization preflight/delay-denial handling, and method dispatch. `sort_nodes`, `set_node_timing`, `error_limited`, `error_limit`, `error_occurred`, `check_response`, and `exception_occurred` provide backend node selection and health/error accounting. `modify_wsgi_pipeline` injects mandatory filters such as `catch_errors`, `gatekeeper`, `listing_formats`, `copy`, `dlo`, and `versioned_writes`. `parse_per_policy_config`, `app_factory`, and `main` are startup entry points.

## Control Flow

At startup, `app_factory` merges global/local config, parses `proxy-server:policy:<index>` sections, creates `Application`, and validates configuration. Each WSGI request is wrapped as a `Request`, normalized by `update_request`, validated by `handle_request`, mapped to a controller, authorized if the pipeline installed an auth hook, and dispatched to the controller method. Exceptions are converted to Swift HTTP responses while unhandled errors become HTTP 500.

Backend node ordering starts as a shuffle, then optionally sorts by stored timing or read-affinity. Backend response and exception helpers update the `ErrorLimiter`; object/account/container controllers call these helpers when backend servers timeout, throw, or return 5xx/507 responses.

## State and Persistence

The app stores process-local runtime state: rings, policy override objects, timing cache entries keyed by node IP, error limiter counters, config-derived booleans/limits, a statsd client, and a spawned watchdog. It writes no durable state itself; persistent data lives in backend rings, backend servers, object expirer data, and middleware/config files.

## Dependencies and Integration Points

The file integrates with Swift rings and storage policies, `swift.common.wsgi`, paste.deploy app factories, `swift.common.registry.register_swift_info`, account/container/object/info controllers, object expirer config, statsd metrics, node affinity helpers, mandatory middleware filters, authorization middleware through `swift.authorize`, and backend error-limiter logic.

## Risks and Edge Cases

Per-policy config parsing requires numeric policy indexes; invalid affinity expressions or sorting methods fail startup. `update_request` deliberately removes `Content-Length` when chunked transfer encoding is present to avoid request-smuggling risks. Cached container info with an unknown policy index causes service unavailable until workers reload policy definitions. Node timing is keyed only by IP, so timing data can blur devices/ports sharing an IP. Pipeline mutation depends on filter names and relative ordering; missing or renamed entry points can change middleware behavior. The class-level socket buffer tweak is legacy Python 2 only.

## Test Signals

Tests should exercise policy override parsing and validation, read/write affinity behavior, per-policy concurrent GET settings, request path routing, bad UTF-8/API paths, chunked plus content-length stripping, authorization delay-denial behavior, host-header denial, node sorting modes, error limiter increments and forced limits, mandatory middleware insertion order, app factory config parsing, and unknown storage policy handling.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/Cargo.toml -->
# sources/object-store/rustfs/crates/audit/Cargo.toml

## Purpose

This manifest defines the `rustfs-audit` library crate: an audit target management system for RustFS with multi-target fan-out, hot reload, observability, and replay/runtime integration.

## Important APIs and Types

The package uses workspace-managed edition, license, repository, rust-version, version, and homepage metadata. It disables doctests for the library. Runtime dependencies are the RustFS target abstraction, RustFS config with audit/constants/server-config-model features, S3 event types, async/concurrency crates, serialization, metrics, tracing, and Tokio. Dev dependencies provide async test traits, temporary environment helpers, and URL parsing.

## Control Flow

Cargo uses this manifest to compile the audit crate as a library. Feature selection is mostly delegated to workspace dependencies; the explicit Tokio features enable sync primitives, filesystem support, runtime flavors, time, and macros needed by the async audit system.

## State and Persistence

The manifest has no runtime state. It controls compile-time linkage to persistence-capable targets and replay stores through `rustfs-targets` and `rustfs-config`.

## Dependencies and Integration Points

The crate is tightly integrated with `rustfs-targets` for target plugins/runtime/replay, `rustfs-config` for audit target configuration, `rustfs-s3-types` for event names, `metrics` for metric emission, `tracing` for structured logs, and Tokio for async execution.

## Risks and Edge Cases

Because most versions and lints are workspace inherited, compatibility and MSRV risks sit at workspace level. Disabling doctests avoids doc example failures but also means public examples are not compiled. The audit crate depends on target/config feature flags; removing the `audit` or server config model features upstream would break this crate.

## Test Signals

Useful signals are `cargo check -p rustfs-audit`, unit/integration tests under `crates/audit/tests`, feature resolution against workspace dependencies, and lint enforcement through workspace lints.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/entity.rs -->
# sources/object-store/rustfs/crates/audit/src/entity.rs

## Purpose

`entity.rs` defines the serializable audit event contract for RustFS. It models object versions, API details, and full audit entries, plus builders used by request handling code to construct audit logs without manually filling every optional field.

## Important APIs and Types

`ObjectVersion` serializes as `{objectName, versionId?}` and has a `new` constructor. `ApiDetails` carries API name, bucket/object/object-list, status/status code, byte counters, header bytes, and latency strings; `ApiDetailsBuilder` provides chainable setters and `build`.

`AuditEntry` is the top-level audit log payload. Required fields are `version`, millisecond timestamp, S3 `EventName`, `trigger`, and `api`; optional fields include deployment/site, type, remote host, historical `requestID`, user agent, request path/host/node, claims/query/headers, response headers, tags, access key, parent user, and error. `AuditEntryBuilder::new` sets required fields and `Utc::now`, while chainable setters fill optional fields or override required fields.

## Control Flow

There is no asynchronous control flow. Callers build `ApiDetails`, then pass it with version/event/trigger into `AuditEntryBuilder::new`, optionally chain metadata setters, and serialize the resulting `AuditEntry` through serde before dispatching it to audit targets.

## State and Persistence

The file owns only data structures. Persistence is external: serialized `AuditEntry` values may be sent to audit targets, replay queues, logs, or external systems. `skip_serializing_if` keeps absent optional fields out of the JSON contract, and `chrono::serde::ts_milliseconds` fixes timestamp serialization.

## Dependencies and Integration Points

It depends on `chrono` for UTC timestamps, `hashbrown::HashMap`, `rustfs_s3_types::EventName`, `serde`, and `serde_json::Value`. It integrates with the pipeline through `EntityTarget<AuditEntry>`, with target plugins that serialize audit payloads, and with tests that protect external field names.

## Risks and Edge Cases

The serde field names are part of an external audit contract. The `request_id` field intentionally serializes as `requestID`, and accidental renames would break consumers. Several duration fields are strings rather than numeric types, so producers must keep formatting consistent. `Default` can create structurally incomplete audit entries if used directly instead of builders. Header/claim/tag maps can contain sensitive values unless callers sanitize before building the entry.

## Test Signals

Existing unit coverage verifies `requestID` serialization and absence of `request_id`. Additional useful tests should verify timestamp millisecond encoding, optional-field omission, builder setter coverage, object version field names, and JSON compatibility with expected external audit schemas.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/entity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/error.rs -->
# sources/object-store/rustfs/crates/audit/src/error.rs

## Purpose

`error.rs` centralizes the audit crate error type and the `AuditResult<T>` alias used across initialization, configuration, target dispatch, persistence, serialization, I/O, and task joins.

## Important APIs and Types

`AuditResult<T>` is `Result<T, AuditError>`. `AuditError` derives `thiserror::Error` and includes configuration errors with optional source, missing config, target errors from `rustfs_targets`, not initialized/already initialized states, storage unavailability, save/load config source errors, serde JSON errors, std I/O errors, and Tokio join errors.

## Control Flow

The enum is used by `?` conversions for target, serialization, I/O, and join failures. Explicit variants are constructed by global/system/pipeline code for logical states such as missing targets or unavailable configuration.

## State and Persistence

No state or persistence exists in this file. It shapes how lower-level persistent or network failures are surfaced to callers.

## Dependencies and Integration Points

It integrates with `rustfs_targets::TargetError`, `serde_json::Error`, `std::io::Error`, `tokio::task::JoinError`, and `thiserror`. Public re-export from `lib.rs` makes these errors part of the crate API.

## Risks and Edge Cases

`Configuration(String, Option<Box<dyn Error + Send + Sync>>)` can carry rich source errors but is awkward to construct consistently. Some variants such as `ConfigNotLoaded`, `StorageNotAvailable`, `SaveConfig`, and `LoadConfig` may be used by neighboring modules not included in this subset; callers need to preserve source context when mapping errors. Target dispatch currently may log target failures without returning an aggregate error, so `AuditError::Target` does not necessarily mean all delivery failures bubble up.

## Test Signals

Tests should verify `From` conversions, display strings, source preservation for boxed errors, and API behavior where global operations intentionally return `Ok(())` when the audit system is not initialized.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/factory.rs -->
# sources/object-store/rustfs/crates/audit/src/factory.rs

## Purpose

`factory.rs` exposes RustFS built-in audit target descriptors and plugin descriptors specialized for `AuditEntry` payloads.

## Important APIs and Types

`builtin_target_descriptors()` calls `rustfs_targets::catalog::builtin::builtin_audit_target_descriptors::<AuditEntry>()`. `builtin_target_plugins()` converts those descriptors into cloned `TargetPluginDescriptor<AuditEntry>` values.

## Control Flow

Runtime configuration loaders can call these functions to discover supported target types, validate fields, and create target instances. The file itself only maps catalog descriptors to plugin descriptors.

## State and Persistence

The file has no mutable state. Created target instances may persist queued messages or connect to external brokers depending on plugin configuration, but descriptor lookup itself is pure.

## Dependencies and Integration Points

It integrates with `rustfs-targets` built-in catalog descriptors and the audit crate's `AuditEntry` type. The tests use RustFS config constants and `ChannelTargetType` to validate AMQP plugin registration and target creation.

## Risks and Edge Cases

The factory relies on the target catalog to include all audit-capable targets. If the catalog changes field names or omits AMQP, tests should fail. `builtin_target_plugins` clones plugin descriptors; plugin descriptors must remain cheap and safe to clone. Misconfigured KVS values are validated by target plugin creation rather than this wrapper.

## Test Signals

Existing tests assert that an AMQP descriptor is present, exposes all configured AMQP keys, creates a target named `amqp`, preserves the configured id, and has no queue store when queue directory is empty. Broader coverage should check every built-in audit target type expected by the product.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/factory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/global.rs -->
# sources/object-store/rustfs/crates/audit/src/global.rs

## Purpose

`global.rs` provides the process-wide audit system facade. It lazily initializes a singleton `AuditSystem`, exposes lifecycle operations, dispatches audit entries when the system is running, reports target metrics, and offers the `AuditLogger` convenience type.

## Important APIs and Types

`init_audit_system` initializes a `OnceLock<Arc<AuditSystem>>`; `audit_system` reads it. `start_audit_system`, `stop_audit_system`, `pause_audit_system`, `resume_audit_system`, `reload_audit_config`, `audit_target_metrics`, and `is_audit_system_running` wrap the singleton. `dispatch_audit_log` accepts `Arc<AuditEntry>` and drops entries with structured logs when the system is uninitialized or not running. `AuditLogger::log`, `is_enabled`, and `instance` provide an ergonomic global logger facade.

## Control Flow

Lifecycle calls use the singleton when available; the `with_audit_system!` macro treats missing initialization as a logged no-op returning `Ok(())`. Starting is different: it always initializes then calls `AuditSystem::start(config)`. Dispatch first checks singleton presence, then asynchronously checks `system.is_running()`, then calls `system.dispatch(entry)` or logs a dropped event.

## State and Persistence

The only state here is the `OnceLock` singleton. Once initialized, it cannot be replaced in-process. Persistent target state and replay queues are owned by `AuditSystem` and lower layers. Dispatch accepts `Arc<AuditEntry>` to avoid unnecessary cloning at the global boundary.

## Dependencies and Integration Points

It integrates with `AuditSystem`, `AuditEntry`, RustFS server `Config`, target metric snapshots, and `tracing` structured logs. Public re-export from `lib.rs` makes this the easiest entry point for request/API code to start and use auditing.

## Risks and Edge Cases

Because `OnceLock` cannot be reset, tests and process lifecycle code must account for singleton persistence. Operations other than start silently succeed when uninitialized, which keeps callers simple but can hide missing initialization unless debug logs are monitored. Dispatch drops entries when paused/stopped rather than buffering at this layer. `AuditLogger::log` only logs dispatch errors; target-level partial failures may already have been converted to metrics/logs by the pipeline.

## Test Signals

Tests should cover start/stop/pause/resume/reload delegation, no-op behavior before initialization, dropped-entry logging when not running, `AuditLogger::is_enabled`, metrics empty vector before init, and singleton behavior across repeated `init_audit_system` calls.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/global.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/lib.rs -->
# sources/object-store/rustfs/crates/audit/src/lib.rs

## Purpose

`lib.rs` defines the public module surface for the RustFS audit crate and re-exports the primary types used by other RustFS components.

## Important APIs and Types

It declares modules `entity`, `error`, `factory`, `global`, `observability`, `pipeline`, `registry`, and `system`. Public re-exports include `ApiDetails`, `AuditEntry`, `ObjectVersion`, `AuditError`, `AuditResult`, all global facade functions, `AuditMetrics`, `AuditMetricsReport`, `PerformanceValidation`, `AuditPipeline`, `AuditRuntimeFacade`, `AuditRuntimeView`, `AuditRegistry`, `AuditSystem`, and `AuditTargetMetricSnapshot`.

## Control Flow

There is no runtime control flow. The file controls how downstream crates import audit functionality and which modules are part of the stable crate API.

## State and Persistence

No state or persistence exists here. It exposes stateful modules such as `global`, `system`, `pipeline`, and `observability`.

## Dependencies and Integration Points

This is the integration gateway for RustFS request handlers, configuration loaders, metrics collectors, and tests. It hides some module path depth by re-exporting common types.

## Risks and Edge Cases

Wildcard re-export of `global::*` exposes all global helper functions and `AuditLogger`, so additions to `global.rs` automatically become public API. Re-exporting broad runtime types couples downstream crates to `registry` and `system` internals. Adding/removing re-exports can be a semver-significant API change.

## Test Signals

Compile tests or downstream crate builds should verify that intended imports continue to work. API review should accompany module or re-export changes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/observability.rs -->
# sources/object-store/rustfs/crates/audit/src/observability.rs

## Purpose

`observability.rs` provides audit metrics, in-memory counters, metrics crate instrumentation, human-readable reports, and performance requirement validation.

## Important APIs and Types

`init_observability_metrics` registers metric descriptors once. `AuditMetrics` owns atomic counters for processed/failed events, total dispatch time, target successes/failures, config reloads, system starts, and an async `last_reset_time`. Methods record event/target/system activity, calculate EPS, average latency, error rate, target success rate, reset counters, generate reports, and validate performance. `AuditMetricsReport` and `PerformanceValidation` are report DTOs with `format` helpers. Global helpers such as `record_audit_success`, `record_target_failure`, `get_metrics_report`, `validate_performance`, and `reset_metrics` operate on a `OnceLock<Arc<AuditMetrics>>`.

## Control Flow

Constructing metrics registers descriptors. Record methods update atomics with relaxed ordering and emit `metrics` counters/histograms/gauges. Report generation reads atomics and computes derived values. Performance validation checks EPS >= 3000, average latency <= 30 ms, and error rate <= 1%, producing recommendations for failed constraints.

## State and Persistence

State is process-local and resettable: atomics plus `last_reset_time`. Metrics are also emitted to whatever global recorder the `metrics` crate has installed, but this module does not persist data itself. The global metrics singleton cannot be replaced once initialized, though counters can be reset.

## Dependencies and Integration Points

It depends on `metrics`, `const-str` for metric names, `tokio::sync::RwLock`, `OnceLock`, and `tracing`. `pipeline.rs` records dispatch and target metrics, while system/global code can record starts and config reloads. External Prometheus/exporter integration depends on the installed metrics recorder.

## Risks and Edge Cases

`record_event_failure` increments failed events but not processed events; total events are computed as processed plus failed, so naming must be understood by consumers. `dispatch_time.as_nanos() as u64/f64` can theoretically lose precision for very long durations. Relaxed atomics are fine for approximate metrics but not for strict synchronization. `PerformanceValidation::format` includes non-ASCII status symbols and bullets, which may matter for plain log consumers. EPS depends on the last reset time, so long-running idle periods can make throughput look poor.

## Test Signals

Tests should cover descriptor idempotence, success/failure counter updates, average latency/error-rate math, target success rate defaulting to 100% with no target ops, reset behavior, report formatting, performance validation thresholds, and global helper delegation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/observability.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/pipeline.rs -->
# sources/object-store/rustfs/crates/audit/src/pipeline.rs

## Purpose

`pipeline.rs` dispatches audit entries to configured targets, exposes a runtime view for target management, and wraps `rustfs-targets` runtime/replay activation for hot reload and reliable delivery.

## Important APIs and Types

`AuditPipeline` owns an `Arc<Mutex<AuditRegistry>>`. `dispatch` fans one `AuditEntry` to all current targets. `dispatch_batch` sends multiple entries to every target. `snapshot_target_metrics` returns delivery counters, and `snapshot_target_health` asks the registry runtime manager for health snapshots.

`AuditRuntimeView` provides runtime target inspection and mutation helpers: `list_targets`, `get_target_values`, `get_target`, `enable_target`, `disable_target`, `remove_target`, and `upsert_target`. Enable/disable currently validate and log state changes; they do not toggle target behavior in the registry.

`AuditRuntimeFacade` owns the registry, replay worker manager, and a `PluginRuntimeAdapter<AuditEntry>`. It builds a `BuiltinPluginRuntimeAdapter` with replay-event callbacks, supports `replace_targets`, `shutdown_runtime`, `activate_targets_with_replay`, and `stop_replay_workers`.

## Control Flow

`dispatch` snapshots target values under the registry lock, releases the lock, converts the audit entry into `EntityTarget<AuditEntry>` for each target, and awaits all target `save` futures with `join_all`. It records per-target success/failure metrics and records one audit success only if all targets succeeded; partial failures are logged and counted as audit failure but still return `Ok(())`.

`dispatch_batch` similarly snapshots targets, then creates one async task per target that loops through all entries sequentially for that target. It logs individual target failures and a batch completion summary but does not currently update global audit event metrics.

Runtime replacement locks both registry and replay workers, then delegates activation/shutdown to the adapter. Replay callbacks log delivered, retryable, dropped, permanent failure, retry exhausted, and unreadable entry events, updating target success/failure metrics and final-failure counters where appropriate.

## State and Persistence

Pipeline state is shared registry access. Target state lives in target implementations and runtime manager snapshots; replay persistence is managed by `rustfs-targets` stores/workers rather than this file. The facade stores replay worker manager state behind an async `RwLock`.

## Dependencies and Integration Points

The file integrates with `AuditRegistry`, `AuditEntry`, `AuditError`, observability helpers, `rustfs_targets` target traits, runtime adapters, replay worker manager and replay events, Tokio locks, futures `join_all`, and structured tracing. It is the bridge between generated audit entities and external audit sinks.

## Risks and Edge Cases

Dispatch clones the full `AuditEntry` once per target; large headers/claims/tags amplify memory cost. Partial target failure is logged and recorded but not returned to callers, so callers cannot directly retry from `dispatch` errors. `dispatch_batch` does not record the same audit success/failure metrics as single dispatch. `enable_target` and `disable_target` are currently logging-only checks, which can mislead callers expecting active state changes. Holding registry locks across runtime replacement is necessary for consistency but can block target inspection or dispatch snapshots. Replay callback behavior must stay aligned with target retry semantics or metrics will drift.

## Test Signals

Tests should cover no-target no-op dispatch, all-target success, partial failure metrics/logging, batch dispatch success/error accounting, target metric snapshots, runtime view missing-target errors, upsert initialization failure and replacement behavior, remove target behavior, replay event metric updates, and hot-reload target replacement with replay workers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/audit/src/pipeline.rs -->
