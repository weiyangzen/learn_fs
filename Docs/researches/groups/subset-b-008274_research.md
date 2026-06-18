# subset-b-008274 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/mod.rs

Purpose: Provides the single entry point for RustFS telemetry initialization and the module boundary for observability backends. It decides between full OTLP export, local rolling-file logging, and stdout-only logging from an `OtelConfig`, then returns an `OtelGuard` that owns the provider/writer lifecycle.

Important APIs/types/functions: Re-exports `OtelGuard` and `Recorder`, exposes public `dial9`, and keeps `filter`, `guard`, `local`, `otel`, `recorder`, `resource`, and `rolling` private. `init_telemetry(config)` computes the effective environment and log level, detects whether any root or per-signal OTLP endpoint is configured, and delegates either to `otel::init_observability_http` or `local::init_local_logging`.

Control flow: `init_telemetry` first treats any non-empty OTLP endpoint (`endpoint`, `trace_endpoint`, `metric_endpoint`, or `log_endpoint`) as a request for the OTLP HTTP pipeline. If no OTLP endpoint exists, it checks `RUSTFS_OBS_LOG_DIRECTORY` dynamically and overlays it onto a cloned config so late environment changes still select file logging. Otherwise local logging chooses between file and stdout internally.

State/persistence behavior: This file does not persist telemetry data itself, but it controls which backend owns external state. Returning and retaining `OtelGuard` is mandatory because dropping it flushes and shuts down providers/writers. The only local mutation is constructing an effective config when the log-directory environment variable overrides the passed struct.

Dependencies/integration: Integrates `OtelConfig`, `TelemetryError`, RustFS config defaults (`DEFAULT_LOG_LEVEL`, `ENVIRONMENT`, production environment name, `ENV_OBS_LOG_DIRECTORY`), and `rustfs_utils::get_env_opt_str`. It is the integration seam callers should use instead of calling backend modules directly.

Risks/test signals: Endpoint detection treats any per-signal endpoint as full OTLP mode, so misconfigured single-signal settings can change logging/metrics behavior. The environment variable override is intentionally dynamic but can surprise code that expects the provided config to be authoritative. Unit tests cover production detection, stdout default logic, log-level mapping expectations, and environment field defaults; they do not instantiate real subscribers or exercise `init_telemetry` end to end.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/otel.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/otel.rs

Purpose: Builds the full OpenTelemetry HTTP observability pipeline for traces, metrics, logs, and optional profiling. It wires OTLP/HTTP exporters, OpenTelemetry SDK providers, the `tracing` subscriber stack, a `metrics` crate recorder, local log fallback, and stdout mirrors into one guarded initialization path.

Important APIs/types/functions: `init_observability_http` is the main entry point. Builder helpers include `build_tracer_provider`, `build_tracer_sampler`, `build_meter_provider`, `build_logger_provider`, `create_periodic_reader`, `resolve_signal_headers`, `parse_otlp_headers`, and `resolve_signal_timeout`. Feature-gated `init_profiler` and `init_memory_profiler` start Pyroscope CPU and jemalloc memory profiling agents when enabled and configured.

Control flow: The main function builds a common `Resource`, resolves service name, stdout behavior, sample ratio, and per-signal endpoints. Missing per-signal endpoints fall back to `endpoint + /v1/{traces,metrics,logs}` when a root endpoint is set. It then builds optional trace and metric providers based on endpoint presence and export-enable flags, starts profilers, and chooses log routing. If a log endpoint is usable, an OTLP log provider is bridged into `tracing`; if not and a log directory exists, it builds a `RollingAppender`, JSON file layer, cleanup task, and optional stdout mirror. The final subscriber registry combines an env filter, `ErrorLayer`, optional file/stdout layers, trace layer, OTLP log bridge, and metrics layer, then emits `rustfs_start_total`.

State/persistence behavior: Runtime state is owned by `OtelGuard`: tracer/meter/logger providers, profiling agents, non-blocking writer guards, stdout guard, and cleanup handle. Global state is mutated through `global::set_tracer_provider`, `global::set_text_map_propagator`, `global::set_meter_provider`, `metrics::set_global_recorder`, `set_observability_metric_enabled(true)`, and `tracing_subscriber::init`. Local log files are persisted via `RollingAppender`; cleanup is delegated to the local telemetry module.

Dependencies/integration: Uses OpenTelemetry SDK, OTLP exporters with HTTP binary protobuf and gzip, `tracing_opentelemetry`, `opentelemetry_appender_tracing`, `tracing_subscriber`, `metrics`, RustFS observability defaults, `build_resource`, `build_env_filter`, `Recorder`, `RollingAppender`, local JSON log/cleanup helpers, and optional Pyroscope/jemalloc crates behind feature/target gates. Header values are percent-decoded and signal-specific headers override common headers.

Risks/test signals: Initialization mutates process-global telemetry/subscriber state and will fail or panic in contexts that attempt multiple subscriber/global recorder installs. Invalid sample ratios fall back to `AlwaysOn`, which preserves telemetry but may increase volume. `Numeric` metrics export depends on successful recorder installation; failure aborts OTLP init. Log export disabled with an endpoint leaves `logger_provider` empty and only uses local fallback if a log directory exists. `MetricExporter`, `SpanExporter`, and `LogExporter` construction are covered only indirectly. Unit tests cover sampler validation, OTLP header parsing/override behavior, and timeout resolution; no test starts a real collector or validates full subscriber composition.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/otel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/recorder.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/recorder.rs

Purpose: Implements a `metrics::Recorder` that translates Rust `metrics` crate instruments into OpenTelemetry meter instruments while preserving labels, descriptions, units, and cached instrument handles.

Important APIs/types/functions: `Recorder::builder(name)` returns `Builder`, whose `with_meter_provider`, `with_instrumentation_scope`, `build`, `install`, and `install_global` configure and optionally install the recorder. `Recorder::with_meter` wraps an existing OpenTelemetry `Meter`. `MetricMetadata` stores one-shot description/unit data from `describe_*`. `WrappedCounter`, `WrappedGauge`, and `WrappedHistogram` implement `CounterFn`, `GaugeFn`, and `HistogramFn`.

Control flow: `describe_counter`, `describe_gauge`, and `describe_histogram` store metadata by `KeyName`. `register_counter/gauge/histogram` first consult type-specific `RwLock<HashMap<Key, _>>` caches. On a miss, the recorder builds an OpenTelemetry instrument using the metric name, removes matching metadata, converts labels to `KeyValue`s, wraps the instrument in the corresponding `metrics` handle, and inserts it into the cache with a second duplicate check under the write lock. Counter `absolute` emits a saturating delta from its tracked atomic value, gauges track the last f64 via atomic bits and CAS for increments/decrements, and histograms record one or many values.

State/persistence behavior: All state is in memory: a shared OpenTelemetry meter, metadata map, and per-type caches. Metadata is consumed on first registration for a metric name, so later registrations with different labels do not reuse descriptions/units unless described again before registration. Caches are keyed by full `metrics::Key`, including labels, preventing repeated instrument allocation for the same label set.

Dependencies/integration: Integrates `metrics` traits/types, OpenTelemetry `Meter`, `SdkMeterProvider`, `InstrumentationScope`, and RustFS `GlobalError`. The OTLP path in `otel.rs` uses this recorder so `metrics` macros flow into OpenTelemetry readers. Poisoned cache/metadata locks are logged with structured `tracing::error` fields and recovered by taking the inner guard.

Risks/test signals: Metadata removal by plain metric name can cause only the first label variant to receive description/unit metadata. `Counter::absolute` cannot emit negative deltas, so lowering an absolute counter records zero rather than a reset. Gauge NaN or unusual f64 bit patterns are stored directly. The register path may build an instrument concurrently more than once before one wins insertion, although only one handle is cached. Tests cover standard usage with stdout exporter, cache reuse for each metric type, and concurrent counter registration inserting one cache entry; they do not assert exported metric payloads or metadata behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/recorder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/resource.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/resource.rs

Purpose: Builds the shared OpenTelemetry `Resource` used by RustFS telemetry providers so all emitted traces, metrics, and logs carry consistent service identity and host/network metadata.

Important APIs/types/functions: `build_resource(config)` returns an `opentelemetry_sdk::Resource`. It sets `service.name`, `service.version`, `deployment.environment.name`, and `network.local.address` using config values with RustFS defaults.

Control flow: The builder takes `service_name`, `service_version`, and `environment` from `OtelConfig` when present, falling back to `APP_NAME`, `SERVICE_VERSION`, and `ENVIRONMENT`. It calls `get_local_ip_with_default()` for the host address and attaches semantic-convention attributes under `SCHEMA_URL`.

State/persistence behavior: Stateless aside from the current host IP lookup. It does not cache resources, mutate globals, or persist anything.

Dependencies/integration: Uses `OtelConfig`, OpenTelemetry semantic conventions (`SERVICE_VERSION`, `DEPLOYMENT_ENVIRONMENT_NAME`, `NETWORK_LOCAL_ADDRESS`), `Resource::builder`, RustFS config constants, and `rustfs_utils::get_local_ip_with_default`. `otel.rs` calls this once and clones the resource into enabled providers.

Risks/test signals: Local IP discovery can vary by network environment and may expose node-level address data in telemetry. Service name is converted through `Cow` and `to_string`, so non-static config values are copied safely. There are no direct unit tests for resource attributes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/resource.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/rolling.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/rolling.rs

Purpose: Implements a custom `Write` appender for local JSON logs with both time-based and size-based rotation. It replaces plain `tracing_appender` rolling files where RustFS needs maximum active file size enforcement plus archive naming that matches the log cleaner.

Important APIs/types/functions: `Rotation` supports `Minutely`, `Hourly`, `Daily`, and `Never`; `Rotation::check_should_roll` checks period boundaries, with daily boundaries aligned to the local offset. `RollingAppender::new`, `active_file_path`, `open_file`, `should_roll`, and `roll` manage file lifecycle. The `Write` impl rotates before writes that would exceed size or cross the time bucket. `ROLL_UNIQUIFIER` disambiguates archive names.

Control flow: `new` rejects filenames that are absolute or contain path components, initializes state, creates the log directory, and opens the active file eagerly. `open_file` retries append-open three times with backoff, records current file size, and seeds `last_roll_ts` from the file mtime so restart can trigger time rotation correctly. `write` lazily opens if needed, checks rotation, attempts `roll`, then writes to the active file and updates metrics. `roll` flushes and drops the current handle, renames active file to an archive name with timestamp/counter in either suffix or prefix mode, opens a new active file, updates rotation metrics, and recovers to the existing active file if rename fails.

State/persistence behavior: Persistent state is the active log file and archive files on disk. In-memory state tracks the current file handle, byte size, and last roll timestamp. Size is recovered from file metadata after restart, and time rotation state is approximated from mtime. Rotation failure intentionally favors continued logging over strict size limits, so the active file can grow past the configured maximum.

Dependencies/integration: Uses RustFS cleaner `FileMatchMode`, log-cleaner metric constants, `metrics::{counter,gauge,histogram}`, `jiff::Zoned` for timestamps/local offsets, and standard file I/O. `otel.rs` and local telemetry use it through `tracing_appender::non_blocking`; cleanup tasks use matching archive naming.

Risks/test signals: Daily rotation uses the current local offset, which may behave oddly across DST changes or if timezone settings change. On Unix, backslashes are accepted as filename characters because only platform path semantics are checked; on Windows they are rejected by path parsing. The rename retry handles permission/interrupted errors but not all race conditions. Tests cover eager file creation, invalid path rejection, basic writes, size rotation, archive-name uniqueness and prefix/suffix formats, and restart size recovery; no test covers time rotation or rename failure recovery.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/rolling.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/Cargo.toml -->
# sources/object-store/rustfs/crates/policy/Cargo.toml

Purpose: Defines the `rustfs-policy` crate metadata, dependency graph, lint inheritance, and library settings for RustFS policy management and enforcement code.

Important APIs/types/functions: The package is named `rustfs-policy` and inherits edition, license, repository, rust-version, version, and homepage from the workspace. It documents the crate as policy management for RustFS and disables doctests under `[lib]`.

Control flow: Cargo uses this manifest to compile policy code with workspace lints and dependencies. Runtime behavior is not implemented here, but selected dependency features shape the available APIs: `rustfs-config` enables `constants` and `opa`; `time` enables serde/parsing/formatting/macros; `tokio` uses `full`; `serde` enables derive and rc; `strum` enables derive; `ipnetwork` enables serde.

State/persistence behavior: No runtime state. Build state is governed by workspace lockfiles and feature resolution.

Dependencies/integration: Internal workspace crates include `rustfs-credentials`, `rustfs-config`, and `rustfs-crypto`. External dependencies support async execution (`tokio`, `async-trait`, `futures`, `pollster`), serialization (`serde`, `serde_json`), errors (`thiserror`), enums (`strum`), policy condition evaluation (`ipnetwork`, `base64-simd`, `regex`, `time`, `chrono`), JWT (`jsonwebtoken`), HTTP/OPA (`reqwest`), tracing, and caching (`moka`). Dev dependencies include `test-case` and `temp-env`.

Risks/test signals: The broad `tokio/full` and network-related dependencies increase compile surface for a policy crate. `doctest = false` means examples in docs will not be checked. Manifest correctness is indirectly tested by crate compilation; there are no manifest-specific tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/arn.rs -->
# sources/object-store/rustfs/crates/policy/src/arn.rs

Purpose: Parses and formats RustFS IAM role ARNs. It supports a narrow ARN shape for RustFS IAM roles: `arn:rustfs:iam:<region>::role/<resource_id>`.

Important APIs/types/functions: `ARN` stores `partition`, `service`, `region`, `resource_type`, and `resource_id`. `ARN::new_iam_role_arn(resource_id, server_region)` validates and constructs a role ARN. `ARN::parse(arn_str)` validates the six colon-separated ARN components and role resource. `Display` formats the canonical ARN with an empty account ID.

Control flow: Construction and parsing both validate resource IDs with `^[A-Za-z0-9_/\\.-]+$`. Parsing checks prefix `arn`, partition `rustfs`, service `iam`, empty account-id field, resource format containing `role/`, and resource type `role`; any mismatch returns `Error::other` with a specific message.

State/persistence behavior: Stateless value object. Persistence is only the string representation emitted by `Display` or accepted by `parse`.

Dependencies/integration: Uses crate-level `Error`/`Result` and `regex::Regex`. It is intended for IAM role and STS policy integration where role ARNs are compared or stored.

Risks/test signals: The regex is compiled on every call rather than static/lazy. `split(':')` rejects ARNs with colons inside resource IDs, which is consistent with this narrow grammar. Region is accepted without validation. No tests are present in this file, so parser compatibility depends on integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/arn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/auth/credentials.rs -->
# sources/object-store/rustfs/crates/policy/src/auth/credentials.rs

Purpose: Provides helpers for validating, generating, and constructing RustFS credentials, including service/session account JWT claims and optional embedded session policies.

Important APIs/types/functions: Constants define access/secret key length bounds, account status strings, and reserved characters. Public helpers include `contains_reserved_chars`, `is_access_key_valid`, `is_secret_key_valid`, `generate_credentials`, `get_new_credentials_with_metadata`, `create_new_credentials_with_metadata`, and `jwt_sign`. `CredentialsBuilder` collects optional session policy, keys, metadata, parent user, groups, and account flags, then `try_build`/`TryFrom<CredentialsBuilder>` returns `rustfs_credentials::Credentials`.

Control flow: `create_new_credentials_with_metadata` validates key lengths, returns an off account without session token when `token_secret` is empty, otherwise derives optional expiration from an `exp` claim, signs all claims through `utils::generate_jwt`, and returns an on account. `CredentialsBuilder` rejects empty parent users, one-sided key pairs, parent/access key equality, and the reserved `site-replicator-0` access key unless explicitly allowed. It creates a claim object with `parent`, embeds a base64 JSON session policy when supplied and <=4096 bytes, marks inherited policy otherwise, merges non-conflicting custom claims, generates missing keys, stores `accessKey`, signs a token with `rustfs_crypto::jwt_encode(access_key, claim)`, and fills the resulting credential metadata.

State/persistence behavior: No persistence is performed here, but returned `Credentials` include durable fields consumed by IAM storage: access key, secret key, status, session token, expiration, parent user, groups, name, description, and claims. Generated credentials are random through `rustfs_credentials`.

Dependencies/integration: Integrates `rustfs_credentials::Credentials`, `rustfs_credentials` constants/generators, `rustfs_crypto::jwt_encode`, policy validation via `Policy::is_valid`, serde JSON, base64 encoding, `time::OffsetDateTime`, and crate JWT utilities. It is consumed by the public `auth` module and IAM account flows.

Risks/test signals: Overlong secret keys in `create_new_credentials_with_metadata` currently return `InvalidAccessKeyLength`, likely a copy/paste bug where `InvalidSecretKeyLength` was intended. `is_access_key_valid` and `is_secret_key_valid` only enforce minimum length, while credential creation enforces min and max. `contains_reserved_chars` uses `s.contains(\"=,\")`, which checks the literal two-character substring rather than either reserved character. The builder signs using the access key as JWT secret rather than the secret key/token secret path used by other helper functions, which should be verified against intended compatibility. Unit tests for credential header parsing are commented out, leaving this file without active direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/auth/credentials.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/auth/mod.rs -->
# sources/object-store/rustfs/crates/policy/src/auth/mod.rs

Purpose: Public authentication module that re-exports credential helpers and defines persisted user identity metadata around `rustfs_credentials::Credentials`.

Important APIs/types/functions: `pub use credentials::*` exposes the credential API. `UserIdentity` stores `version`, `credentials`, and optional `update_at` timestamp serialized as `updatedAt` with `update_at` alias. `UserIdentity::new`, `From<Credentials>`, `add_ssh_public_key`, and `get_ssh_public_keys` manage identity creation and SFTP public-key claims.

Control flow: New identities set version `1` and `update_at` to `OffsetDateTime::now_utc()`. SSH key addition lazily creates `credentials.claims` and inserts `"ssh_public_keys"` as a JSON array containing the provided key. Retrieval walks optional claims, expects an array, filters string values, and returns an empty vector for missing/malformed data.

State/persistence behavior: `UserIdentity` is a serializable storage shape. Timestamp serde accepts legacy `update_at` but emits `updatedAt`; this preserves compatibility with MinIO/RustFS-style IAM JSON. SSH keys are persisted inside credential claims.

Dependencies/integration: Uses the private `credentials` module, `rustfs_credentials::Credentials`, serde, serde JSON, `HashMap`, `time::OffsetDateTime`, and crate datetime serde helpers. Identity values are likely stored by IAM user/account subsystems.

Risks/test signals: `add_ssh_public_key` replaces any existing `"ssh_public_keys"` claim instead of appending, so multiple calls keep only the last key. There is no validation of SSH public key syntax. Tests cover deserializing MinIO-style RFC3339 `updatedAt`; no tests cover SSH key mutation or legacy `update_at` alias.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/auth/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/error.rs -->
# sources/object-store/rustfs/crates/policy/src/error.rs

Purpose: Defines the crate-wide `Error` and `Result` types for IAM/policy operations outside the inner policy syntax module, along with helper predicates for common not-found variants.

Important APIs/types/functions: `Error` variants cover wrapped `policy::Error`, string errors, crypto/JWT errors, IAM not-found cases, invalid arguments/state, credential/key problems, access denial, policy size, I/O, and initialization conflicts. `Error::other` wraps arbitrary errors as `std::io::Error::other`. `From` impls convert `std::io::Error`, `time::error::ComponentRange`, `serde_json::Error`, and `regex::Error`; `thiserror` derives conversions for policy, crypto, and JWT errors. Predicate helpers include `is_err_no_such_policy`, `is_err_no_such_user`, `is_err_no_such_account`, `is_err_no_such_temp_account`, `is_err_no_such_group`, and `is_err_no_such_service_account`.

Control flow: Callers use `?` to convert lower-level errors into this enum. Non-enum arbitrary errors are intentionally collapsed into `Error::Io(ErrorKind::Other)` through `Error::other`, preserving display text but losing precise type information.

State/persistence behavior: Stateless error representation. The display strings are user/API visible and may be part of compatibility expectations.

Dependencies/integration: Bridges `crate::policy`, `rustfs_crypto`, `jsonwebtoken`, `serde_json`, `time`, `regex`, and standard I/O. The auth, ARN, and policy modules return this `Result` for operational errors.

Risks/test signals: Converting JSON/time/regex failures into I/O `Other` obscures source categories. There is both `StringError` and `Error::other`, so callers may produce inconsistent variants for similar failures. Tests cover conversions, helper predicates, display formatting for many variants, and `StringError`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/format.rs -->
# sources/object-store/rustfs/crates/policy/src/format.rs

Purpose: Defines a minimal serializable IAM format/version marker.

Important APIs/types/functions: `Format` is a `Deserialize`, `Serialize`, `Default` struct containing `version: i32`. Commented code suggests intended constants for config path and default version.

Control flow: There is no behavior beyond serde/default construction.

State/persistence behavior: Intended as a persisted shape for IAM format metadata, likely under a config path, but current code only defines the struct and does not provide path/default helpers.

Dependencies/integration: Depends only on serde. Exposed publicly through `lib.rs`.

Risks/test signals: Default version is `0` because no custom `Default` impl exists, while comments suggest a default version of `1`; callers relying on `Default` may persist an unintended version. No tests cover this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/format.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/lib.rs -->
# sources/object-store/rustfs/crates/policy/src/lib.rs

Purpose: Crate root for `rustfs-policy`; exposes the policy, auth, ARN, error, format, datetime, service type, and utility modules.

Important APIs/types/functions: Public modules are `arn`, `auth`, `error`, `format`, `policy`, `serde_datetime`, `service_type`, and `utils`. No functions or types are declared directly in this file.

Control flow: Rust module declaration only; it defines the public API surface and compilation units.

State/persistence behavior: None directly. It exposes modules that define persisted IAM/policy JSON shapes and serialization helpers.

Dependencies/integration: Used by downstream crates through module paths such as `rustfs_policy::policy::Policy`, `rustfs_policy::auth::UserIdentity`, and `rustfs_policy::error::Error`.

Risks/test signals: Publicly exposing `utils` may make helper internals part of the effective API. There are no root-level tests; correctness is compilation plus module-specific tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy.rs -->
# sources/object-store/rustfs/crates/policy/src/policy.rs

Purpose: Top-level policy module facade. It declares policy submodules, re-exports core policy types, and defines policy-syntax validation errors.

Important APIs/types/functions: Public/re-exported API includes `ActionSet`, `PolicyDoc`, `Effect`, `Functions`, `ID`, `Policy`, `Principal`, `ResourceSet`, `Statement`, `ClaimLookup`, and `get_claim_case_insensitive`. Submodules include action, doc, effect, function, id, opa, policy, principal, resource, statement, utils, and variables. `policy::Error` variants describe invalid policy version/effect/action/key/resource shape and conflicting action/resource fields.

Control flow: This file has no evaluator logic itself; it centralizes module wiring and the error taxonomy used by validators and deserializers in submodules.

State/persistence behavior: None directly. Re-exported types define persisted policy documents and evaluation state.

Dependencies/integration: The outer crate `error::Error` wraps `policy::Error`, and downstream code imports policy primitives from here. `opa`, `resource`, `statement`, and `variables` are part of the broader policy engine even though this work item focuses on specific files.

Risks/test signals: Re-export choices define API stability. `function` is private but `Functions` is public, so internals can change while the condition aggregate stays exposed. No tests in this file directly; submodule tests cover individual behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/action.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/action.rs

Purpose: Defines supported IAM/S3/admin/STS/KMS action names, their serde representation, wildcard matching, and action-set behavior for policy statements.

Important APIs/types/functions: `ActionSet(Vec<Action>)` serializes as an array, deserializes from a string or array, de-duplicates entries, compares as an unordered set, and implements `is_match`. `Action` wraps `S3Action`, `AdminAction`, `StsAction`, `KmsAction`, or `None`, parses by prefix, and uses wildcard matching on string forms. Large enums enumerate supported `s3:*`, `admin:*`, `sts:*`, and `kms:*` action strings. `AdminAction::is_table_resource_scoped` identifies table-scoped admin actions; `AdminAction::is_valid` whitelists recognized admin variants.

Control flow: Deserialization accepts a single action string or sequence, parsing each through `Action::try_from`. The bare `"*"` wildcard maps to `S3Action::AllActions`. `ActionSet::is_match` returns true if any stored action wildcard-matches the requested action, with a special case allowing `s3:GetObjectVersion` to match `s3:GetObject`. `Action::try_from` returns `InvalidAction` through the outer crate error type when prefix parsing fails.

State/persistence behavior: Action sets are stored as JSON arrays of strings even for one element, supporting S3 policy compatibility. Duplicate actions are removed during deserialization, but manual `ActionSet(vec![...])` can still contain duplicates until serialized/evaluated.

Dependencies/integration: Uses serde, `strum` enum string conversions, policy wildcard utilities, crate `Error`/`Result`, and `policy::Error`. Policy statement validation and request authorization depend on this taxonomy.

Risks/test signals: The bare `"*"` mapping only becomes S3 all-actions, not all action families. `ActionSet::is_valid` currently returns `Ok(())` without checking emptiness or family mixing; those checks may live in statement/policy validators. Manual enum additions must update `AdminAction::is_valid` when applicable. Tests cover wildcard parsing, STS/KMS parsing and wildcard matching, array serialization, and many table/admin action validity cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/action.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/doc.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/doc.rs

Purpose: Defines a versioned persisted policy document wrapper that can carry create/update timestamps around a `Policy` while also accepting legacy bare policy JSON.

Important APIs/types/functions: `PolicyDoc` has `Version`/`version`, `Policy`/`policy`, `CreateDate`/`create_date`, and `UpdateDate`/`update_date` serde mappings. `PolicyDoc::new`, `update`, and `default_policy` construct or mutate wrappers. `TryFrom<Vec<u8>>` parses either a `PolicyDoc` or a bare `Policy`.

Control flow: `new` sets version `1` and both timestamps to now. `update` increments version, replaces policy, updates update date, and backfills create date if it was missing. `default_policy` creates version `1` without timestamps. The byte parser first attempts full document deserialization, then falls back to bare policy and wraps it; if both fail it emits a custom serde error.

State/persistence behavior: This is a persisted JSON compatibility boundary. It serializes with MinIO-style capitalized field names and RFC3339 option timestamps through crate datetime helpers while accepting legacy lowercase aliases.

Dependencies/integration: Uses serde, `time::OffsetDateTime`, `crate::serde_datetime::option`, and `Policy`. IAM policy storage/loading code can use it to preserve update metadata while remaining backward compatible.

Risks/test signals: If bare `Policy` parsing succeeds, wrapper metadata defaults to version `0` and no dates because `Default` is used. `TryFrom<Vec<u8>>` masks the detailed first/second parse errors with a generic custom error. Tests cover RFC3339 serialization, MinIO-style timestamp deserialization, and timestamp round-trip.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/doc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/effect.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/effect.rs

Purpose: Represents statement effects (`Allow` or `Deny`) and provides simple logic for translating a condition/resource/action match into an allowed result.

Important APIs/types/functions: `Effect` is a serde/strum enum with default `Allow`. `TryFrom<String>` parses effect strings. `Effect::is_allowed(allowed)` returns `allowed` for `Allow` and `!allowed` for `Deny`. It implements `Validator` with a no-op `is_valid`.

Control flow: Deserialization uses `try_from = "String"` and string enum parsing. `is_allowed` applies the effect as a boolean inversion for deny.

State/persistence behavior: Persisted as `"Allow"` or `"Deny"` in policy JSON. No in-memory state beyond enum value.

Dependencies/integration: Uses serde, `strum`, crate `Error`/`Result`, and policy `Validator`. Statement evaluation likely combines this with match results.

Risks/test signals: Defaulting to `Allow` can be dangerous if a missing/invalid effect path ever falls through to default construction rather than serde validation. `TryFrom` maps `strum::ParseError` to `Error::StringError`, not the inner `policy::Error::InvalidEffect`. No direct tests in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/effect.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function.rs

Purpose: Aggregates policy condition operators into `Functions`, handling `ForAnyValue`, `ForAllValues`, and normal condition groups, plus serde and evaluation dispatch.

Important APIs/types/functions: `Functions` stores three vectors of `Condition`: `for_any_value`, `for_all_values`, and `for_normal`. `evaluate` and `evaluate_with_resolver` run all conditions asynchronously. `is_empty` and `references_key_name` support validation and policy analysis. Custom serde serializes/deserializes condition maps with optional `ForAnyValue:` or `ForAllValues:` qualifiers. `Value` is an unused serializable marker type.

Control flow: Evaluation short-circuits false. `ForAnyValue` conditions pass `for_all=false`, `ForAllValues` pass `for_all=true`, and normal conditions pass `for_all=false` into each `Condition`. Deserialization rejects duplicate operator keys, parses at most one qualifier prefix separated by `:`, rejects unknown qualifiers or extra separators, and delegates each operator body to `Condition::from_deserializer`.

State/persistence behavior: No external state. The persisted policy shape is a JSON map whose keys are condition operator names, optionally prefixed with `ForAnyValue:` or `ForAllValues:`. Empty maps are accepted; a commented block suggests they may once have been rejected.

Dependencies/integration: Re-exports and uses submodules `addr`, `binary`, `bool_null`, `condition`, `date`, `func`, `key`, `key_name`, `number`, and `string`. Async evaluation can use `PolicyVariableResolver` to resolve policy variables through string conditions.

Risks/test signals: Duplicate detection uses the raw operator key string, so semantically related keys like `StringEquals` and `StringEqualsIfExists` are distinct. Empty condition maps evaluate true. Evaluation order is deterministic by vector order from serde map traversal. Tests cover many deserialization shapes, numeric/date/string/ARN operator parsing, IfExists syntax, and serialization ordering for grouped conditions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/addr.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/addr.rs

Purpose: Implements IP address condition values and evaluation for `IpAddress` and, through `Condition` negation, `NotIpAddress`.

Important APIs/types/functions: `AddrFunc` is `InnerFunc<AddrFuncValue>`. `AddrFunc::evaluate(values)` checks request context IP values against configured CIDR networks. `AddrFuncValue(Vec<IpNetwork>)` deserializes from a string or string array and serializes transparently.

Control flow: For each configured key/value pair, evaluation looks up request values by the condition key's short name, parses each request string as `IpAddr`, and returns true as soon as any IP is contained in any configured network. If a request value cannot parse, it returns false. If there are no matching request values across all configured entries, it returns false. Deserialization appends `/32` to values without a slash before parsing as `IpNetwork`.

State/persistence behavior: Stateless in memory; persisted policy values are CIDR strings or arrays. Serialization normalizes single string inputs to arrays because `IpNetwork` vec is transparent and tests expect arrays.

Dependencies/integration: Uses `ipnetwork` with serde, `InnerFunc`, `Key`, and `KeyName`. `Condition::NotIpAddress` inverts `AddrFunc::evaluate` through `is_negate`.

Risks/test signals: Appending `/32` to IPv6 host literals means host IPv6 values become `/32`, which is a broad IPv6 network rather than the usual `/128`; tests encode this behavior but it may not match AWS semantics. Evaluation returns true on the first matching configured key and does not require all `InnerFunc` entries to match. Tests cover IPv4/IPv6 CIDR and host parsing, variables, arrays, and serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/addr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/binary.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/binary.rs

Purpose: Implements AWS IAM `BinaryEquals` policy values and evaluation using base64-decoded byte comparison.

Important APIs/types/functions: `BinaryFunc` is `InnerFunc<BinaryFuncValue>`. `BinaryFuncValue` stores original encoded strings for serialization and decoded byte vectors for comparison. `BinaryFuncValue::new`, `TryFrom<String>`, `TryFrom<&str>`, custom serde, and `BinaryFunc::evaluate` provide parsing and evaluation. `BinaryFuncValueError::InvalidBase64` reports malformed values.

Control flow: Policy deserialization accepts one base64 string or a non-empty array, eagerly decodes every value, and rejects malformed base64 at parse time. Evaluation requires every configured key/value pair to match. For each key, missing request values return false; each request value is decoded from base64, and any malformed request value fails closed immediately; at least one decoded request value must equal one configured decoded value.

State/persistence behavior: No external state. Policy JSON round-trips the original encoded string/array form, while equality compares decoded bytes to avoid formatting differences.

Dependencies/integration: Uses `base64-simd`, serde, `HashMap`, and `InnerFunc`. `Condition::BinaryEquals` delegates directly here.

Risks/test signals: Failing closed on any invalid request value means a request with one valid matching binary value and one malformed value is denied. Empty arrays are rejected. Evaluation expects request context values to still be base64 strings, not raw decoded header bytes. Tests are strong: decoded match/non-match, missing/empty keys, multi-value OR behavior, invalid request fail-closed behavior, all-key AND behavior, serde parse rejection, and round-trips.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/binary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/bool_null.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/bool_null.rs

Purpose: Implements boolean condition operands for `Bool` and `Null` IAM condition operators.

Important APIs/types/functions: `BoolFunc` is `InnerFunc<BoolFuncValue>`. `evaluate_bool` compares configured booleans with request string values. `evaluate_null` checks request-key presence/absence. `BoolFuncValue` serializes booleans as strings and deserializes from bools, `"true"`/`"false"` strings, or a one-element array.

Control flow: `evaluate_bool` requires every configured key to have a first request value equal to the configured boolean's lowercase string; missing keys or mismatches fail. `evaluate_null` computes request vector length and, for a configured `true`, requires zero values; for `false`, requires at least one value. Deserialization rejects empty arrays, arrays with more than one value, and non-boolean strings.

State/persistence behavior: Policy JSON emits `"true"` or `"false"` strings even if input used JSON booleans. No external state.

Dependencies/integration: Uses serde visitors and `InnerFunc`. `Condition::Bool` and `Condition::Null` delegate here.

Risks/test signals: `evaluate_bool` only inspects the first request value, ignoring later values. A present key with an empty vector is considered null for `Null`. Tests cover bool/string/one-element-array deserialization, invalid inputs, variable suffix keys, and serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/bool_null.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/condition.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/condition.rs

Purpose: Defines the condition-operator enum and dispatches parsing, serialization, key-reference analysis, and asynchronous evaluation for all policy condition types.

Important APIs/types/functions: `Condition` variants cover string/ARN equals/like/not/ignore-case operators, `BinaryEquals`, `IpAddress`, `NotIpAddress`, `Null`, `Bool`, numeric comparisons, date comparisons, dedicated `NumericGreaterThanIfExists`, and generic `IfExists(Box<Condition>)`. Key functions include `from_deserializer`, `to_key`, `to_key_with_suffix`, `has_any_key_in`, `references_key_name`, `evaluate_with_resolver`, `is_negate`, and `serialize_map`.

Control flow: `from_deserializer` maps an operator key to a typed condition body; unknown keys ending in `IfExists` recursively parse the base operator and wrap it. Evaluation delegates to typed functions: string/ARN operators use `StringFunc::evaluate_with_resolver` with flags for case, wildcard, and negation; binary/IP/bool/null/number/date use their specialized evaluators. Generic `IfExists` returns true when none of the referenced keys appear in the request context, otherwise delegates to the inner condition. After delegate evaluation, `is_negate` currently only inverts `NotIpAddress`; string negations are handled by flags to avoid double negation.

State/persistence behavior: No external state. Serde uses `to_key_with_suffix` and `serialize_map` so wrapper conditions serialize as operator keys like `StringEqualsIfExists`; nested wrappers serialize with repeated suffixes.

Dependencies/integration: Integrates all function operand modules, `PolicyVariableResolver`, `KeyName`, serde map APIs, `HashMap`, and `time::OffsetDateTime`. It is the central dispatch point used by `Functions`.

Risks/test signals: `NumericGreaterThanIfExists` delegates to `i64::ge` rather than `i64::gt`, so its semantics look like greater-than-or-equal if present. There is no generic `IfExists` special handling for all dedicated variants beyond suffix parsing; nested IfExists is allowed and serialized. `NotIpAddress` is the only post-dispatch negation; other future negative operators must avoid double-negation mistakes. Tests specifically cover StringNotEquals no double negation, absent-key behavior, IfExists serialization/deserialization, and IfExists evaluation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/condition.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/date.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/date.rs

Purpose: Implements RFC3339 date/time condition values and comparisons for date IAM operators.

Important APIs/types/functions: `DateFunc` is `InnerFunc<DateFuncValue>`. `DateFunc::evaluate(op, values)` compares configured `OffsetDateTime` values with request context values using the supplied comparison function. `DateFuncValue` wraps `OffsetDateTime` with custom RFC3339 serde.

Control flow: For every configured key/value pair, evaluation reads the first request value by short key name, parses it as RFC3339, and applies the comparison as `op(&policy_value, &request_value)`. Missing or unparsable request values fail. Serialization formats the policy value using `Rfc3339`.

State/persistence behavior: Policy JSON stores dates as RFC3339 strings. No external state.

Dependencies/integration: Uses `time::OffsetDateTime` and the well-known `Rfc3339` format, serde, `HashMap`, and `InnerFunc`. `Condition` supplies equality/ordering functions for date variants.

Risks/test signals: Comparison argument order is policy value first and request value second, which must be checked against intended IAM semantics for less-than/greater-than operators. Only the first request value is considered. Tests cover parsing and serialization for object-lock retain-until date keys with and without variable suffixes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/date.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/func.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/func.rs

Purpose: Provides the generic map representation shared by typed condition functions: policy condition keys mapped to operator-specific values.

Important APIs/types/functions: `InnerFunc<T>(Vec<FuncKeyValue<T>>)` stores one condition operator body. `FuncKeyValue<T>` stores `Key` and typed `values`. `InnerFunc::key_names` returns request-context short key names, and `contains_key_name` checks references. Custom serde serializes as a map from key to value and deserializes maps into `FuncKeyValue` entries.

Control flow: Deserialization visits a map, deserializes each key through `Key` and each value as `T`, pushes entries in input order, and rejects an empty map with `"has no condition key"`. Serialization emits each key/value pair.

State/persistence behavior: This is a persisted policy JSON shape but has no external state. It preserves input order in the internal vector, although equality for wrappers may treat vectors/order according to derived or custom comparisons.

Dependencies/integration: Used by string, address, binary, bool/null, date, and number condition modules. Depends on serde and `Key`/`KeyName`.

Risks/test signals: Duplicate keys in a condition map are not explicitly rejected here; serde map behavior and JSON parser behavior determine what reaches the visitor. Empty condition bodies are rejected at this lower level even though empty `Functions` is accepted. There are no direct tests in this file; typed function tests cover its serde path.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/func.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/key.rs

Purpose: Represents a condition key, including the known key name and optional variable suffix after a slash.

Important APIs/types/functions: `Key { name: KeyName, variable: Option<String> }` implements serde as/from a string. `Key::is`, `var_name`, and `name` expose comparisons and rendered names. `From<Key> for String` emits the full key string. `TryFrom<&str>` parses `name[/variable]`.

Control flow: Parsing splits the input at the first `/`; the prefix is parsed as `KeyName`, and any remainder is stored as `variable` without further validation. `name()` returns the short key name without the namespace prefix and appends `/variable` if present; `var_name()` returns the `${namespace:key}` variable placeholder from `KeyName`.

State/persistence behavior: No external state. This defines how condition keys are persisted in policy JSON and how they map to request context keys for evaluation.

Dependencies/integration: Uses `KeyName`, crate `Error`, policy `Error::InvalidKey`, and `Validator`. All typed condition functions depend on `Key`.

Risks/test signals: Variables are not validated for emptiness or allowed characters. `name()` strips the namespace prefix, so request context maps must use short names like `x-amz-copy-source` or `SourceIp` rather than full `s3:`/`aws:` keys. Tests cover serialization/deserialization success and invalid key names across namespaces.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key_name.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/key_name.rs

Purpose: Enumerates all recognized policy condition key names across S3, AWS, JWT, LDAP, STS, and service-account namespaces, and maps between strings, short names, and policy variable placeholders.

Important APIs/types/functions: `KeyName` wraps `AwsKeyName`, `JwtKeyName`, `LdapKeyName`, `StsKeyName`, `SvcKeyName`, and `S3KeyName`. `TryFrom<&str>` dispatches by namespace prefix. `COMMON_KEYS` lists keys used for variable substitution in string conditions. `prefix`, `name`, and `var_name` compute prefix length, short key name, and `${...}` placeholder. Each namespace enum uses `strum` for exact string parsing/serialization.

Control flow: Parsing is case-sensitive and prefix-specific; unknown prefixes or misspelled keys return `InvalidKeyName`. `name()` returns the part after the namespace prefix by slicing the enum string. `var_name()` rebuilds a `${namespace:key}` string using the full enum string.

State/persistence behavior: No external state. These enum variants define the accepted persisted policy condition key vocabulary.

Dependencies/integration: Uses serde and `strum`. `Key`, `StringFunc` variable substitution, `Functions::references_key_name`, and condition validators depend on this vocabulary.

Risks/test signals: Adding a condition key requires updating the right enum and possibly `COMMON_KEYS` if it should participate in variable substitution. `KeyName::name()` returns short names that may collide across namespaces, so request context maps need consistent naming. Tests cover successful parsing/serde, failed case-sensitive parsing, and JWT roles support.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key_name.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/number.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/number.rs

Purpose: Implements integer condition values and comparisons for numeric IAM operators.

Important APIs/types/functions: `NumberFunc` is `InnerFunc<NumberFuncValue>`. `NumberFunc::evaluate(op, if_exists, values)` applies a supplied integer comparison to request and policy values. `NumberFuncValue(i64)` serializes as a string and deserializes from JSON signed integers, unsigned integers, or numeric strings.

Control flow: For each configured key, evaluation reads the first request value. If missing, it returns the supplied `if_exists` boolean. If present, it parses the request as `i64` and applies `op(&request_value, &policy_value)`. Any parse failure or failed comparison returns false; all configured key comparisons must pass.

State/persistence behavior: Policy JSON emits numeric values as strings. No external state.

Dependencies/integration: Uses serde, `HashMap`, and `InnerFunc`. `Condition` passes the correct comparison functions and the `if_exists` flag for numeric variants.

Risks/test signals: `visit_u64` casts to `i64` with `as`, so values above `i64::MAX` wrap to negative numbers rather than being rejected. Only the first request value is considered. The dedicated `NumericGreaterThanIfExists` caller currently passes `i64::ge`, which changes strict greater-than semantics. Tests cover serde for integer and string inputs plus variable suffix keys; they do not cover overflow or evaluation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/number.rs -->
