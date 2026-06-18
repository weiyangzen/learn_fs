# subset-b-008269 research

Grouped research report for RustFS madmin and notify files. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/info_commands.rs -->
# sources/object-store/rustfs/crates/madmin/src/info_commands.rs

Purpose: defines the Rust serializable data model behind admin info/status responses: disk inventory, backend topology, per-server properties, service health summaries, bucket/object usage counters, and the top-level `InfoMessage`. It is a wire-contract module, not an executor.

Important APIs/types/functions: `ItemState` maps `offline`, `initializing`, and `online` strings; constants mirror those values. `Disk`, `DiskMetrics`, and `HealingDisk` describe drive capacity, throughput, runtime state, inode counters, physical devices, and heal progress. `StorageInfo`, `BackendDisks`, `BackendInfo`, `BackendByte`, `BackendType`, `FSBackend`, and `ErasureBackend` represent FS/erasure layouts and parity/set counts. `ServerProperties`, `Services`, `Kms`, `Ldap`, `Status`, `Buckets`, `Objects`, `Versions`, `DeleteMarkers`, `Usage`, `ErasureSetInfo`, and `InfoMessage` model the admin response tree. `BackendDisks::sum` is the only aggregation helper.

Control flow: runtime logic is limited to enum/string conversion and simple summing. Most behavior is serde field mapping through `rename`, `default`, and `skip_serializing_if`; `InfoMessage` composes optional subsections for partial admin responses.

State and persistence: no persistence is performed. State is represented as deserialized snapshots from remote/admin APIs. Backward compatibility is explicit in optional disk fields such as `runtimeState`, capacity observation metadata, and `physicalDeviceIds`.

Dependencies/integration: depends on serde, `time::OffsetDateTime`, `SystemTime`, and `metrics::TimedAction`. It is publicly re-exported by `madmin::lib`, and consumed by admin clients and site replication/user types through `BackendInfo`.

Risks: the wire schema is sensitive to serde names, casing, and optional defaults. `ItemState::from_string` is case-sensitive. Several numeric values can be large but are plain `u64`/`usize`; callers must avoid interpreting missing optional fields as known zero values.

Test signals: extensive unit tests cover state conversion, defaults, value construction, serde round trips, msgpack legacy/forward compatibility for `Disk`, physical device serialization, backend sums, constants, debug formatting, and approximate memory sizing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/info_commands.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/lib.rs -->
# sources/object-store/rustfs/crates/madmin/src/lib.rs

Purpose: crate entry point for RustFS admin data contracts. It declares the module layout and chooses which modules are flattened into the public prelude.

Important APIs/types/functions: exposes modules `group`, `heal_commands`, `health`, `info_commands`, `metrics`, `net`, `policy`, `service_commands`, `site_replication`, `trace`, `user`, and `utils`. Public glob re-exports are limited to `group::*`, `info_commands::*`, `policy::*`, `site_replication::*`, and `user::*`.

Control flow: none. Compilation and public API shape are the behavior. Consumers can access all modules by path, but only selected schema families are available directly as `madmin::TypeName`.

State and persistence: no runtime state or persistence.

Dependencies/integration: integrates all sibling modules into one crate namespace. The limited re-export set matters for downstream imports: metrics, trace, service commands, health, net, and utils require module-qualified access unless separately re-exported elsewhere.

Risks: glob re-exports can create future name collisions between group/info/policy/site_replication/user schemas. Adding a new module is not enough to make its types prelude-visible; this file must be updated deliberately.

Test signals: no local tests. Coverage is indirect through compilation and tests in re-exported modules such as `info_commands.rs` and `user.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/metrics.rs -->
# sources/object-store/rustfs/crates/madmin/src/metrics.rs

Purpose: defines admin metrics wire models and aggregation logic for disks, scanner, OS, RPC, network, memory, batch jobs, site resync, and realtime rollups.

Important APIs/types/functions: `TimedAction::merge` adds count/time/bytes. `DiskMetric::merge`, `OsMetrics::merge`, `NetMetrics::merge`, `RPCMetrics::merge`, `ScannerMetrics::merge`, `BatchJobMetrics::merge`, `SiteResyncMetrics::merge`, and `RealtimeMetrics::merge` aggregate node samples. Scanner-specific snapshots model cycle progress, partial-cycle sources, pacing pressure, lifecycle transition queues, maintenance control, scan checkpoint state, and source work. `Metrics` holds optional category metrics and delegates merges.

Control flow: merge methods combine distributed samples. Timestamps choose freshest metadata for collected times, last ping/connect, site resync, and scanner status fields. Counters mostly add, many scanner counters use `saturating_add`; pressure and maintenance choose dominant state via priority helpers, then sort per-source vectors for deterministic output. `RealtimeMetrics` replaces per-host/per-disk entries while merging aggregated metrics.

State and persistence: no storage, but the structs are state snapshots. Aggregation mutates in-memory accumulators and preserves API field names with serde renames/defaults.

Dependencies/integration: depends on `chrono`, serde, `HashMap`, and `health::MemInfo`. `info_commands::DiskMetrics` reuses `TimedAction`; admin metric endpoints can stream host/disk entries into `RealtimeMetrics`.

Risks: integer addition in some merge paths is non-saturating (`RPCMetrics`, `NetMetrics`, maps), so extreme cumulative values could overflow in debug or wrap in release. Merge semantics are not uniform: some fields sum, some max, some replace with newest, and `BatchJobMetrics` overwrites jobs by ID. `Metrics::merge` currently ignores `mem` and `cpu`, so those categories are not aggregated.

Test signals: tests exercise scanner merge behavior for partial-cycle sources, pause pressure, lifecycle transition status, maintenance-control priority, and distributed status fields. Other merge paths rely mainly on compile/serde coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/net/mod.rs -->
# sources/object-store/rustfs/crates/madmin/src/net/mod.rs

Purpose: provides the admin network information shape and a platform-gated `get_net_info` constructor.

Important APIs/types/functions: `get_net_info(addr, iface) -> NetInfo` fills common node address and interface name. On Linux it returns a default `NetInfo` with address/interface only. On non-Linux it returns `NetInfo` with `NodeCommon.error` set to a not-implemented message. `NetInfo` contains `node_common`, `interface`, `driver`, and `firmware_version`.

Control flow: compile-time `cfg(target_os = "linux")` selects the implementation. There is no probing of driver, firmware, ethtool, or OS network state yet.

State and persistence: no persistence. Returned values are request-local snapshots; most fields remain default-empty.

Dependencies/integration: depends on serde and `health::NodeCommon`. It is exposed as `madmin::net`, but not glob re-exported by `lib.rs`.

Risks: `NetInfo` fields are private, which is fine for serde output from inside the crate but restricts downstream construction/inspection unless accessor APIs are added. Linux implementation can look complete while omitting driver/firmware/error data. Non-Linux callers get an error string but still receive the requested interface.

Test signals: no local tests. Current behavior is compile-time validated only; future platform probing should add Linux and non-Linux unit or integration tests around populated fields and error semantics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/net/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/policy.rs -->
# sources/object-store/rustfs/crates/madmin/src/policy.rs

Purpose: defines the admin policy-info wire schema.

Important APIs/types/functions: `PolicyInfo` contains `policy_name`, arbitrary JSON `policy`, and optional `create_date`/`update_date` timestamps. It derives serde traits and `Debug`.

Control flow: no executable logic. Serde omits absent dates, allowing old or partial admin responses to carry just the name and policy JSON.

State and persistence: no persistence. The module represents policy state returned by or sent to admin endpoints. The policy body stays as `serde_json::Value`, leaving semantic validation to IAM/policy code outside this crate.

Dependencies/integration: depends on serde, `serde_json::Value`, and `time::OffsetDateTime`. It is glob re-exported by `lib.rs`, making `PolicyInfo` part of the crate’s top-level public contract.

Risks: arbitrary JSON means malformed policy semantics can pass this layer. Optional timestamps do not use an explicit serde RFC3339 adapter here, so compatibility depends on `time` serde behavior enabled in the workspace.

Test signals: no local tests. Validation is indirect through downstream policy parsing and serde compilation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/policy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/service_commands.rs -->
# sources/object-store/rustfs/crates/madmin/src/service_commands.rs

Purpose: parses service trace query options into a trace bitmask and threshold settings for admin/service trace commands.

Important APIs/types/functions: `ServiceTraceOpts` stores booleans for S3, internal, storage, OS, scanner, decommission, healing, batch replication/key rotation/expire/all, rebalance, replication resync, bootstrap, FTP, ILM, error-only filtering, and a `Duration` threshold. `trace_types` builds a `TraceType` mask. `parse_params(&Uri)` reads query parameters and parses `threshold` via `utils::parse_duration`.

Control flow: `parse_params` splits the URI query on `&` and `=`, defaults missing values to `"false"`, sets booleans only when value is exactly `"true"`, expands `all=true` to S3/internal/storage/OS, and parses optional threshold. `trace_types` handles `batch_all` by enabling all batch trace bits.

State and persistence: state is in the mutable options struct for one parsed request. No persistence.

Dependencies/integration: depends on `hyper::Uri`, `trace::TraceType`, and `utils::parse_duration`/`humantime`. It bridges HTTP query strings to trace filtering.

Risks: query parsing is ad hoc: it does not percent-decode, ignores repeated keys except the last via `HashMap`, and loses values containing `=`. `batch_all` is not populated by `parse_params`, so only direct struct construction can currently trigger all batch trace bits. `only_errors` is parsed but not used in `trace_types`.

Test signals: no local tests. Duration parsing is covered in `utils.rs`; trace option parsing needs focused tests for `all`, threshold errors, repeated keys, and batch flags.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/service_commands.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/site_replication.rs -->
# sources/object-store/rustfs/crates/madmin/src/site_replication.rs

Purpose: large wire-contract module for site replication administration: peer/site membership, IAM and bucket metadata replication, IDP settings, status summaries, replication metrics, remove/edit/resync operations, and site network performance results.

Important APIs/types/functions: `SITE_REPL_API_VERSION` is `"1"`. Core topology types include `PeerSite`, `PeerInfo`, `SiteReplicationInfo`, `SRPeerJoinReq`, `SRStateInfo`, `SRStateEditReq`, and `SyncStatus`. IAM/bucket change models include `SRPolicyMapping`, `SRSTSCredential`, `SRExternalUser`, `SRLDAPUser`, `SRIAMUser`, `SRGroupInfo`, `SRSvcAccUpdate/Delete/Change`, `SRCredInfo`, `SRIAMItem`, `SRBucketMeta`, `SRBucketInfo`, `SRIAMPolicy`, and `ILMExpiryRule`. Status/metrics types include `SRStatusInfo`, per-entity mismatch summaries, `SRSiteSummary`, `SRMetricsSummary`, `SRMetric`, queue/worker/window counters, and `SiteNetPerfResult`.

Control flow: only helper logic is `deserialize_vec_null_default`, which turns `null` site lists into empty vectors. Behavior is otherwise serde mapping, defaults, and omission of empty fields.

State and persistence: no direct persistence. The structs mirror replicated configuration and operational snapshots, heavily using `BTreeMap` for deterministic maps and timestamp fields for conflict/age visibility.

Dependencies/integration: imports group/user service-account types from the crate, serde, `serde_json::Value`, `HashMap`/`BTreeMap`, and `time::OffsetDateTime`. It is glob re-exported by `lib.rs`, so schema stability is externally visible.

Risks: the module carries many exact JSON field names, including mixed casing and hyphenated names; compatibility can break with small rename changes. Sensitive fields such as access keys and secret keys are present in serializable structs. Many values are generic `Value` or `String`, so semantic validation is elsewhere.

Test signals: no local tests in this file. Confidence comes from serde derives and downstream API tests; high-value additions would cover null-vector compatibility, timestamp serialization, and representative SR status round trips.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/site_replication.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/trace.rs -->
# sources/object-store/rustfs/crates/madmin/src/trace.rs

Purpose: defines trace type bitmasks and trace-event payload schemas for admin/service tracing.

Important APIs/types/functions: `TraceType(u64)` exposes constants for OS, storage, S3, internal, scanner, decommission, healing, batch jobs, rebalance, replication resync, bootstrap, FTP, ILM, and `ALL`. Methods `new`, `contains`, `overlaps`, `single_type`, `merge`, `set_if`, and `mask` implement bitmask operations. `TraceInfo` is the current event payload; `TraceInfoLegacy` wraps request/response/stats/storage/OS legacy shapes. Supporting structs include `TraceHTTPStats`, `TraceCallStats`, `TraceRequestInfo`, `TraceResponseInfo`, `StorageStats`, and `OSStats`.

Control flow: bitmask methods are simple bitwise checks/mutations. Payload structs rely on serde renames and optional omissions. `TraceInfo::mask` converts stored numeric type back into `TraceType`.

State and persistence: no persistence. Trace records are transient serialized event snapshots with timing, path, bytes, messages, errors, custom key/value data, HTTP stats, and optional heal result.

Dependencies/integration: uses `chrono::DateTime<Utc>`, serde, `Duration`, `HashMap`, and `heal_commands::HealResultItem`. `service_commands.rs` builds `TraceType` masks from URI parameters.

Risks: many payload fields are private, preventing direct downstream construction and making serde the main access path. `Duration` serde compatibility must match trace consumers. `ALL` assumes metrics-all remains last; adding a new trace constant requires updating the mask width.

Test signals: no local tests. Bitmask operations and trace serde round trips are not directly covered in this module.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/trace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/user.rs -->
# sources/object-store/rustfs/crates/madmin/src/user.rs

Purpose: models admin IAM users, access keys, service accounts, account access summaries, site-replication service-account exports, and IAM import/entity results.

Important APIs/types/functions: `AccountStatus` serializes enabled/disabled and implements `AsRef<str>`/`TryFrom<&str>`. `UserAuthType`, `UserAuthInfo`, `UserInfo`, and `AddOrUpdateUserReq` cover users. `ServiceAccountInfo`, list responses, `AddServiceAccountReq`, `UpdateServiceAccountReq`, `Credentials`, `AddServiceAccountResp`, `InfoServiceAccountResp`, `InfoAccessKeyResp`, LDAP/OpenID-specific info, and access-key list constants cover service-account APIs. Validation helpers enforce name, description, and expiration rules. `SRSessionPolicy` preserves raw JSON/null for replication. `SRSvcAccCreate` and IAM import/entity structs support site replication/import reporting.

Control flow: request `validate` methods delegate to helpers: names may be empty but, if set, must be <=32 chars, ASCII alphanumeric/underscore/hyphen, and start with a letter; descriptions are <=256 bytes; expiration must be future unless unix timestamp zero. Policy values are normalized so JSON strings become JSON objects when parseable. Service-account expiration deserialization accepts RFC3339 and a legacy exported format, trims empty strings, and maps zero timestamp to `None`.

State and persistence: no storage. The module represents persisted IAM state and import/export payloads, including raw session policy JSON to avoid lossy replication.

Dependencies/integration: uses serde, `serde_json::Value`/`RawValue`, `time`, and `BackendInfo`. `site_replication.rs` imports `SRSvcAccCreate` and `UserInfo`; `lib.rs` re-exports this module.

Risks: several structs serialize credentials/secrets. Validation uses byte length for descriptions but char iteration for names; expiration validation depends on current UTC time. Raw policy equality is textual, so semantically equivalent JSON with different formatting may compare unequal.

Test signals: broad unit tests cover account status conversion/serde, user/service-account construction, validation success/failure, generated credentials, stringified policy JSON, missing policies, credential serialization, access/account summaries, round trips, debug/memory checks, edge cases, empty/legacy/RFC3339 service-account expiration handling.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/user.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/utils.rs -->
# sources/object-store/rustfs/crates/madmin/src/utils.rs

Purpose: small utility module currently dedicated to human-readable duration parsing.

Important APIs/types/functions: `parse_duration(s: &str) -> Result<Duration, String>` wraps `humantime::parse_duration` and converts the parser error to a `String`.

Control flow: no custom parsing logic remains despite comments suggesting one. All duration grammar, units, and error wording are delegated to `humantime`.

State and persistence: none.

Dependencies/integration: depends on `std::time::Duration` and the `humantime` crate. `service_commands.rs` uses it to parse trace threshold query parameters.

Risks: accepted syntax is exactly `humantime` syntax, which may be broader than the admin API intends. Returning `String` errors loses structured error information. Comments are stale and could mislead maintainers into thinking the parser is custom.

Test signals: unit test `test_parse_dur` verifies `3s`, `3ms`, `3m`, and `3h` map to expected `Duration` values. Invalid input and compound durations are not covered here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/Cargo.toml -->
# sources/object-store/rustfs/crates/notify/Cargo.toml

Purpose: package manifest for `rustfs-notify`, the RustFS notification service crate that delivers real-time file/object events to configured targets.

Important APIs/types/functions: declares package metadata, workspace-managed edition/license/repository/rust-version/version/homepage, docs.rs documentation, keywords/categories, library doctests disabled, and Criterion bench `snapshot_mode_scan` with `harness = false`.

Control flow: Cargo uses this file to resolve build graph, features, benches, and lint inheritance. There is no runtime code.

State and persistence: no runtime state. Dependency choices indicate persisted/queued notification behavior through `rustfs-targets`, config models, and queue-related target configuration used in examples.

Dependencies/integration: internal crates include `rustfs-config` with notify/constants/server-config-model features, `rustfs-ecstore`, `rustfs-s3-types`, `rustfs-s3-ops`, `rustfs-targets`, and `rustfs-utils`. External dependencies include `arc-swap`, `async-trait`, `chrono`, `form_urlencoded`, `hashbrown`, `percent-encoding`, `rayon`, `rustc-hash`, serde, `starshard`, `thiserror`, Tokio, tracing, URL, `wildmatch`, metrics, and `quick-xml` with serialization/encoding features. Dev dependencies support Tokio tests, tracing subscriber, Axum examples, serde_json, time, and Criterion.

Risks: quick-xml compatibility is explicitly called out for custom S3 filter deserialization, so upgrading it may affect AWS XML compatibility. `tokio` is built with multi-thread runtime features. Disabling doctests means public examples in docs are not validated through `cargo test --doc`.

Test signals: `[[bench]] snapshot_mode_scan` is registered. Dev dependencies indicate async unit tests and webhook examples are expected to compile in test/example builds.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/benches/snapshot_mode_scan.rs -->
# sources/object-store/rustfs/crates/notify/benches/snapshot_mode_scan.rs

Purpose: Criterion benchmark comparing `starshard::AsyncShardedHashMap` snapshot modes when scanning notification rule maps for a target ID.

Important APIs/types/functions: `build_rule_map` creates a `RulesMap` with an ObjectCreatedPut wildcard rule for one `TargetID`. `build_map` creates an async sharded map with selected `SnapshotMode` and fills `bucket-{i}` entries. `scan_target_bound` iterates a snapshot and returns true if any rules map contains the target. `bench_snapshot_mode_scan` runs Clone vs Cached modes for 1,000 and 10,000 buckets.

Control flow: a Tokio runtime is created inside the benchmark. For each size/mode pair, setup builds the map once, then Criterion repeatedly scans for a missing target to force a full traversal. Throughput is recorded as bucket elements.

State and persistence: in-memory benchmark data only; no external state. The map uses `FxBuildHasher`, `DEFAULT_SHARDS`, and the selected snapshot caching strategy.

Dependencies/integration: imports `rustfs_notify::rules::RulesMap`, `rustfs_targets::arn::TargetID`, `rustfs_s3_types::EventName`, `starshard`, Tokio runtime, and Criterion. It benchmarks a core rule-engine access pattern: target-bound full-map scans.

Risks: uses a missing target only, so it measures worst-case scan but not early-hit behavior. Runtime creation and `block_on` inside iterations add async overhead. Benchmark does not vary rule complexity per bucket.

Test signals: not a unit test; run with `cargo bench -p rustfs-notify --bench snapshot_mode_scan`. It provides performance regression signals for snapshot mode changes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/benches/snapshot_mode_scan.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/base.rs -->
# sources/object-store/rustfs/crates/notify/examples/base.rs

Purpose: shared logging helper for notify examples.

Important APIs/types/functions: `init_logger(LogLevel)` initializes a tracing subscriber with an `EnvFilter` directive and a formatted layer including target, thread names/IDs, file, and line number. `LogLevel` enum maps Debug/Info/Warn/Error to tracing filter directives.

Control flow: `main` simply initializes Info logging and logs a confirmation, but is marked dead-code because examples import the helper as a module. `init_logger` detects whether stdout is a terminal to enable ANSI coloring.

State and persistence: initializes global tracing subscriber process state once. No file persistence.

Dependencies/integration: uses `tracing_subscriber` registry/layers and `std::io::IsTerminal`. `full_demo.rs` and `full_demo_one.rs` import `init_logger` and `LogLevel`.

Risks: `.init()` panics if another global subscriber was already installed; examples are binaries so that is usually acceptable. There is a duplicated `.with_target(true)` call. `parse().unwrap()` is safe for hard-coded directives but would not be safe for arbitrary user input.

Test signals: no tests; behavior is validated by compiling/running notify examples.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/base.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/full_demo.rs -->
# sources/object-store/rustfs/crates/notify/examples/full_demo.rs

Purpose: end-to-end notification demo that initializes the global notification system, configures webhook/MQTT-style targets, removes a target, loads bucket rules, and sends a test event.

Important APIs/types/functions: uses `initialize`, `notification_system`, `Config`, `KV`, `KVS`, notify subsystem constants, `BucketNotificationConfig`, `Event::new_test_event`, `TargetID`, and `EventName::ObjectCreatedPut`.

Control flow: initializes logging, obtains or creates the global notification system, constructs webhook KVS and an MQTT KVS, writes config into `system.config`, calls `system.init`, checks active targets, removes the MQTT target, builds bucket notification config with webhook and MQTT rules, loads it for `my-bucket`, sends an event, then waits for delivery/logging.

State and persistence: mutates in-memory global notification system config and target/rule state. Queue directories point under a project-root-relative deploy/logs path, so real target backends may persist queued events there.

Dependencies/integration: integrates rustfs-config target settings, rustfs-notify global system APIs, rustfs-utils project-root discovery, S3 event names, target ARNs, Tokio, and tracing.

Risks: contains assertions about active target count that may be stale because MQTT insertion is commented while the log text says webhook and MQTT. It assumes a local webhook server at `127.0.0.1:3020` and optional MQTT environment. Hard-coded credentials and paths make it demo-only.

Test signals: not a test, but executable as an example. It exercises target removal and missing-target behavior during event dispatch.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/full_demo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/full_demo_one.rs -->
# sources/object-store/rustfs/crates/notify/examples/full_demo_one.rs

Purpose: dynamic notification configuration demo focused on adding and removing targets while the notification system is running.

Important APIs/types/functions: same core APIs as `full_demo.rs`, plus `set_target_config`, `remove_target_config`, and `remove_bucket_notification_config`.

Control flow: initializes or retrieves the global notification system, configures and initializes a webhook target, sleeps, dynamically adds an MQTT target via `set_target_config`, creates bucket rules for webhook and MQTT targets, sends an ObjectCreatedPut test event, removes the webhook target config, removes bucket notification config, and exits after a short delay.

State and persistence: mutates global notification config, active targets, bucket rule state, and queue directories under deploy/logs. Event payloads are in-memory unless target queues persist them.

Dependencies/integration: ties together config subsystem constants, notification system runtime APIs, target IDs, S3 event names, Tokio sleeps, and tracing logs. It expects a local webhook endpoint and MQTT broker to be useful beyond compilation.

Risks: `remove_target_config("notify_webhook", "1")` hard-codes strings instead of using imported constants/default target, which may drift. External services and paths are assumed. Credentials are example values.

Test signals: not a unit test; it is an integration-style example for manual or CI example compilation. It gives coverage of dynamic add/remove flows absent from `bucket_config_manager` unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/full_demo_one.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/webhook.rs -->
# sources/object-store/rustfs/crates/notify/examples/webhook.rs

Purpose: local Axum webhook receiver used by notify demos to inspect delivered event payloads and reset a receive counter.

Important APIs/types/functions: routes `POST /webhook` and `GET /webhook` to `receive_webhook`, `GET /webhook/reset` to query/header-aware reset, and `GET /webhook/reset/{reason}` to path reset. `WEBHOOK_COUNT` is a global `AtomicU64`. `is_service_active` performs a TCP self-check. `convert_seconds_to_date` manually converts Unix seconds for display.

Control flow: parses/binds address `:3020`, starts Axum server, spawns a delayed health check, and shuts down on Ctrl-C. Receive handler prints approximate current time and pretty JSON payload, increments count, and returns 200. Reset handlers print count/reason/headers and reset the atomic.

State and persistence: all state is process-local atomic count and stdout logs. No disk persistence.

Dependencies/integration: uses Axum, Tokio, serde/serde_json, `rustfs_utils::parse_and_resolve_address`, chrono for reset logging, and standard atomics/time.

Risks: `convert_seconds_to_date` ignores leap years and is only approximate; chrono is already available and should be preferred for correctness. `GET /webhook` is registered with a JSON extractor, so ordinary browser GETs without JSON may fail. Server binds a fixed port.

Test signals: no tests. Manual signal is receiving events from `full_demo`/`full_demo_one`; health check only validates TCP accept, not route behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/examples/webhook.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/bucket_config_manager.rs -->
# sources/object-store/rustfs/crates/notify/src/bucket_config_manager.rs

Purpose: coordinates bucket-level notification configuration across target availability, subscriber snapshots, and rule-engine state.

Important APIs/types/functions: `NotifyBucketConfigManager` owns `Arc<EventNotifier>`, `NotifyRuleEngine`, and `Arc<NotificationSystemSubscriberView>`. `new` constructs it. `has_subscriber(bucket, event)` checks the fast subscriber view first, then confirms the rule engine. `load_bucket_notification_config(bucket, cfg)` validates targets and loads rules. `remove_bucket_notification_config(bucket)` clears subscriber and rule-engine state.

Control flow: load obtains available ARNs for the config region from the notifier. If none exist, it returns `NotificationError::Configuration(notify_configuration_hint())`. It logs validation details, calls `cfg.validate`, rejects most parse/config errors as `BucketNotification`, but treats `ParseConfigError::ArnNotFound` as a warning so configs referencing temporarily missing targets can still load. It then applies the config to the subscriber view and sets the bucket rules in the async rule engine.

State and persistence: no disk persistence. It mutates in-memory subscriber snapshot and sharded/async rule-engine state. Logging emits structured notify bucket-config events.

Dependencies/integration: depends on `BucketNotificationConfig`, `EventNotifier`, `NotifyRuleEngine`, `NotificationSystemSubscriberView`, `NotificationError`, `ParseConfigError`, `EventName`, `Arc`, and tracing. It is the bridge between S3 bucket notification XML/config parsing and event dispatch lookup.

Risks: missing ARN tolerance can allow rules for unavailable targets; dispatch must handle missing targets later. `has_subscriber` can return false if subscriber view and rule engine drift, so both updates must remain paired. Region-specific ARN list governs validation.

Test signals: Tokio tests verify empty state reports no subscriber and `remove_bucket_notification_config` clears a previously applied subscriber snapshot. Tests do not cover successful load validation, missing ARN warning behavior, or rule-engine confirmation after load.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/notify/src/bucket_config_manager.rs -->
