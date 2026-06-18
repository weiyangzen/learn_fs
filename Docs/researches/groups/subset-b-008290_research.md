# subset-b-008290 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/check.rs -->
# sources/object-store/rustfs/crates/targets/src/check.rs

## Purpose
Connectivity and preflight probe module for RustFS notification/audit targets. It exposes async checks for MQTT, NATS, Pulsar, MySQL, PostgreSQL, Kafka, Redis, and AMQP so admin validation and runtime initialization can confirm a target backend is reachable before or while enabling delivery.

## Important APIs, types, and functions
- `check_mqtt_broker_available` and `check_mqtt_broker_available_with_tls` parse a broker URL, build `rumqttc` options through the MQTT target helper, subscribe to a topic, and wait for an event-loop poll.
- `check_nats_server_available`, `check_pulsar_broker_available`, `check_redis_server_available`, and `check_amqp_broker_available` delegate to target-specific connection builders, then run lightweight liveness calls such as NATS `flush`, Pulsar topic lookup, Redis ping, or AMQP connection/channel status.
- `check_mysql_server_available` validates `MySqlArgs`, parses DSN details, builds a `mysql_async` pool with optional TLS material, and runs `SELECT 1`.
- `check_postgres_server_available` validates `PostgresArgs`, builds a pool, executes `SELECT 1`, and verifies table readability with `LIMIT 0`.
- `check_kafka_broker_available` validates `KafkaArgs`, maps acks to `RequiredAcks`, applies optional security config, and creates an async producer.

## Control flow
Every check performs local validation before network I/O when the target args support it. The network phase is bounded by `tokio::time::timeout` values of 3, 5, or 8 seconds depending on backend. Errors are mapped into `TargetError` variants: malformed configuration stays `Configuration`, unreachable brokers often become `Network` or `NotConnected`, and hung handshakes become `Timeout`.

## State and persistence behavior
The module does not persist application data. It opens short-lived client connections and deliberately avoids side-effecting operations beyond read-only probes and broker handshakes. MySQL intentionally relies on pool drop instead of `pool.disconnect()` because tests documented that disconnect can hang past the probe timeout.

## Dependencies and integration points
This file integrates the public target validation surface with backend crates: `rumqttc`, `async_nats`, Pulsar helpers, `mysql_async`, PostgreSQL pool helpers, `rustfs_kafka_async`, Redis helpers, and AMQP helpers. The functions are re-exported from `lib.rs` for callers outside the crate.

## Risks and edge cases
The checks can produce false negatives in slow DNS/TLS environments because timeouts are short and fixed. Kafka only validates producer creation, not topic existence. MQTT only waits for one event after subscribe, so broker-specific auth or ACL behavior can affect the signal. MySQL and PostgreSQL TLS paths are passed through backend-specific builders, so path validation must remain aligned with `target_args.rs` and the target modules.

## Test signals
Unit tests assert that Kafka SASL without TLS, invalid MySQL table identifiers, and unpaired MySQL TLS client fields fail before opening network connections. These tests focus on fast local validation and guard against accidental probe behavior that reaches the network for invalid configs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/common.rs -->
# sources/object-store/rustfs/crates/targets/src/config/common.rs

## Purpose
Shared configuration helpers for target config loading and validation. The module centralizes environment variable field parsing, enable-state parsing, URL parsing, and backend-specific validation that is reused by argument builders.

## Important APIs, types, and functions
- `split_env_field_and_instance` maps an environment-variable suffix to `(field, instance_id)`, including fields that themselves contain underscores.
- `is_target_enabled` reads `enable` from a `KVS` and interprets `EnableState` aliases.
- `parse_target_bool` accepts RustFS enable-state strings and native boolean strings, returning `None` for missing or blank input.
- `validate_nats_server_config` rejects embedded credentials, conflicting auth methods, relative credentials/TLS/queue paths, and unpaired TLS cert/key fields.
- `validate_pulsar_broker_config` validates broker URL, topic presence, mutually exclusive auth styles, TLS option/scheme consistency, and queue directory absoluteness.
- `parse_url` wraps `url::Url::parse` and produces `TargetError::Configuration` with field context.

## Control flow
The env-field splitter normalizes the suffix to lowercase, first checks for a default-instance field match, then finds the longest valid field prefix followed by the default delimiter. NATS and Pulsar validation are fail-fast sequences that read optional keys from `KVS` and return a concrete configuration error at the first incompatible combination.

## State and persistence behavior
No state is persisted. The helpers only read `KVS` values and path strings. They enforce that path-like configuration points to absolute paths before any target runtime writes queue files or loads credentials.

## Dependencies and integration points
The module depends on `rustfs_config` constants and `KVS`, `async_nats::ServerAddr`, Pulsar broker validation from the target module, `url::Url`, and `TargetError`. It is used by `loader.rs` for env parsing and by `target_args.rs` for backend argument validation.

## Risks and edge cases
The longest-prefix logic is important for field names with internal underscores; adding new fields whose names prefix other fields can change parsing unless covered by tests. Boolean parsing is permissive, so callers that need strict `true`/`false` semantics must not assume it. NATS and Pulsar validation use default queue dirs supplied by callers, so an invalid relative default can fail otherwise valid configs.

## Test signals
Tests cover conflicting NATS auth methods, relative NATS queue dirs, and Pulsar TLS flags on non-TLS broker schemes. These are high-value checks because they prevent ambiguous credentials and unsafe TLS settings from reaching runtime connection code.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/instance.rs -->
# sources/object-store/rustfs/crates/targets/src/config/instance.rs

## Purpose
Canonical normalization layer for target plugin instances. It turns legacy file/env target configuration into `TargetPluginInstanceRecord` values that carry domain, plugin identity, instance id, enablement, source provenance hints, and effective merged config.

## Important APIs, types, and functions
- `TargetPluginInstanceCompatDescriptor` describes one legacy target family: domain, plugin id, target type, config subsystem, route prefix, and valid fields.
- `TargetInstanceSourceHints` records whether default and instance config came from files or environment, and classifies records as `Config`, `Env`, or `Mixed`.
- `TargetPluginInstanceRecord` is the normalized instance model consumed by compatibility/admin surfaces.
- `normalize_target_plugin_instances_from_env` delegates merging to `collect_merged_target_configs_from_env`, then enriches each merged record with descriptor metadata.
- `normalize_legacy_target_instances*` are compatibility aliases around the canonical normalization functions.

## Control flow
The function builds a valid-field set from the descriptor, collects merged configs for the descriptor subsystem and route prefix, then maps every merged record into a plugin instance record. Disabled instances are preserved in this layer, unlike `collect_target_configs`, so admin surfaces can report disabled definitions.

## State and persistence behavior
The module is read-only. It materializes effective configs from in-memory `Config` plus environment variables and preserves source hints that explain whether the materialized value came from file defaults, file instance entries, env defaults, or env instance entries.

## Dependencies and integration points
It bridges `rustfs_config::server_config::Config/KVS`, `TargetDomain`, builtin manifests, and `loader.rs`. Higher-level control/admin code can use records to present plugin instances without knowing legacy subsystem naming rules.

## Risks and edge cases
Default-only entries are intentionally excluded by the loader, so a globally enabled default target does not create an instance without file or env instance material. Environment-only instances need an explicit instance `enable` flag to be discovered. Mixed-source classification can surprise callers because a default from one source plus an instance from another source produces `Mixed`.

## Test signals
Tests verify notify and audit webhook normalization, domain/subsystem preservation, disabled instance retention, default-only exclusion, mixed source hints, and compatibility wrapper equivalence.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/instance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/loader.rs -->
# sources/object-store/rustfs/crates/targets/src/config/loader.rs

## Purpose
Target config collection and merge engine. It reads RustFS config-file sections and `RUSTFS_*` environment variables, applies default and instance overrides, redacts sensitive values for debug logging, and emits enabled target configs for runtime creation.

## Important APIs, types, and functions
- `collect_target_configs` and `collect_target_configs_from_env` return enabled `(instance_id, KVS)` pairs for a target type.
- `collect_env_target_instance_ids*` discovers explicit env instance ids without materializing configs.
- `collect_merged_target_configs_from_env` is the core merger and returns `MergedTargetConfigRecord` with effective config plus source flags.
- `is_sensitive_target_field`, `redact_target_field_value`, and `redacted_target_config` protect passwords, tokens, credentials, private keys, and DSNs in debug logs.

## Control flow
The loader filters env vars to the RustFS prefix, reads file configs from a section such as `notify_webhook`, extracts file default `_`, then parses env keys using the route prefix, target type, and valid-field set. Env default overrides extend file defaults. The instance list starts from file instance ids and adds env instance ids only when their env config contains `enable`. For each instance, effective config is file/env default, then file instance, then env instance; finally enabled state is derived from the merged result.

## State and persistence behavior
No persistence occurs. Effective `KVS` values are cloned and merged in memory. The loader deliberately preserves redacted debug observability without mutating the real config values passed to target builders.

## Dependencies and integration points
It depends on `rustfs_config` naming constants, `KVS`/`Config`, tracing, and `common.rs` helpers. `plugin.rs` uses `collect_target_configs` to create registered targets from server config; `instance.rs` uses the crate-private merged-record function to keep disabled/admin-visible records.

## Risks and edge cases
Only env-only instances with an explicit instance `enable` key are discovered, so setting only `endpoint_INSTANCE` is ignored even if the default is enabled. Field parsing is strict against the valid-field list and logs ignored fields. Redaction must track new secret-bearing field names; otherwise debug logs could expose credentials.

## Test signals
Tests cover env defaults applying to file targets, env instance discovery with `enable`, env-only instances without `enable` being skipped, fields with internal underscores, Redis field parsing, sensitive-value redaction, partial MySQL/Postgres DSN redaction, and redacted config shape preservation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/loader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/mod.rs -->
# sources/object-store/rustfs/crates/targets/src/config/mod.rs

## Purpose
Public facade for the target configuration subsystem. It keeps implementation modules private where possible and re-exports the normalization, loader, builder, and validator APIs used by the rest of `rustfs_targets`.

## Important APIs, types, and functions
- Private modules: `common`, `instance`, `loader`, and `target_args`.
- Re-exports instance descriptors and records such as `TargetPluginInstanceRecord`, source-hint types, and legacy compatibility aliases.
- Re-exports loader functions including `collect_target_configs*` and `collect_env_target_instance_ids*`.
- Re-exports per-target builders and validators for AMQP, Kafka, MQTT, MySQL, NATS, PostgreSQL, Pulsar, Redis, and Webhook.

## Control flow
There is no runtime control flow beyond Rust module resolution. The file defines the crate-level import surface and intentionally hides shared helper details in private modules.

## State and persistence behavior
No state is stored. This module only controls API visibility.

## Dependencies and integration points
`lib.rs`, `plugin.rs`, admin handlers, and target initialization code import through this facade. Because it re-exports legacy and canonical names, it is also a compatibility boundary for callers that still use older target-instance terminology.

## Risks and edge cases
Accidental removal or renaming of re-exports is a breaking crate API change. Keeping `common` private means any validation helper needed outside the config subsystem must be intentionally promoted through this file or another public API.

## Test signals
No direct tests live in this file. Coverage comes from the re-exported modules' unit tests and downstream compilation of modules that import through `crate::config`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/target_args.rs -->
# sources/object-store/rustfs/crates/targets/src/config/target_args.rs

## Purpose
Transforms merged `KVS` configuration into strongly typed target argument structs and validates backend-specific configuration rules. It is the main compatibility layer between RustFS legacy config keys and runtime target constructors.

## Important APIs, types, and functions
- Builders: `build_amqp_args`, `build_webhook_args`, `build_mqtt_args`, `build_nats_args`, `build_pulsar_args`, `build_redis_args`, `build_postgres_args`, `build_kafka_args`, and `build_mysql_args`.
- Validators: `validate_*_config` wrappers either build and discard args or run stricter preflight checks.
- Internal parsers include `parse_kafka_acks_value`, `parse_kafka_sasl_enable`, and `parse_amqp_bool_value`.
- Backend args include target type so the same builder path can support notify and audit domains where target implementations allow both.

## Control flow
Each builder reads required keys, applies defaults for optional keys, parses URLs or DSNs, maps booleans/durations/limits, constructs the backend args struct, and usually calls its `validate()` method. Validators are thin wrappers except where extra rules are needed, such as webhook client cert/key pairing and queue-dir absoluteness or MQTT QoS/queue compatibility.

## State and persistence behavior
The module does not persist state. It decides queue directories and queue limits that downstream targets use for durable delivery stores. It enforces absolute queue/TLS path rules before those downstream components open files.

## Dependencies and integration points
It depends heavily on `rustfs_config` key constants, target modules for argument structs and validators, `rumqttc::QoS`, URL parsing from `common.rs`, and `TargetError`. `plugin.rs` descriptors use these validators and builders when registered target plugins are created from config.

## Risks and edge cases
Some numeric options silently fall back when parsing fails, while others, such as MySQL `max_open_connections`, return errors; callers need to know which fields are strict. Kafka infers SASL enablement from credentials unless explicitly disabled, which is convenient but subtle. MQTT build maps invalid QoS values to `AtLeastOnce`, while validation rejects invalid QoS, so callers should validate before relying on built args.

## Test signals
The large unit suite covers AMQP schemes, booleans, credentials, TLS path pairing, Kafka acks/SASL/TLS interactions, MySQL DSN/table/TLS/queue/max-connection validation, Redis defaults and tuning fields, and PostgreSQL DSN/table/format/TLS/queue rules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/config/target_args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/control_plane.rs -->
# sources/object-store/rustfs/crates/targets/src/control_plane.rs

## Purpose
Declarative control-plane model for target plugin installation, enablement, runtime status, and external plugin action planning. It does not execute installs or sidecars; it validates whether an action should be allowed and returns the resulting desired state.

## Important APIs, types, and functions
- State enums: `TargetPluginInstallState`, `TargetPluginEnableState`, `TargetPluginRuntimeState`, and `TargetPluginExternalAction`.
- State records: `TargetPluginRevision`, `TargetPluginInstallation`, `TargetPluginOperationalState`, and `TargetPluginExternalActionDecision`.
- Constructors: `builtin_target_plugin_installation`, `external_target_plugin_installation`, `failed_external_target_plugin_installation`, `rollback_target_plugin_installation`, and `builtin_target_plugin_operational_state`.
- Gates and policies: `TargetPluginExternalFlowGate`, `TargetPluginExternalFlowGateStatus`, and `TargetPluginInstallPolicy`.
- Action planner: `plan_external_target_plugin_action`; install validator: `validate_external_plugin_installation`.

## Control flow
`plan_external_target_plugin_action` first rejects non-external manifests and closed/disabled gates. It then routes by action: install validates provider, protocol, distribution metadata, artifact URL host/scheme, digest, signature, and provenance; enable and disable require an installed revision; rollback additionally requires a previous revision. Decisions return cloned or newly constructed state but perform no I/O.

## State and persistence behavior
All state is serializable in-memory metadata. Builtin plugins are represented as virtually installed revisions with source `builtin`; external plugins carry digest, artifact id, install time, and previous revision for rollback. Persistence of these records would be a caller responsibility.

## Dependencies and integration points
The file ties manifests to sidecar runtime policy. It uses marketplace manifest fields from `manifest.rs`, sidecar policy and safety checks from `runtime/sidecar.rs`, protocol version from `sidecar_protocol`, `url::Url` for artifact validation, and serde for admin/control-plane serialization.

## Risks and edge cases
Default external flow is disabled and requires a closed circuit breaker, sandbox, provenance, and allowed artifact host. The allowlist currently defaults to `plugins.example.test`, making it more of a scaffold than a production policy. Digest validation only checks hex shape and minimum length, not an actual downloaded artifact. Runtime state results are planned labels, not evidence from a running process.

## Test signals
Tests verify builtin revision modeling, operational state mapping, runtime label mapping, external revision and rollback metadata, failed install records, disabled default gates, builtin-manifest rejection, signature/provenance requirements, sandbox and circuit-breaker enforcement, action planning for install/disable/rollback, and allowed/disallowed install policy cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/control_plane.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/domain.rs -->
# sources/object-store/rustfs/crates/targets/src/domain.rs

## Purpose
Small domain mapping module that names the two logical target plugin domains RustFS supports: notification targets and audit targets.

## Important APIs, types, and functions
- `TargetDomain::{Notify, Audit}` serializes with snake_case names.
- `runtime_target_type` maps domains to `TargetType::NotifyEvent` or `TargetType::AuditLog`.
- `impl From<TargetType> for TargetDomain` maps runtime target types back into domain values.

## Control flow
The conversion logic is a pair of total `match` expressions over the currently known target types.

## State and persistence behavior
No state is persisted. The enum is serde-compatible and can appear in manifests, handshakes, and admin records.

## Dependencies and integration points
It depends on `crate::target::TargetType` and is used by manifests, instance descriptors, sidecar handshakes, and control-plane policy checks.

## Risks and edge cases
The `From<TargetType>` implementation assumes every `TargetType` belongs to one of these domains. If more target types are added, this conversion must be updated or compilation will fail.

## Test signals
There are no direct tests. Coverage is indirect through sidecar, manifest, and instance-normalization tests that compare expected domains.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/domain.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/error.rs -->
# sources/object-store/rustfs/crates/targets/src/error.rs

## Purpose
Defines shared error enums for target storage and delivery/runtime operations.

## Important APIs, types, and functions
- `StoreError` covers queue-store I/O, serialization, deserialization, compression, limits, missing entries, and internal invalid entries.
- `TargetError` covers storage, network, request, timeout, authentication, configuration, encoding, serialization, connection state, initialization, invalid ARN, disabled targets, dropped queued payloads, parse failures, save-config failures, and uninitialized server state.
- `impl From<url::ParseError> for TargetError` maps URL parse failures to configuration errors.

## Control flow
The file has no branching behavior beyond the URL parse error conversion. Error display strings are supplied through `thiserror`.

## State and persistence behavior
No state is stored. These error variants are used to classify state transitions elsewhere, especially replay behavior where `Timeout` and `NotConnected` are retryable, `Dropped` is terminal, and other errors are permanent.

## Dependencies and integration points
It depends on `std::io`, `thiserror`, and `url`. The enums are re-exported by `lib.rs` and used across target implementations, queue stores, config validation, connectivity checks, runtime replay, and plugin registry code.

## Risks and edge cases
Many variants carry strings instead of structured fields, so callers often inspect the variant but cannot reliably parse causes. Adding variants can require replay and admin mapping updates. `TargetError::Configuration` is used broadly for both parse failures and policy failures.

## Test signals
No direct tests are present. Variant behavior is exercised throughout config, connectivity, runtime, and target module tests via pattern matching and display-string assertions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/lib.rs -->
# sources/object-store/rustfs/crates/targets/src/lib.rs

## Purpose
Crate root and public API surface for `rustfs_targets`. It wires submodules together, re-exports target/plugin/runtime/config APIs, and defines the generic `TargetLog` event container.

## Important APIs, types, and functions
- Declares modules for ARN, catalog, config, control plane, domain, errors, manifest, networking, plugin registry, runtime, store, system user-agent helpers, and target implementations.
- Re-exports extension schema builders, connectivity checks, config normalization/builders, control-plane planning APIs, manifests, plugin descriptors/registry, runtime manager/adapters/registries/sidecars, `EventName`, user-agent helpers, `Target`, and `TargetDeliverySnapshot`.
- `TargetLog<E>` serializes as PascalCase and contains `event_name`, `key`, and `records`.

## Control flow
There is no runtime control flow. The file defines what downstream crates can import from `rustfs_targets` without depending on internal module paths.

## State and persistence behavior
No persistent state is owned here. `TargetLog` is a serializable payload model that downstream targets can store or send.

## Dependencies and integration points
The root integrates internal modules and external crates `rustfs_s3_types` and `serde`. It is the compatibility boundary for admin, server, and target code that imports this crate.

## Risks and edge cases
Because it re-exports many internal symbols, changes here are API-significant. Private modules such as `check` and `net` still expose selected symbols through re-exports, so accidental omission can break callers even if the underlying code remains intact.

## Test signals
No direct tests live in this file. Compilation of downstream modules and tests is the primary signal that the re-export surface remains coherent.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/manifest.rs -->
# sources/object-store/rustfs/crates/targets/src/manifest.rs

## Purpose
Defines declarative manifest metadata for builtin and future installable target plugins, including supported domains, secret fields, packaging, entrypoint style, runtime transport, and distribution artifacts.

## Important APIs, types, and functions
- Core structs: `TargetPluginManifest`, `TargetPluginMarketplaceManifest`, `TargetPluginExternalRuntimeContract`, `TargetPluginArtifactManifest`, and `TargetPluginDistributionManifest`.
- Enums: `TargetPluginPackaging`, `TargetPluginEntrypointKind`, and `TargetPluginRuntimeTransport`.
- Constructors: `builtin_target_manifest`, `builtin_target_marketplace_manifest`, and `installable_target_marketplace_manifest`.
- `impl From<TargetPluginManifest> for TargetPluginMarketplaceManifest` turns builtins into marketplace records with builtin packaging and in-process runtime transport.

## Control flow
`builtin_target_manifest` matches target type strings to display names, builtin plugin ids, and secret-field lists. Marketplace conversion fills stable API/runtime compatibility versions and uses `None` distribution for builtins. Installable manifests preserve base metadata but mark packaging external and attach a supplied runtime contract and distribution.

## State and persistence behavior
The module stores only static metadata. Secret-field arrays identify config keys that admin/UI layers should treat as sensitive; they do not themselves redact or persist values.

## Dependencies and integration points
It depends on `TargetDomain` and many `rustfs_config` field constants. Control-plane validation consumes marketplace manifests. Instance normalization and plugin descriptors use builtin plugin ids to identify target types consistently.

## Risks and edge cases
Unknown target types become `custom:target` with no secret fields, which could under-classify sensitive custom config if used beyond placeholder scenarios. Secret field lists must be updated whenever new credential-like keys are added. Builtin API compatibility strings are hard-coded constants and should be versioned deliberately.

## Test signals
Tests verify secret fields for webhook and Kafka, marketplace metadata derived from builtins, supported-domain preservation, stable builtin conversion, and an installable sidecar manifest carrying distribution metadata.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/manifest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/net.rs -->
# sources/object-store/rustfs/crates/targets/src/net.rs

## Purpose
Network and HTTP metadata helper module. It extracts request/response headers for target payloads, parses and validates hosts/URLs, normalizes URL display, and classifies common network errors.

## Important APIs, types, and functions
- `NetError` classifies invalid hosts, missing IPv6 brackets, parse failures, unexpected schemes, and URLs with schemes but empty hosts.
- `Host` represents a host name/IP plus optional port and implements display/equality helpers.
- Header helpers extract all headers, host, port, content length, referer, and user-agent from `hyper::HeaderMap` or S3 request/response types.
- `parse_host`, `trim_ipv6`, `ParsedURL`, `parse_url`, and `parse_http_url` validate host names/IPs, handle IPv6 zone IDs, infer default ports, clean paths, and normalize default ports on display.
- `is_network_or_host_down`, `is_conn_reset_err`, and `is_conn_refused_err` classify `std::io::Error` values.

## Control flow
Header extraction iterates header maps and skips non-UTF-8 values. Port detection prioritizes `x-forwarded-port`, explicit host port, forwarded-proto defaults, then a `port` header. Host parsing splits bracketed IPv6, bare IPv6, and host:port forms, validates labels with a regex, and supports zone suffixes for IP validation. URL parsing rejects `scheme:///path`, validates host/port through `parse_host`, and normalizes path components.

## State and persistence behavior
No persistent state exists. `HOST_LABEL_REGEX` is lazily initialized once through `LazyLock`.

## Dependencies and integration points
It depends on `hyper`, `s3s`, `url`, `regex`, `serde`, `libc`, and `hashbrown`. Config builders and connectivity checks use `parse_url`; target delivery code can use header extraction to build event metadata.

## Risks and edge cases
`get_request_port` treats host port `0` as absent and may infer forwarded-proto defaults instead. Path cleaning removes `..` and non-normal path components, which is useful for canonicalization but can change user-supplied URL text. Header extraction drops binary or invalid header values.

## Test signals
Tests cover port priority and IPv6 handling, host parse success/failure for IPv4, hostnames, bracketed and bare IPv6, zone IDs, invalid brackets, invalid host labels, URL default-port normalization, empty-host rejection, invalid-host rejection, and path normalization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/net.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/plugin.rs -->
# sources/object-store/rustfs/crates/targets/src/plugin.rs

## Purpose
Plugin registry and descriptor layer for constructing target instances from configuration. It packages create/validate callbacks with manifest metadata and provides runtime activation through a `PluginRuntimeAdapter`.

## Important APIs, types, and functions
- `TargetRequestValidator` enumerates admin validation modes for builtin target families.
- `TargetAdminMetadata` and `BuiltinTargetAdminDescriptor` expose subsystem, valid fields, manifest, and validation metadata for admin/control-plane use.
- `TargetPluginDescriptor<E>` owns manifest, target type, valid fields, a config validator closure, and a target factory closure.
- `BuiltinTargetDescriptor<E>` couples plugin descriptors to admin metadata.
- `TargetPluginRegistry<E>` registers descriptors, creates targets, creates all enabled targets from config, and creates runtime activations via an adapter.
- `boxed_target` erases concrete targets into boxed trait objects.

## Control flow
Descriptors validate config before invoking their create callback. Registry config creation iterates registered target types, collects enabled merged configs for each type using `collect_target_configs`, attempts target creation per instance, logs failures, and continues building the rest. `create_activation_from_config` delegates successful targets to a runtime adapter, which may start replay workers.

## State and persistence behavior
Registry state is an in-memory map from target type to descriptor. It does not persist configs or targets. Created targets may own durable queue stores, but that state belongs to target implementations and runtime activation.

## Dependencies and integration points
The module integrates config loading, target trait objects, manifests, runtime adapters, serde bounds for event payloads, and tracing. It is the central connection between legacy config sections and runtime target management.

## Risks and edge cases
Duplicate registration replaces the prior descriptor for a target type. `create_targets_from_config` logs per-target creation errors and returns `Ok` with partial success, so callers must inspect resulting activation if they need all-or-nothing semantics. Registry iteration order comes from `hashbrown::HashMap`, so creation order is not stable.

## Test signals
The unit test registers a synthetic target, materializes one enabled config instance, activates through `BuiltinPluginRuntimeAdapter`, and asserts the expected `primary:test` target appears without replay workers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/plugin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/adapter.rs -->
# sources/object-store/rustfs/crates/targets/src/runtime/adapter.rs

## Purpose
Defines the runtime adapter abstraction for target plugins and implements the builtin in-process adapter. The adapter isolates activation, replay-worker management, runtime replacement, snapshots, health checks, and shutdown behind a stable trait.

## Important APIs, types, and functions
- `PluginRuntimeAdapter<E>` trait defines `activate_with_replay`, `replace_runtime_targets`, `stop_replay_workers`, `snapshot_runtime_status`, `snapshot_runtime_health`, and `shutdown`.
- `BuiltinPluginRuntimeAdapter<E>` stores replay hook, replay-start observer, optional replay semaphore, batch timeout, idle sleep, and stop log prefix.
- `BuiltinPluginRuntimeAdapter::new` configures those runtime parameters.

## Control flow
Activation wraps `activate_targets_with_replay` and, for each target, calls `init_target_and_optionally_start_replay`. Store-backed enabled targets can start replay workers through `start_replay_worker`. Replacement stops old replay workers, closes existing runtime targets, adds activated targets, and swaps replay worker managers. Shutdown is the same stop-and-close sequence without adding replacements.

## State and persistence behavior
The adapter holds runtime policy/configuration in memory. It does not persist target state but controls replay workers that drain persistent target stores. Store-backed targets can remain active even when initialization fails so queued payloads can still be replayed.

## Dependencies and integration points
It depends on `runtime/mod.rs` primitives, `Target`, `TargetError`, async trait support, serde bounds, `tokio::sync::Semaphore`, and configured replay hooks supplied by callers. `plugin.rs` uses it through the trait when creating runtime activations from config.

## Risks and edge cases
Replacement stops and closes the old runtime before adding new activated targets, so partial activation decisions are already baked in. Failed target close operations are logged inside runtime manager cleanup and do not abort shutdown. Replay concurrency depends on the optional semaphore supplied by the caller.

## Test signals
Tests cover empty activation, non-store targets being skipped on init failure, store-backed targets being retained with a replay worker after init failure, and shutdown clearing runtime targets/replay workers while calling target close exactly once.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/mod.rs -->
# sources/object-store/rustfs/crates/targets/src/runtime/mod.rs

## Purpose
Core runtime lifecycle and replay machinery for instantiated targets. It manages active target references, runtime status/health snapshots, replay worker cancellation, target activation, and durable queue replay.

## Important APIs, types, and functions
- Public submodules: `adapter`, `ops_diagnostics`, `s3_hooks`, `sidecar`, `sidecar_protocol`, and `tls`.
- `SharedTarget<E>` is the shared `Arc<dyn Target<E>>` runtime object.
- `ReplayWorkerManager` stores cancel senders and can snapshot or stop all workers.
- Snapshot types: `RuntimeActivation`, `RuntimeStatusSnapshot`, `RuntimeTargetSnapshot`, `RuntimeTargetHealthState`, and `RuntimeTargetHealthSnapshot`.
- `ReplayEvent` reports delivered, retryable, dropped, permanent, exhausted, and unreadable replay outcomes.
- `TargetRuntimeManager` provides add/get/remove/close/list/snapshot/health methods.
- `init_target_and_optionally_start_replay`, `activate_targets_with_replay`, and `start_replay_worker` implement activation and queue replay.

## Control flow
Activation initializes each target. Init failure drops non-store targets but keeps store-backed targets so replay can still be attempted. Enabled store-backed targets get replay workers; disabled targets are kept without replay. Replay loops list store keys, confirm raw entries are readable, batch keys, and send them from store. `NotConnected` and `Timeout` retry with exponential backoff and jitter up to five attempts; `Dropped` and other errors produce terminal events.

## State and persistence behavior
Runtime manager state is an in-memory map keyed by `TargetID` string. Replay workers operate on target-provided durable stores and remove/retain entries according to target `send_from_store` behavior. The runtime itself only tracks cancellation channels, active target references, and delivery/health snapshots.

## Dependencies and integration points
It depends on target traits, target IDs, store traits and queue payloads, `TargetDeliverySnapshot`, `TargetError`, `StoreError`, serde bounds, `tokio` channels/semaphores, and tracing. `adapter.rs` wraps these primitives for plugin/runtime consumers.

## Risks and edge cases
Replay currently processes a batch whenever it has any key, making the batch timeout mostly relevant when keys are pending but no new store keys arrive. `1u32 << retry_count` is safe for the current small retry bound but would need care if retry counts grow. Store `list()` order and target send semantics determine replay ordering and deletion behavior. Cancel checks are cooperative, so a worker may finish a batch before stopping.

## Test signals
Tests verify `remove_and_close` removes a target and calls close once, and snapshots contain target id/type data. Adapter tests provide additional coverage for activation and replay-worker lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/ops_diagnostics.rs -->
# sources/object-store/rustfs/crates/targets/src/runtime/ops_diagnostics.rs

## Purpose
Registry for ops-diagnostics extensions. It validates extension schemas/contracts, records which diagnostic surfaces each extension serves, and authorizes read-only diagnostic access.

## Important APIs, types, and functions
- `OpsDiagnosticsRegistryError` reports invalid contracts, unsupported extension kinds, and missing required capability.
- `OpsDiagnosticsRegistration` records extension id and diagnostic surface.
- `OpsDiagnosticsRegistry` stores registrations by `OpsDiagnosticSurface`.
- `OpsDiagnosticsReadRequest` carries requested surface, capability, and admin authorization flag.
- `OpsDiagnosticsAccessDecision` returns allow or specific denial reasons.

## Control flow
`register_schema` rejects non-ops-diagnostics schemas, requires the ops diagnostics capability, validates the contract, then registers every declared surface. `authorize_read` denies unknown surfaces first, then missing admin authorization, then wrong capability, otherwise allowing read-only access.

## State and persistence behavior
Registrations are in-memory `BTreeMap` entries. The registry does not execute diagnostics or persist access decisions.

## Dependencies and integration points
It integrates with `rustfs_extension_schema` contracts, extension kinds, capabilities, and diagnostic surface enums. Builtin extension schema/contract constructors are re-exported from the crate root and used by tests.

## Risks and edge cases
Authorization is registry-local and assumes the caller has already performed any identity/authentication work that sets `admin_action_authorized`. Capability comparison is string-based. Registration allows multiple extensions per surface and does not deduplicate extension ids.

## Test signals
Tests verify default unknown-surface denial, successful builtin registration, read-only authorization, wrong capability denial, missing admin-action denial, rejection of non-diagnostics schemas, and rejection of contracts that mutate object data.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/ops_diagnostics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/s3_hooks.rs -->
# sources/object-store/rustfs/crates/targets/src/runtime/s3_hooks.rs

## Purpose
Registry scaffold for S3 post-auth hook extensions. It validates extension schemas and hook contracts, records hook registrations by hook point, and currently dispatches with an allow/continue decision only.

## Important APIs, types, and functions
- `S3HookRegistryError` reports invalid contracts, unsupported extension kinds, and missing hook capability.
- `S3HookRegistration` records extension id and hook point.
- `S3HookRegistry` stores registrations by `S3HookPoint`.
- `S3HookContext::post_auth` constructs context only when an authenticated principal is present.
- `S3HookDecision::Continue` is the current dispatch result.

## Control flow
`register_schema` rejects non-S3-hook schemas, requires the post-auth hook capability, validates the hook contract, and registers all declared hook points. `dispatch_post_auth` ignores current registrations and context and returns `Continue`, preserving existing request behavior while the registry contract is introduced.

## State and persistence behavior
State is an in-memory `BTreeMap` of hook registrations. No hook side effects, persistence, or request mutation occurs in this file.

## Dependencies and integration points
It depends on `rustfs_extension_schema` extension kinds, capabilities, hook points, and S3 hook contract validation. It is re-exported by `lib.rs` for S3 server/runtime integration.

## Risks and edge cases
Dispatch is a placeholder; registering hooks does not yet execute plugin code. `S3HookContext::post_auth` only rejects blank principals and does not validate bucket/object strings. Multiple hooks per hook point are accepted without ordering guarantees beyond `Vec` insertion order within a surface.

## Test signals
Tests verify empty registry behavior, blank-principal rejection, valid builtin hook registration with unchanged continue dispatch, rejection of non-hook schemas, and rejection of unsafe contracts such as IAM bypass.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/s3_hooks.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/sidecar.rs -->
# sources/object-store/rustfs/crates/targets/src/runtime/sidecar.rs

## Purpose
Policy and state model for external sidecar plugin runtimes. It validates activation safety checks, tracks sidecar health/failures, handles domain/handshake checks, and models degradation back to builtin behavior after repeated failures.

## Important APIs, types, and functions
- `SidecarRuntimePolicy` controls whether external sidecars are allowed, sandbox/provenance requirements, max queue depth, operation timeout, failure threshold, and error redaction.
- `SidecarRuntimeSafetyChecks` reports sandbox, provenance, and queue-depth evidence.
- `SidecarRuntimePolicyError` classifies activation denials.
- `SidecarPluginRuntime` stores endpoint, handshake, health, failure count, degraded flag, and last error.
- Methods include `enable`, `enable_with_policy`, `mark_unhealthy`, `record_failure`, `record_failure_with_policy`, `send_with_timeout`, and `shutdown`.

## Control flow
Enablement validates the sidecar handshake against an expected plugin id, checks required domain support, then optionally enforces runtime policy against safety checks. Failure recording increments counters, marks unhealthy, optionally redacts details, and sets `degraded_to_builtin` once the default or policy threshold is reached. Timeout simulation records a failure if latency exceeds the supplied operation budget.

## State and persistence behavior
All runtime state is in-memory and serde-compatible for status reporting. It does not manage an actual process or connection; endpoint and handshake data represent the sidecar boundary declaratively.

## Dependencies and integration points
It depends on `TargetDomain`, `SidecarHandshake`, serde, durations, and `thiserror`. `control_plane.rs` embeds `SidecarRuntimePolicy` and `SidecarRuntimeSafetyChecks` in external flow gates.

## Risks and edge cases
`record_failure` uses the module default threshold, while `record_failure_with_policy` uses policy threshold and redaction. `send_with_timeout` uses the non-policy failure path, so policy redaction does not apply there. Activation proves only declared safety checks, not OS-level sandboxing or provenance verification itself.

## Test signals
Tests cover successful enablement, default policy rejection, sandbox/provenance/queue-depth enforcement, verified external activation, redacted failure details and threshold degradation, domain mismatch rejection, shutdown health state, default threshold degradation, and timeout error recording.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/sidecar.rs -->
