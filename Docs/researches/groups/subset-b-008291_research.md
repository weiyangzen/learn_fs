# Group Research: subset-b-008291

This grouped report covers the RustFS target runtime TLS reload, queue store, integration-test, shared TLS runtime, and trusted-proxy cloud metadata files assigned to `subset-b-008291`. Each section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/sidecar_protocol.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/sidecar_protocol.rs

Purpose: defines the JSON-serializable handshake contract between the RustFS target runtime and an external sidecar plugin. The protocol version constant is `SIDECAR_RUNTIME_PROTOCOL_VERSION = "rustfs.target-runtime.v1"`, and the file models the minimum plugin capability surface as `SidecarPluginCapability::{HealthCheck, SendEvent, Shutdown}`.

Important APIs/types/functions: `SidecarHandshake` carries `protocol_version`, `plugin_id`, `plugin_version`, `supported_domains: Vec<TargetDomain>`, and `capabilities`. `SidecarHandshake::validate(expected_plugin_id)` enforces exact protocol version, exact plugin id, and presence of all three required capabilities. Serde `snake_case` renaming makes this the wire contract for sidecar IPC.

Control flow and state: validation is pure and stateless. It returns the first contract violation as a `String` error and otherwise `Ok(())`; it does not currently validate `supported_domains` against a caller requirement.

Dependencies and integration points: depends on `crate::TargetDomain` and serde. Sidecar launch/registration code should call `validate` after receiving a handshake before routing target events to the plugin.

Risks: all capabilities are mandatory, so adding a capability to the hard-coded loop would become a breaking protocol change. Error strings include expected and actual ids/versions, useful for operators but potentially noisy in logs. Domain support is advertised but not enforced here.

Test signals: unit tests cover accepting the expected contract and rejecting protocol mismatch. Missing tests include plugin id mismatch, missing capability, and domain filtering behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/sidecar_protocol.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/adapter.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/adapter.rs

Purpose: provides `TlsReloadAdapter<M>`, the small per-target handle that connects a concrete `ReloadableTargetTls` implementation to `TargetTlsReloadCoordinator`. Targets can hold `Option<TlsReloadAdapter<M>>` and use it on their send hot path while retaining a legacy fallback when registration fails.

Important APIs/types/functions: `try_register(target, options, coordinator)` delegates to `coordinator.register`, logs success or failure, and returns `Some(adapter)` only after initial material has been built and, for poll/hybrid mode, the background loop has been spawned. `current_material()` clones the current `Arc<M>` from the coordinator-managed `ArcSwap`; `generation()` returns the active generation; `status_snapshot()` calls `TargetTlsReloadCoordinator::build_status_snapshot`; `runtime_state()` exposes the shared state for cleanup; `unregister()` stops the coordinator entry for the target label.

Control flow and state: the adapter stores `Arc<TargetTlsRuntimeState<M>>` plus the `TlsReloadOptions` used for snapshots. Cloning the adapter shares the same runtime state and options. It never mutates TLS material directly; all mutation is owned by the coordinator.

Dependencies and integration points: depends on target TLS config/coordinator/state/trait modules, `Arc`, and tracing. It is the ergonomic boundary used by AMQP, SQL, webhook, or other TLS-capable target implementations.

Risks: failed registration silently degrades to fallback behavior by returning `None`; callers must preserve and exercise the fallback. `unregister` is best-effort and logs warnings instead of propagating errors.

Test signals: tests use a fake target to prove success builds material once, failure returns `None`, clones share state, and snapshots expose the target label and reload enablement.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/config.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/config.rs

Purpose: keeps the targets crate on the same TLS reload configuration model as the shared `rustfs_tls_runtime` crate. This file is a compatibility/re-export layer rather than an independent configuration implementation.

Important APIs/types/functions: re-exports `TlsReloadOptions`, `ReloadDetectMode`, and aliases `rustfs_tls_runtime::config::ReloadApplyHint` as `ReloadApplyMode`. The alias preserves target-side naming while tying behavior to the shared runtime type.

Control flow and state: none; all defaults and semantics live in `crates/tls-runtime/src/config.rs`. Default options there enable polling every 15 seconds, debounce for 2 seconds, use a 1 second minimum stable age field, and apply lazily.

Dependencies and integration points: used by target TLS adapter, coordinator, trait, and tests. Because this is a re-export, crate users can import target TLS configuration through the targets crate without depending directly on `rustfs-tls-runtime`.

Risks: the alias can hide the fact that target-side `ReloadApplyMode` is actually a shared `ReloadApplyHint`. Any change to the shared enum is an API change here. There are no local tests because there is no local logic.

Test signals: behavior is indirectly covered by target coordinator and adapter tests that construct `TlsReloadOptions` and match `ReloadApplyMode` variants.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/coordinator.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/coordinator.rs

Purpose: implements the target-level TLS reload coordinator. It registers TLS-capable targets, builds initial TLS material, spawns per-target polling loops, performs fingerprint-based reload decisions, validates material, applies newly built material, publishes it atomically, and records target TLS metrics.

Important APIs/types/functions: `TargetTlsReloadCoordinator` owns a `RwLock<HashMap<String, TargetReloadEntry>>`. `register` rejects disabled options, calls `target.tls_input_set`, builds initial material, fingerprints configured CA/cert/key files, publishes generation 1 into `TargetTlsRuntimeState`, and starts `spawn_target_poll_loop` for poll/hybrid detection. `unregister` and `shutdown` cancel/abort poll tasks. `force_reload` runs one reload cycle. `build_status_snapshot` serializes runtime status. Private `reload_target_once` performs read/compare/validate/build/apply/publish.

Control flow and state: each poll loop delays its first tick, honors a debounce check against `last_attempt_unix_ms`, then calls `reload_target_once`. Reload updates `last_attempt` first, skips unchanged fingerprints, validates generic TLS files and target-specific files, builds new material before changing state, asks the target to apply it, then stores a new `TargetTlsPublishedState` in `current` and `last_good`. On any failure, current and last-good material stay untouched and `last_error` is set.

Dependencies and integration points: integrates with `ReloadableTargetTls`, `TargetTlsRuntimeState`, target fingerprint/validate modules, metrics, Tokio tasks/channels, and tracing. Targets use the returned runtime state through `TlsReloadAdapter`.

Risks: `min_stable_age` exists in options but this coordinator only uses `debounce`; there is no file mtime stability check. `register` inserts entries by label and would overwrite an existing entry with the same label without first stopping the old poll loop. `bump_generation` is computed from current state before publish, so concurrent forced reloads on the same runtime state could race unless callers serialize them.

Test signals: unit tests cover initial material creation, disabled registration, shutdown/unregister, unchanged reload skip, build/apply/validate failure preservation, clearing errors after success, preserving `last_good`, status snapshots, and generation saturation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/coordinator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/fingerprint.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/fingerprint.rs

Purpose: provides target-specific TLS fingerprint and generation types used to detect CA/client certificate/client key changes for outbound target connections.

Important APIs/types/functions: `TargetTlsFingerprint` stores optional SHA256 digests for CA, client cert, and client key. `TargetTlsGeneration(pub u64)` is a saturating generation counter wrapper. `TargetTlsState` combines generation and optional fingerprint, with `refresh`, `needs_update`, and `reset`. `build_target_tls_fingerprint(ca_path, client_cert_path, client_key_path)` asynchronously reads non-empty paths and digests bytes through `rustfs_tls_runtime::TlsFingerprint::from_optional_bytes`.

Control flow and state: empty paths map to `None` digests. `TargetTlsState::refresh` mutates only when the candidate fingerprint differs, saturating generation upward and storing the new fingerprint. `needs_update` is a non-mutating gate intended for build-before-publish flows.

Dependencies and integration points: uses `tokio::fs::read`, `TargetError::Configuration`, and shared runtime fingerprint hashing. It feeds `TargetTlsReloadCoordinator` comparisons and initial state.

Risks: it reads whole files into memory; acceptable for TLS material but still unbounded by code. Error messages include paths. Reusing `TlsFingerprint::server_sha256` for each target file digest is a convenient but slightly opaque implementation detail.

Test signals: unit tests cover generation increments only on change, reset, equality when all digest fields match, and inequality on CA differences. File-read error and empty-path behavior are exercised indirectly by coordinator tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/fingerprint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/metrics.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/metrics.rs

Purpose: declares and records metrics for per-target TLS reload behavior.

Important APIs/types/functions: `init_target_tls_metrics()` describes counters, gauges, and histograms for reload attempts, skipped reloads, current generation, reload duration, publication failures, and stale generation observations. `record_target_tls_reload_result(target, result, duration_secs, generation)` increments attempts, records duration, and updates generation. `record_target_tls_reload_skipped`, `record_target_tls_publication_fail`, and `record_target_tls_stale_generation` provide focused counters.

Control flow and state: no in-memory state beyond metrics recorder side effects. Labels use `target_id`, `result`, and `reason` with owned strings so target labels can be dynamic.

Dependencies and integration points: used by the target TLS coordinator and potentially by target send paths that detect stale generation. It depends on the `metrics` crate macros.

Risks: unbounded `target_id` labels can increase metric cardinality if target labels include user-generated or high-churn values. The histogram is recorded for successes in the coordinator; some failure paths use only publication-fail counters and do not record reload duration/result.

Test signals: no local tests. Indirect signal comes from coordinator paths invoking these functions; metric registration correctness depends on runtime metrics backend behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/mod.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/mod.rs

Purpose: is the public module boundary for target TLS hot reload support. It organizes adapter, config, coordinator, fingerprint, metrics, state, trait, and validation helpers and re-exports the main types.

Important APIs/types/functions: re-exports `TlsReloadAdapter`, `TargetTlsReloadCoordinator`, fingerprint types and builder, `init_target_tls_metrics`, runtime state/status types, `ReloadableTargetTls`, and `validate_tls_material`.

Control flow and state: none. The file establishes import ergonomics and crate-facing API shape.

Dependencies and integration points: target implementations can depend on `runtime::tls::*` instead of individual submodules. It bridges target-specific code with shared `rustfs_tls_runtime` config and certificate parsing helpers.

Risks: because it re-exports broad internals, later module refactors can become public API changes. The raw identifier module `r#trait` avoids reserved keyword conflict but may be mildly awkward for direct imports.

Test signals: no local tests; coverage is distributed across submodules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/state.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/state.rs

Purpose: defines per-target TLS reload runtime state, immutable published state, watched input paths, and an admin/debug status snapshot.

Important APIs/types/functions: `TargetTlsInputSet` records CA path, client cert path, client key path, and `target_label`; `is_empty` detects no TLS paths. `TargetTlsPublishedState<M>` contains generation, fingerprint, material `Arc<M>`, and load timestamp. `TargetTlsRuntimeState<M>` owns `current` and `last_good` `ArcSwap`s, atomic attempt/success timestamps, `last_error`, and inputs. It exposes `new`, `current_generation`, `bump_generation`, `mark_attempt`, `mark_success`, and timestamp accessors. `TargetTlsStatusSnapshot` is serde-serializable for observability.

Control flow and state: `current` is the hot-path material pointer. `last_good` is updated only after successful publish and is intentionally preserved on failed reloads. Timestamp atomics use acquire/release ordering; error text uses `parking_lot::RwLock`.

Dependencies and integration points: used by adapter and coordinator. `ArcSwap` enables cheap, lock-free reads of current material by send paths.

Risks: `bump_generation` computes from the currently loaded generation but does not publish atomically with compare-and-swap; concurrent reload publishers could select the same generation if not externally serialized. The status snapshot includes file paths, which is useful operationally but may expose local paths through admin APIs.

Test signals: tests live in the coordinator module for state mutation semantics; shared runtime state has its own direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/trait.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/trait.rs

Purpose: defines `ReloadableTargetTls`, the protocol a TLS-capable notification target must implement to participate in coordinated certificate hot reload.

Important APIs/types/functions: associated type `Material` is the rebuilt client/pool/connector object. `tls_input_set` declares watched TLS files. `build_tls_material` constructs a fresh material object from disk. `apply_tls_material(generation, material, mode)` atomically replaces the target's active state and must preserve old state on error. `validate_tls_files` is an optional async pre-check with a default no-op.

Control flow and state: the trait itself is stateless; it encodes the two-phase reload contract: build new material off the send path, apply it atomically, and let the coordinator publish only after apply succeeds.

Dependencies and integration points: depends on `TargetError`, `async_trait`, `Arc`, target generation, apply mode, and input set. Implemented by target types such as AMQP, SQL, webhook, or other outbound clients.

Risks: correctness depends heavily on implementors honoring the atomic apply contract. The coordinator cannot verify that a failed `apply_tls_material` left old state intact. `validate_tls_files` is optional, so target-specific validation gaps can remain.

Test signals: fake/mock implementations in adapter and coordinator tests validate expected call ordering and failure handling from the coordinator side.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/trait.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/validate.rs -->
## sources/object-store/rustfs/crates/targets/src/runtime/tls/validate.rs

Purpose: provides target-side validation helpers for CA files and client certificate/key pairs before rebuilding target TLS material.

Important APIs/types/functions: `validate_cert_key_pairing(cert_path, key_path)` allows both paths empty, rejects only-one-present, and uses `rustfs_tls_runtime::load_certs` plus `load_private_key` to parse both files. `validate_ca_file(ca_path)` allows empty CA and parses non-empty paths. `validate_tls_material(ca_path, cert_path, key_path)` composes both checks.

Control flow and state: pure synchronous validation with no persistent state. All parse failures are converted into `TargetError::Configuration` messages that name the invalid path.

Dependencies and integration points: called by `reload_target_once` before target-specific validation and material construction. It reuses shared TLS runtime PEM parsing, keeping target validation aligned with server/global TLS parsing.

Risks: validates parseability and presence pairing, but not semantic certificate/key matching, expiration, CA trust policy, or hostname constraints. Synchronous filesystem reads in shared helpers occur inside the async coordinator path and may briefly block a Tokio worker.

Test signals: no direct tests in this file; coordinator tests exercise empty-path success and target-specific validation failure. Certificate parse failure coverage appears in `tls-runtime` cert tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/runtime/tls/validate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/store.rs -->
## sources/object-store/rustfs/crates/targets/src/store.rs

Purpose: implements a filesystem-backed queue store used by notification targets to persist events or raw payloads for retry/replay. It supports single entries, concatenated JSON batches, raw bytes, optional Snappy compression, entry limits, oldest-first listing, and deletion.

Important APIs/types/functions: `Key` encodes UUID name, file extension, batch `item_count`, and compression flag into filenames like `3:<uuid>.json.snap`. `parse_key` reverses filenames into keys. `ensure_store_entry_raw_readable` probes a key and deletes unreadable entries except `NotFound`. `Store<T>` defines open/put/put_multiple/put_raw/get/get_multiple/get_raw/del/delete/list/len/is_empty/boxed_clone. `QueueStore<T>` implements the trait with `entries: RwLock<HashMap<String, i64>>`, `pending_entries: AtomicU64`, and `fs_guard`.

Control flow and state: `open` creates the directory, scans files, indexes modified times, and resets pending reservations. `put`, `put_multiple`, and `put_raw` acquire a filesystem read guard, reserve an entry slot by comparing `entries.len + pending_entries` with the limit, write bytes, then index the key. `EntryReservation` decrements pending on drop. Reads optionally decompress based on key metadata. `list` sorts indexed keys by modified time to support oldest-first replay. `delete` removes the directory and clears state.

Dependencies and integration points: depends on `rustfs_config` defaults/env (`ENV_TARGET_STORE_COMPRESS`), serde JSON, `snap`, UUIDs, tracing, and `StoreError`. Targets use it for durable at-least-once delivery queues.

Risks: `write_file` writes directly to the final path, so process crash during write can leave an empty/partial file that later reads as `NotFound` or deserialization failure. `put_multiple` stores concatenated JSON objects rather than a JSON array; `get_multiple` uses a stream deserializer and warns on partial batches, which is a fragile format. `entries` is only in-memory and must be rebuilt with `open`; callers must open before use. Compression choice is encoded in keys, so wrong key parsing breaks reads.

Test signals: unit tests cover compression env defaults, key compression flag, key round trip, raw byte round trip with compression, store deletion, entry limit enforcement, and concurrent `put_raw` respecting the limit.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/sys/mod.rs -->
## sources/object-store/rustfs/crates/targets/src/sys/mod.rs

Purpose: declares the `sys` module namespace for target system utilities.

Important APIs/types/functions: exposes `pub mod user_agent;`.

Control flow and state: none.

Dependencies and integration points: lets callers import `crate::sys::user_agent` and keeps system utility files under one module boundary.

Risks: no direct behavior. Any public API stability resides in child modules.

Test signals: none here; child module tests cover actual behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/sys/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/sys/user_agent.rs -->
## sources/object-store/rustfs/crates/targets/src/sys/user_agent.rs

Purpose: constructs RustFS User-Agent strings that include platform, architecture, product version, and optional service type.

Important APIs/types/functions: `ServiceType` enumerates `Basis`, `Core`, `Event`, `Logger`, and `Custom(Cow<'static, str>)`. Internal `UserAgent` stores `os_platform`, `arch`, `version`, and service. `get_user_agent(service)` creates and formats the string as `Mozilla/5.0 (<platform>; <arch>) RustFS/<VERSION>` plus `(<service>)` for non-basis services.

Control flow and state: `OS_PLATFORM: OnceLock<String>` computes the platform once. OS-specific helpers use `sysinfo::System` for Windows/macOS/Linux, and fixed strings for BSD variants. The cached string is returned as `&'static str`.

Dependencies and integration points: depends on `rustfs_config::VERSION`, `std::env::consts::ARCH`, `OnceLock`, `Cow`, and `sysinfo` except OpenBSD. HTTP clients in target implementations can use this to identify service traffic.

Risks: platform detection is cached forever, which is correct for normal runtime but hard to override in tests. On unknown OSes it reports `Unknown`. Some OS helpers are compiled as `N/A` on other platforms and only selected by `cfg!`.

Test signals: tests verify basis omits `(basis)`, core/custom include service suffixes, version is present, and cached platform pointers are reused.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/src/sys/user_agent.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/tests/amqp_integration.rs -->
## sources/object-store/rustfs/crates/targets/tests/amqp_integration.rs

Purpose: ignored integration tests for the AMQP notification target against a RabbitMQ-compatible AMQP 0-9-1 broker.

Important APIs/types/functions: `broker_url` reads `RUSTFS_TEST_AMQP_URL` or defaults to localhost RabbitMQ. `test_args` builds `AMQPArgs` with `amq.topic`, mandatory persistent delivery, empty TLS paths, optional queue settings, and `TargetType::NotifyEvent`. `entity_for` builds event payloads. `bind_queue` declares and binds an exclusive auto-delete queue. `read_one` polls `basic_get` with a 5 second timeout and ACKs the message.

Control flow and state: tests create unique routing keys and queues with UUIDs. Direct publish constructs `AMQPTarget` and calls `save`, then verifies JSON payload and AMQP properties. Reconnect test publishes, closes cached connection, and publishes again. Queue replay test configures `queue_dir`, verifies one queued entry, calls `send_from_store`, verifies delivery, and confirms queue length returns to zero.

Dependencies and integration points: exercises `lapin`, `rustfs_targets::Target`, `check_amqp_broker_available`, `AMQPTarget`, queue store integration, and S3 event shape.

Risks: all tests except none are ignored because they require an external broker. Queue cleanup is manual best-effort. These tests assume default broker exchange behavior and may be sensitive to RabbitMQ availability/timing.

Test signals: provides strong behavioral expectations for broker probing, payload format, persistence flag/content type, reconnect after close, and queue replay deletion, but it is not part of default CI due to `#[ignore]`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/tests/amqp_integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/tests/mysql_integration.rs -->
## sources/object-store/rustfs/crates/targets/tests/mysql_integration.rs

Purpose: ignored integration tests for the MySQL/TiDB notification target, covering direct writes, queue replay, duplicate replay semantics, schema validation, and connectivity probing.

Important APIs/types/functions: `test_dsn` requires `RUSTFS_TEST_MYSQL_DSN`. `table_name` creates short UUID-suffixed table names. `make_args` builds `MySqlArgs` with empty TLS paths, queue limit, format `access`, and max open connections. `make_entity` constructs event entities. `build_test_pool` parses `MySqlDsn`, configures `mysql_async::OptsBuilder`, and installs the rustls aws-lc provider when TLS is requested. `drop_table` cleans up.

Control flow and state: direct write initializes target/table, saves one event, and verifies one row with bucket data. Delete test verifies PUT and DELETE events append separate rows. Queue test saves to store before init, verifies zero DB rows before replay, replays store keys, and checks queue empty. Duplicate replay decodes `QueuedPayload`, sends raw payload twice with the same key metadata, and expects duplicate rows, documenting MySQL at-least-once behavior. Incompatible schema test expects `TargetError::Initialization`. Connectivity test succeeds against an existing compatible table.

Dependencies and integration points: exercises `mysql_async`, target queue store, `QueuedPayload`, MySQL DSN parsing, SQL schema initialization, and `check_mysql_server_available`.

Risks: ignored tests require external MySQL/TiDB and manual setup. Duplicate replay intentionally produces duplicates, so consumers need downstream idempotency if required. Table identifiers are generated but SQL formatting still relies on target-side validation.

Test signals: strong documentation for MySQL target delivery semantics; not run by default CI.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/tests/mysql_integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/tests/postgres_integration.rs -->
## sources/object-store/rustfs/crates/targets/tests/postgres_integration.rs

Purpose: integration tests for the PostgreSQL notification target. Most tests are ignored because they require a running PostgreSQL server; one identifier validation test runs without a database.

Important APIs/types/functions: `test_args` builds `PostgresArgs` from `RUSTFS_TEST_PG_DSN` or a localhost default and copies schema parsed by `PostgresDsn`. `with_search_path` rewrites DSN query parameters. `raw_client` opens a `tokio_postgres` client with `NoTls` and spawns the connection future. `unique_table` and `entity_for` provide isolation helpers.

Control flow and state: probe tests verify an existing table succeeds and a missing table fails. Namespace format creates a key/value table and asserts two saves for the same key collapse via upsert. Access format creates an append table and asserts distinct events create two rows. Replay idempotency is simulated with direct SQL using `ON CONFLICT (event_id) DO NOTHING`. Init succeeds against an existing namespace table. The non-ignored malicious table name test verifies construction rejects unsafe identifiers.

Dependencies and integration points: exercises `PostgresTarget`, `PostgresDsn`, `PostgresFormat`, `check_postgres_server_available`, `tokio_postgres`, URL manipulation, and serde JSON event payloads.

Risks: database tests are ignored by default and depend on manual environment. `raw_client` uses `NoTls`, while target TLS behavior is not covered here. Dynamic SQL uses quoted generated identifiers; identifier validation is critical and directly tested for malicious input.

Test signals: documents namespace upsert semantics, access append semantics, access replay idempotency via event id conflict, connectivity errors, init behavior, and identifier validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/targets/tests/postgres_integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/Cargo.toml -->
## sources/object-store/rustfs/crates/tls-runtime/Cargo.toml

Purpose: declares the `rustfs-tls-runtime` crate, described as the project-wide TLS runtime foundation for RustFS.

Important APIs/types/functions: package metadata uses workspace version/edition/license/repository/rust-version/homepage, disables doctests for the library, and opts into workspace lints. Keywords and categories classify it as TLS/hot-reload/network-programming infrastructure.

Control flow and state: no runtime behavior, but dependencies shape the crate: `arc-swap` for atomic published state, `metrics`, `rustls` and `rustls-pki-types`, `serde`, `sha2`, `thiserror`, `tokio` with fs/rt/sync/time, and `tracing`.

Dependencies and integration points: consumed by `rustfs-targets` and likely server/global TLS initialization. Dev dependencies `rcgen`, `serde_json`, `tempfile`, and Tokio macros support local unit tests for certificates, status JSON, and async coordination.

Risks: choosing `aws_lc_rs` rustls crypto in code means runtime crypto-provider assumptions must match workspace rustls configuration. Disabling doctests avoids doc examples failing but also means public examples are not validated.

Test signals: this manifest enables focused unit tests across the crate but no integration tests are declared here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/certs.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/certs.rs

Purpose: centralizes certificate/key loading, mTLS client verifier construction, certificate directory inspection, multi-domain certificate discovery, and rustls SNI resolver creation.

Important APIs/types/functions: `CertDirectoryLoadOptions` and builder define directory plus cert/key filenames. `WebPkiClientVerifierOptions` and builder configure optional mTLS verification and fallback CA filenames. `load_certs`, `load_cert_bundle_der_bytes`, and `load_private_key` parse PEM files. `build_webpki_client_verifier` builds a rustls `WebPkiClientVerifier` from client CA bundle when enabled. `TlsCertPairStatus`, `TlsCertPairInspection`, `TlsDomainInspection`, and `TlsDirectoryInspection` model inspection results. `inspect_cert_directory` reports root/domain cert status. `load_all_certs_from_directory` loads root default cert and valid domain certs. `create_multi_cert_resolver` builds an SNI resolver with default fallback.

Control flow and state: directory scanning skips non-directories and hidden/Kubernetes projection-style directories beginning with `.`. Domain pairs are sorted for stable inspection. Loading warns and skips invalid root/domain pairs, but returns `NotFound` if no valid pair exists. Resolver construction maps `"default"` to fallback and other domain names into rustls SNI.

Dependencies and integration points: used by server TLS material loading, target TLS validation, reloadable server cert resolver, and mTLS server verifier setup. Depends on rustls, rustls-pki-types PEM readers, filesystem IO, tracing, and `RootCertStore`.

Risks: many operations are synchronous filesystem reads/parses. `create_multi_cert_resolver` requires private keys supported by the configured rustls crypto provider. Inspection validates parseability but not certificate expiration or hostname correctness. Hidden directory skipping is important for Kubernetes secrets; changing it could accidentally load projection internals.

Test signals: tests cover error construction, missing cert/key file errors, empty directory failure, skipping Kubernetes projection dirs, valid root/domain inspection, and invalid/missing pair reporting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/certs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/config.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/config.rs

Purpose: defines shared TLS reload options and enum knobs for the foundation runtime and target adapters.

Important APIs/types/functions: `ReloadDetectMode::{Poll, Watch, Hybrid}` models detection strategy; watch and hybrid are marked TODO for fs-watch implementation. `ReloadApplyHint::{Lazy, SoftReconnect}` tells consumers how aggressively to apply new material. `TlsReloadOptions` contains `enabled`, `detect_mode`, `interval`, `debounce`, `min_stable_age`, and `apply_hint`. `Default` enables poll reload every 15 seconds, 2 second debounce, 1 second min stable age, and lazy apply.

Control flow and state: no mutable state. Options are copied/cloned into coordinators and adapters.

Dependencies and integration points: imported directly by `rustfs-tls-runtime` and re-exported/aliased by target TLS config. Runtime coordinators currently implement polling; watch/hybrid naming is present before full watch behavior.

Risks: fields `debounce` and `min_stable_age` are not uniformly enforced across all reload paths; target coordinator uses debounce and shared foundation coordinator currently uses interval only. Watch mode skips target poll loop even though fs-watch is TODO, so consumers choosing Watch may get no automatic reload.

Test signals: no local tests; defaults are used in coordinator/server tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/coordinator.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/coordinator.rs

Purpose: implements the shared TLS reload coordinator for foundation TLS material snapshots. It loads TLS material from a `TlsSource`, publishes initial state, detects changed fingerprints, notifies a consumer, updates runtime state, and can spawn a polling loop.

Important APIs/types/functions: `TlsConsumer<M>` requires `on_publish(generation, state)`. `TlsReloadCoordinator` stores `source` and `options`, exposes accessors, `status_snapshot`, `load_initial_snapshot`, `publish_initial_state`, `reload_once`, and `spawn_poll_loop`.

Control flow and state: `publish_initial_state` wraps a snapshot as generation 1 and records generation metrics. `reload_once` marks attempt time, reloads a fresh `TlsMaterialSnapshot`, skips unchanged fingerprints, creates a new `TlsPublishedState` with bumped generation, calls `consumer.on_publish`, then stores to `current` and `last_good`, marks success, clears `last_error`, and records metrics. If consumer publication fails, state is not updated and a publication-fail metric is emitted. `spawn_poll_loop` returns `None` when disabled or non-poll mode, otherwise ticks forever and records last error on failure.

Dependencies and integration points: used by global TLS runtime initialization and consumers that need snapshot updates. Depends on `TlsMaterialSnapshot`, `TlsReloadRuntimeState`, `TlsSource`, metrics, Tokio tasks/time, and tracing.

Risks: poll loop has no shutdown channel; task lifetime is external handle abortion/drop policy. `reload_once` loads material before comparing fingerprints, which is simple but can be expensive for large cert directories. `debounce` and `min_stable_age` options are not applied here.

Test signals: unit test verifies unchanged fingerprint reload returns `Ok(None)`. Crate-level tests verify initial state publication generation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/coordinator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/debug.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/debug.rs

Purpose: defines serializable debug/status response structures for TLS runtime observability.

Important APIs/types/functions: `TlsConsumerStatusItem` records a consumer name, generation, root CA presence, and mTLS identity presence. `TlsDebugStatusResponse` contains a foundation `TlsRuntimeStatusSnapshot` plus consumer status items. `TlsDebugStatusResponse::builder` creates `TlsDebugStatusResponseBuilder`; `push_consumers` appends iterable consumer status entries; `build` returns the response.

Control flow and state: builder is immutable-by-value and only accumulates a vector before build. No global state.

Dependencies and integration points: depends on serde and `TlsRuntimeStatusSnapshot`. Intended for admin/debug endpoints that combine foundation runtime and consumer-specific status.

Risks: `consumer` is `&'static str`, so dynamic consumer labels require static identifiers or a type change. The response reports presence booleans rather than detailed certificate metadata, which is safer but less diagnostic.

Test signals: unit test serializes a built response to JSON and verifies `foundation` and array `consumers` fields exist.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/debug.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/error.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/error.rs

Purpose: defines the shared error type for TLS runtime operations.

Important APIs/types/functions: `TlsRuntimeError` variants cover empty source path, missing directory, non-directory path, material errors, publication errors, and wrapped IO errors. `thiserror::Error` supplies display messages and source handling for IO.

Control flow and state: no state; errors are constructed by source validation, material loading, and coordinator/consumer publication paths.

Dependencies and integration points: used across `source`, `material`, `coordinator`, and server resolver code. Target TLS validation converts lower-level parsing errors into `TargetError` instead of this type, but shared runtime paths use it directly.

Risks: `Material(String)` and `Publication(String)` are flexible but lose structured detail. Directory errors include full local paths, which is useful for operators but may need care in externally exposed APIs.

Test signals: source validation tests assert `DirectoryNotFound`; other variants are exercised indirectly by cert/material tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/fingerprint.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/fingerprint.rs

Purpose: provides the shared SHA256 fingerprint structure used to detect TLS material changes across server, outbound CA, client CA, and mTLS identity inputs.

Important APIs/types/functions: `TlsFingerprint` contains optional digests for `server_sha256`, `public_ca_sha256`, `client_ca_sha256`, `client_cert_sha256`, and `client_key_sha256`. `from_optional_bytes` digests each supplied byte slice and leaves absent inputs as `None`. Private `digest_bytes` wraps `sha2::Sha256`.

Control flow and state: pure deterministic hashing with no IO and no mutable state.

Dependencies and integration points: used by `TlsMaterialSnapshot`, target TLS fingerprint helper, server resolver fingerprinting, and reload coordinators for equality checks.

Risks: fingerprints include private key bytes for change detection; they are only digests, but code paths handling them should still avoid leaking debug representations unnecessarily. Domain ordering must be stabilized before hashing multi-cert material, which `material` and `server` handle explicitly.

Test signals: crate-level tests verify fingerprint changes when server material changes; server resolver tests verify stable fingerprints across domain ordering.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/fingerprint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/lib.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/lib.rs

Purpose: defines the public API surface of the `rustfs-tls-runtime` crate by declaring modules and re-exporting TLS certificate, config, reload, debug, material, metrics, outbound, server, source, and state types.

Important APIs/types/functions: public re-exports include certificate loaders/inspectors/resolvers, reload options, `TlsReloadCoordinator`, `TlsConsumer`, debug response builders, `TlsRuntimeError`, `TlsFingerprint`, `TlsMaterialSnapshot`, metrics helpers, global outbound TLS state helpers, `ReloadableServerCertResolver`, `spawn_server_cert_reload_loop`, `TlsSource`, and runtime state/status structs.

Control flow and state: no runtime behavior beyond tests; it establishes stable import paths for downstream crates like `rustfs-targets`.

Dependencies and integration points: all crate modules are public. The targets crate imports config, fingerprint, cert loaders, and validation-related helpers through this crate.

Risks: broad re-exporting makes internal module changes observable to downstream users. The test module constructs simplified material snapshots, so it validates API wiring more than full certificate lifecycle.

Test signals: tests verify missing TLS source directories fail, server material fingerprint changes when certificate/key material changes, and the coordinator publishes initial generation 1.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/material.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/material.rs

Purpose: loads complete TLS material snapshots from a `TlsSource`, combining server certificate material, outbound root CA bundle, optional client mTLS identity, and a fingerprint that covers all loaded inputs.

Important APIs/types/functions: `OutboundTlsMaterial` stores combined root CA PEM and optional `MtlsIdentityPem`. `ServerTlsMaterial` is either `SingleCert` or `MultiCert` with domain-to-cert/key pairs. `TlsMaterialSnapshot::load(source)` validates the source directory, loads server material, reads public CA and fallback/client CA files, validates client cert/key PEM when both exist, and computes `TlsFingerprint`. Helpers include `load_server_material`, `combine_optional_pem`, and deterministic `serialize_server_material_for_fingerprint`.

Control flow and state: server loading first attempts directory discovery. Multi-cert is selected when more than one cert or any non-default domain exists; a single default cert becomes `SingleCert`; no certs becomes `None`. Public CA and fallback CA PEM are concatenated with newline normalization. Client mTLS identity is present only when both client cert and key files can be read and parsed.

Dependencies and integration points: used by the shared coordinator, outbound global publisher, server resolver, and debug status. Depends on certificate loading helpers, `rustfs_common::MtlsIdentityPem`, rustls PKI types, Tokio file reads, and SHA fingerprints.

Risks: partial client identity files are silently treated as absent unless both reads succeed, except parse errors after both are present; this may hide a missing key/cert misconfiguration. Private key bytes are included in fingerprint input. Server material loading can downgrade some discovery failures to single-root loading or none depending on error kind.

Test signals: covered indirectly by coordinator/server/certs/lib tests. Direct tests for CA bundle concatenation and partial mTLS absence would improve confidence.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/material.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/metrics.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/metrics.rs

Purpose: declares shared TLS runtime metrics for global outbound publication, reload attempts, generations, skipped reloads, publication failures, and stale consumer generations.

Important APIs/types/functions: constants identify foundation and outbound consumers. `record_outbound_tls_publication` records publication count and gauges root/mTLS presence. `record_tls_generation`, `record_tls_reload_result`, `record_tls_reload_skipped`, `record_tls_publication_fail`, and `record_tls_consumer_stale_generation` update generic TLS metrics. `init_tls_metrics` registers descriptions for counters, gauges, and histogram.

Control flow and state: no local state; all effects go through `metrics` macros. `record_tls_reload_result` optionally records duration and generation, allowing callers with partial information such as server resolver reloads.

Dependencies and integration points: used by shared coordinator, outbound publisher, and reloadable server resolver. Labels use static `consumer`, `result`, and `reason` values.

Risks: using static consumer labels avoids cardinality problems, but downstream callers should not pass unbounded dynamic strings. Publication failure metrics do not include error classification.

Test signals: no direct tests. Runtime correctness depends on exercising reload paths and metrics backend integration.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/outbound.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/outbound.rs

Purpose: publishes and reads global outbound TLS root CA and mTLS identity state used by outbound clients.

Important APIs/types/functions: `GlobalPublishedOutboundTlsState` captures generation, optional root CA PEM, and optional mTLS identity. `GlobalOutboundTlsStateSummary` exposes generation and presence booleans. `publish_global_outbound_tls_state(generation, material)` writes `GLOBAL_ROOT_CERT`, `GLOBAL_MTLS_IDENTITY`, and global generation. `load_global_outbound_tls_state`, `load_global_outbound_tls_generation`, and `summarize_global_outbound_tls_state` read back state.

Control flow and state: publishing clears global root cert when material has no root CA bytes, always updates mTLS identity, then sets generation and metrics. Reads acquire async global locks from `rustfs_common`.

Dependencies and integration points: integrates `TlsMaterialSnapshot` outbound material with global process-level TLS configuration consumed by outbound HTTP/database/etc. clients. Depends on `rustfs_common` global TLS storage and metrics.

Risks: process-global mutable TLS state means all outbound consumers share the same roots/identity. Callers must coordinate publication order; there is no compare-and-swap against generation. Clearing root CA on empty material is explicit and can affect all clients.

Test signals: no direct tests in this file; debug/status and coordinator tests cover related generation handling indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/outbound.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/server.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/server.rs

Purpose: implements a reloadable rustls server certificate resolver that can serve SNI-specific certificates, fall back to a default certificate, and reload material from a TLS source directory on a poll loop.

Important APIs/types/functions: private `ResolverState` holds `ResolvesServerCertUsingSni`, optional default `CertifiedKey`, cert count, and fingerprint. `ReloadableServerCertResolver` owns `TlsSource`, current resolver state behind `std::sync::RwLock`, and an atomic generation. `load_from_source`/`load_from_directory` build initial state. `reload` reloads certs, compares fingerprints, swaps resolver state, and increments generation. It implements rustls `ResolvesServerCert`. `spawn_server_cert_reload_loop(protocol, resolver, options, shutdown_rx)` polls reload until a watch shutdown signal.

Control flow and state: domain entries are sorted before fingerprinting and resolver construction. `reload` handles poisoned locks by taking the inner value and still proceeding. The server resolver's `resolve` method performs a read lock and tries SNI first, then default cert.

Dependencies and integration points: uses cert directory loading, `TlsReloadOptions`, metrics, rustls server traits/signing, Tokio watch/time, and tracing. Intended for HTTP/S3/admin server TLS hot reload.

Risks: synchronous reload and resolver-state construction happen inside async poll task. Generation uses relaxed atomics and `fetch_add` without saturation. `spawn_server_cert_reload_loop` ignores detect mode and starts whenever enabled, unlike the foundation coordinator. Resolver reload failure keeps old state but only logs/metrics the error.

Test signals: tests verify default cert replacement after file rotation, unchanged reload skip, and stable fingerprint across domain ordering.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/source.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/source.rs

Purpose: models where TLS material is loaded from and the expected filenames/layout inside a TLS directory.

Important APIs/types/functions: `TlsSourceKind::{Directory, ExplicitFiles}` reserves source strategies; current constructor is `TlsSource::from_directory`. `TlsFileLayout` names server cert/key, public CA, client CA, client cert, and client key filenames using `rustfs_config` constants by default. `TlsSource` stores kind, base directory, layout, fallback CA filename, trust flags, and server mTLS enablement. `validate_directory` rejects empty, missing, and non-directory paths.

Control flow and state: construction sets directory mode, default filenames, fallback CA as `RUSTFS_CA_CERT`, and trust/mTLS flags false. Validation only checks filesystem path shape; it does not inspect files.

Dependencies and integration points: consumed by material loading, coordinator status, and reloadable server resolver. It is the root of all shared TLS runtime file discovery.

Risks: `ExplicitFiles` is declared but no constructor/validation behavior exists here, so callers should not assume explicit-file mode is implemented. Trust flags are stored but not acted on in the visible material loading path. Validation uses live filesystem checks.

Test signals: crate-level test verifies missing directory produces `TlsRuntimeError::DirectoryNotFound`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/source.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/state.rs -->
## sources/object-store/rustfs/crates/tls-runtime/src/state.rs

Purpose: defines shared TLS runtime generation, published state, atomic runtime state, and serializable status snapshot structures.

Important APIs/types/functions: `TlsGeneration(pub u64)`, `TlsPublishedState<M>` with generation/material/fingerprint/load time, and `TlsReloadRuntimeState<M>` with `current`, `last_good`, attempt/success atomics, and async `last_error`. Methods include `new`, `current_generation`, `bump_generation`, `mark_attempt`, `mark_success`, and timestamp getters. `TlsRuntimeStatusSnapshot` groups runtime, outbound, server, and consumer sections; `from_outbound_only` builds a reduced status; `is_complete` reports whether any server/outbound material exists. `detect_mode_label` maps enum to static strings.

Control flow and state: `ArcSwap` gives lock-free reads of current and last-good states. `bump_generation` saturates at `u64::MAX`. Timestamp atomics use relaxed ordering in this shared state. `last_error` is an async `tokio::sync::RwLock`.

Dependencies and integration points: used by shared coordinator, debug responses, outbound-only status, and tests. Serde derives make status snapshots admin/API friendly.

Risks: relaxed atomics are likely fine for observability timestamps but not synchronization. Like target state, generation bump is separate from publication and assumes one publisher at a time. Status exposes source paths and only coarse material booleans.

Test signals: tests cover generation/timestamp tracking, generation saturation, status completeness when roots exist, and incompleteness when empty.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/tls-runtime/src/state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/Cargo.toml -->
## sources/object-store/rustfs/crates/trusted-proxies/Cargo.toml

Purpose: declares the `rustfs-trusted-proxies` crate, which manages trusted proxy detection/ranges and middleware-related network security behavior.

Important APIs/types/functions: package metadata uses workspace versioning and lints, disables doctests, and declares two test targets: `unit_tests` at `tests/unit/mod.rs` and `integration_tests` at `tests/integration/mod.rs`.

Control flow and state: no runtime code. Dependencies include `async-trait`, `axum`, `http`, `ipnetwork`, `metrics`, `moka`, `reqwest`, `rustfs-config`, `rustfs-utils` net feature, serde, `thiserror`, Tokio, Tower, tracing, and regex. Dev dependencies add full Tokio/Tower utilities, `serial_test`, and `temp-env`.

Dependencies and integration points: cloud detector and metadata files depend on `reqwest`, `ipnetwork`, `async-trait`, Tokio, tracing, environment helpers, and app error types from this crate.

Risks: network metadata fetching depends on external cloud endpoints and public range JSON formats. `moka` cache and middleware dependencies indicate shared state/cache behavior elsewhere in the crate, not visible in this file.

Test signals: explicit unit and integration test targets suggest broader coverage outside this subset.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/detector.rs -->
## sources/object-store/rustfs/crates/trusted-proxies/src/cloud/detector.rs

Purpose: detects the current cloud provider and fetches trusted proxy CIDR ranges from provider-specific metadata/range fetchers.

Important APIs/types/functions: `CloudProvider` supports AWS, Azure, GCP, DigitalOcean, Cloudflare, and `Unknown(String)`, with `FromStr`, `detect_from_env`, and `name`. `CloudMetadataFetcher` defines provider name, network CIDR fetch, public IP range fetch, and a default `fetch_trusted_proxy_ranges` that degrades independently on each dataset. `CloudDetector` stores enabled flag, timeout, and optional forced provider; methods include `new`, `detect_provider`, `fetch_trusted_ranges`, and `try_all_providers`. `default_cloud_detector` disables detection.

Control flow and state: provider detection is disabled-first, then forced-provider, then environment markers. Fetching dispatches to AWS/Azure/GCP metadata fetchers, Cloudflare/DigitalOcean range fetchers, or returns empty for unknown/none. `try_all_providers` sequentially tries AWS, Azure, and GCP until a non-empty result.

Dependencies and integration points: integrates with `AwsMetadataFetcher`, `AzureMetadataFetcher`, `GcpMetadataFetcher`, `CloudflareIpRanges`, and `DigitalOceanIpRanges`. Uses `rustfs_utils::get_env_opt_str`, `ipnetwork`, tracing, and crate `AppError`.

Risks: environment detection uses `RUSTFS_`-prefixed markers rather than raw cloud provider env names, so deployment adapters must set those markers. The default trait method returns `Ok` with partial data when one fetch fails, which is robust but can silently broaden/narrow trust depending on fallback behavior. Forced unknown providers return empty without error.

Test signals: tests cover AWS env detection preference and no-marker returning `None`. Fetch behavior relies on provider-specific tests elsewhere or integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/detector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/aws.rs -->
## sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/aws.rs

Purpose: implements AWS-specific metadata and public range fetching for trusted proxy CIDRs.

Important APIs/types/functions: `AwsMetadataFetcher` holds a `reqwest::Client` and IMDS endpoint. `new(timeout)` builds a timeout client and defaults endpoint to `http://169.254.169.254`. Private `get_metadata_token` obtains an IMDSv2 token but is currently marked dead code. The `CloudMetadataFetcher` impl returns provider name `aws`, default VPC private ranges from `fetch_network_cidrs`, and downloads/parses `https://ip-ranges.amazonaws.com/ip-ranges.json` in `fetch_public_ip_ranges`, filtering services `EC2` and `CLOUDFRONT`.

Control flow and state: network CIDRs are hardcoded fallback ranges `10/8`, `172.16/12`, and `192.168/16`. Public range fetch returns parsed networks on success, but returns an empty vector for HTTP or request errors instead of propagating.

Dependencies and integration points: called by `CloudDetector` when AWS is detected or in `try_all_providers`. Depends on `reqwest`, serde JSON structs, `ipnetwork::IpNetwork::from_str`, tracing, and `AppError`.

Risks: IMDS token retrieval is unused, so no actual AWS instance metadata is queried for VPC/subnet data. Treating all EC2 and CloudFront public ranges as trusted proxies may be too broad for strict deployments. HTTP errors degrade to empty public ranges while private ranges are still included by the detector default combiner.

Test signals: no local tests in this file. Behavior is indirectly covered if cloud detector/provider tests exercise AWS fetcher with mocked network or default ranges.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/aws.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/azure.rs -->
## sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/azure.rs

Purpose: implements Azure metadata and public Service Tags fetching for trusted proxy CIDR discovery.

Important APIs/types/functions: `AzureMetadataFetcher` stores a timeout `reqwest::Client` and IMDS endpoint. `get_metadata(path)` calls Azure IMDS with `Metadata: true`. `fetch_azure_ip_ranges` downloads a hard-coded Microsoft Service Tags JSON URL, deserializes `values[].properties.address_prefixes`, and includes tags whose name contains `Azure` but not `ActiveDirectory`. `default_azure_ranges` and `default_azure_network_ranges` provide public and VNet fallback CIDRs. The `CloudMetadataFetcher` impl returns provider `azure`, fetches network CIDRs from IMDS `instance/network/interface`, and public ranges from `fetch_azure_ip_ranges`.

Control flow and state: IMDS network metadata is parsed into interface/subnet structs and converted from address plus prefix into CIDR strings. Empty or failed metadata falls back to private/reserved Azure network ranges. Public range request failure falls back to a large hardcoded IPv4/IPv6 range list; HTTP non-success returns empty public ranges.

Dependencies and integration points: called by `CloudDetector`; depends on reqwest, serde, `ipnetwork`, tracing, and `AppError`.

Risks: the Service Tags URL includes a date-specific filename (`ServiceTags_Public_20260126.json`), which will age and may disappear or become stale. Filtering tags by substring `Azure` is broad and may include more ranges than desired. Fallback public ranges are static and require maintenance. Metadata JSON shape assumptions must match Azure IMDS response exactly.

Test signals: no local tests in this file. Reliable coverage would require mocked IMDS/service-tag responses and fallback-path tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/azure.rs -->
