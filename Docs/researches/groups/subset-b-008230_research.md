# subset-b-008230 research

Grouped code research for RustFS config constants, notification keys, observability/OPA/server config model, credentials, and crypto helpers. Each section preserves the source path and is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/console.rs -->
# sources/object-store/rustfs/crates/config/src/constants/console.rs

## Purpose
Defines public environment names and defaults for S3 endpoint CORS, management console CORS, console enable/address settings, console rate limiting, console auth timeout, and update checks.

## Important APIs, types, and functions
`ENV_CORS_ALLOWED_ORIGINS` and `ENV_CONSOLE_CORS_ALLOWED_ORIGINS` distinguish S3 endpoint and console CORS policy. `DEFAULT_*_CORS_ALLOWED_ORIGINS` are intentionally empty. Console rate-limit knobs are `ENV_CONSOLE_RATE_LIMIT_ENABLE`, `ENV_CONSOLE_RATE_LIMIT_RPM`, and defaults `false`/`100`. `ENV_CONSOLE_AUTH_TIMEOUT` defaults to `3600` seconds, and `ENV_UPDATE_CHECK` defaults to `true`.

## Control flow
There is no runtime control flow beyond unit tests asserting the restrictive empty CORS defaults and stable env names.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Consumed by server/config loaders and console HTTP setup. It integrates with browser CORS behavior, rate-limit middleware, console session/auth handling, and update-check scheduling.

## Risks and edge cases
The security-sensitive behavior is that empty CORS means no generic cross-origin access; changing it to `*` would reopen broad browser access. Rate limiting defaults to off, so deployments expecting protection must opt in. Timeout values are only enforced if downstream parsing validates range comments.

## Test signals
Unit tests currently pin endpoint and console CORS env names/defaults. Broader signals should include browser CORS responses, console rate-limit activation, auth-session expiry, and update-check disablement.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/console.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/drive.rs -->
# sources/object-store/rustfs/crates/config/src/constants/drive.rs

## Purpose
Centralizes environment names and defaults for drive operation timeouts, active health probes, recovery thresholds, timeout-to-health policy, and timeout profile presets.

## Important APIs, types, and functions
Exports legacy `ENV_DRIVE_MAX_TIMEOUT_DURATION`, per-operation timeout keys for metadata, disk info, list-dir, walk-dir, and stall detection, plus active check interval/timeout keys. Health policy constants are `DRIVE_TIMEOUT_HEALTH_ACTION_MARK_FAILURE` and `DRIVE_TIMEOUT_HEALTH_ACTION_IGNORE_SCANNER`. Recovery tuning includes suspect failure, returning success, returning probe, offline grace, and long-offline thresholds. `RUSTFS_DRIVE_TIMEOUT_PROFILE=high_latency` maps to a 60-second preset.

## Control flow
No executable logic; downstream code reads these constants to choose timeouts and drive-state transitions.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with local/remote drive wrappers, scanner-sensitive walk/list paths, disk health state machines, and operator environment parsing.

## Risks and edge cases
Timeout defaults are short and can mark storage failed under high latency. The `ignore_scanner` policy changes health semantics for scanner workloads and must stay aligned with drive-state code. Legacy fallback plus per-operation overrides can create precedence ambiguity if parsers drift.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Drive-state tests should cover timeout classification, high-latency profile precedence, returning-drive thresholds, and scanner timeout policy.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/drive.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/env.rs -->
# sources/object-store/rustfs/crates/config/src/constants/env.rs

## Purpose
Defines shared configuration vocabulary and a permissive `EnableState` parser used by RustFS config/environment surfaces.

## Important APIs, types, and functions
Core constants include `ENV_PREFIX`, delimiters, default event/audit directories, global audit/notify switches, ILM process-time keys, `ENABLE_KEY`, and `COMMENT_KEY`. `EnableState` has variants for true/false, yes/no, on/off, enabled/disabled, ok/not_ok, success/failure, active/inactive, and 1/0. It implements `Display`, `FromStr`, `as_str`, `is_enabled`, and `is_disabled`.

## Control flow
`FromStr` trims input and performs case-insensitive matching for word values while handling `1` and `0` exactly. `is_enabled` and `is_disabled` classify every variant, with `Empty` treated as disabled.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
This module is re-exported by `config/src/lib.rs` under the `constants` feature and is consumed by notify/audit/server config code that needs uniform enable and comment keys.

## Risks and edge cases
The parser returns `Err(())` for unknown values, so callers need clear error handling. Treating empty as disabled is conservative but can surprise code that wants tri-state semantics. Adding variants requires keeping `as_str`, parsing, and classification in sync.

## Test signals
Unit tests pin all conversions, defaults, enabled/disabled classification, and audit/notify env names. Additional integration tests should ensure callers reject invalid enable strings consistently.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/env.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/heal.rs -->
# sources/object-store/rustfs/crates/config/src/constants/heal.rs

## Purpose
Defines the heal admin subsystem name, supported config keys, and environment/default values for automatic healing, heal queue behavior, concurrency, per-set bulkheads, page parallelism, and scanner-driven bitrot cycles.

## Important APIs, types, and functions
Exports `HEAL_SUB_SYS`, `HEAL_BITROT_CYCLE`, `HEAL_KEYS`, and `DEFAULT_HEAL_BITROT_CYCLE_SECS`. Runtime knobs include auto-heal enable, queue size, interval, task timeout, global/per-set concurrency, low-priority merge/drop behavior, page object concurrency, event-driven wakeups, set bulkheads, and page parallel enablement.

## Control flow
No code executes in this file. Heal managers and admin config parsers use the constants to configure queues, schedulers, and repair workers.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with heal queue admission, erasure-set repair schedulers, scanner bitrot/deep-scan configuration, and admin config storage.

## Risks and edge cases
Defaults enable auto-heal and event-driven scheduling, so misconfigured environments can increase repair load. Queue size and concurrency constants directly affect memory and disk pressure. Per-set concurrency must remain aligned with scheduler fairness assumptions.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Heal runtime tests should cover queue-full low-priority behavior, duplicate merge, per-set concurrency limits, and event-driven wakeups.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/heal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/health.rs -->
# sources/object-store/rustfs/crates/config/src/constants/health.rs

## Purpose
Defines health endpoint and readiness probe configuration names and defaults.

## Important APIs, types, and functions
`ENV_HEALTH_ENDPOINT_ENABLE` defaults public health/ready routes on. `ENV_HEALTH_READINESS_CACHE_TTL_MS` defaults readiness cache TTL to 1000 ms. Other flags control minimal response payloads, busy protection by active request count, and optional KMS readiness participation.

## Control flow
No local control flow; endpoint registration and readiness evaluation happen in HTTP/server layers that consume these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with HTTP route setup, storage readiness checks, request accounting, and optional KMS manager state.

## Risks and edge cases
Health endpoints default to enabled, which is useful for orchestration but exposes status unless deployment routing controls it. Readiness cache can hide rapid state changes for up to the configured TTL. Busy/KMS checks are opt-in and can change compatibility semantics for probes.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Health endpoint tests should assert route registration, 404 when disabled, readiness-cache TTL behavior, minimal payload mode, busy 429 behavior, and KMS gating.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/health.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/internode.rs -->
# sources/object-store/rustfs/crates/config/src/constants/internode.rs

## Purpose
Defines internode gRPC timeout, keepalive, request timeout, and data-plane transport backend constants.

## Important APIs, types, and functions
Exports connect timeout, TCP keepalive, HTTP/2 keepalive interval/timeout, RPC timeout env names and defaults, plus `ENV_RUSTFS_INTERNODE_DATA_TRANSPORT`, default backend `tcp-http`, legacy alias `tcp`, and `KNOWN_INTERNODE_DATA_TRANSPORT_BACKENDS`.

## Control flow
No runtime logic beyond tests that assert bounds and env-name stability.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Consumed by internode client/channel builders and transport selection code for distributed object-store communication.

## Risks and edge cases
Timeout defaults are low and may need high-latency tuning. The backend allow-list must stay synchronized with actual transport implementations; accepting a backend here that has no runtime implementation would fail later.

## Test signals
Unit tests pin default timeout values, env names, default transport, legacy alias, and known backend list. Integration tests should verify channel construction and request timeout behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/internode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/mod.rs -->
# sources/object-store/rustfs/crates/config/src/constants/mod.rs

## Purpose
Collects all config constant submodules under one internal module tree.

## Important APIs, types, and functions
Declares `pub(crate) mod` entries for app, body limits, capacity, compress, console, drive, env, heal, health, internode, object, oidc, profiler, protocols, proxy, quota, runtime, scanner, targets, tls, workload, and zero_copy.

## Control flow
No executable flow; Rust module resolution wires submodules for `lib.rs` feature-gated re-exports.

## State and persistence behavior
No runtime state. Its only persistence effect is compile-time module availability.

## Dependencies and integration points
Used by `config/src/lib.rs` when the `constants` feature is enabled.

## Risks and edge cases
Adding a constants file without registering it here prevents downstream re-export. Removing or renaming modules is a public API break for `rustfs-config` constant consumers.

## Test signals
Compilation with the `constants` feature is the primary signal. Public API checks should ensure expected modules remain reachable from the crate root.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/object.rs -->
# sources/object-store/rustfs/crates/config/src/constants/object.rs

## Purpose
Defines object read/write performance, timeout, buffering, lock, backpressure, priority scheduling, storage-media detection, and adaptive read-ahead environment constants.

## Important APIs, types, and functions
Important knobs cover high/medium concurrency thresholds, max disk reads, optional GetObject bitrot skip, fixed and dynamic GetObject/disk-read timeouts, duplex and I/O buffer sizes, lock optimization and diagnostics, deadlock detection, backpressure watermarks, I/O priority thresholds and queue capacities, starvation prevention, load sampling, storage media override/detection, access-pattern history, bandwidth EMA thresholds, media-specific buffer caps, and random read-ahead disablement.

## Control flow
No local control flow. Runtime object APIs consume these constants while calculating timeouts, buffer sizes, priority classes, lock diagnostics, and adaptive I/O behavior.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with S3 GetObject paths, erasure/disk reads, namespace lock managers, priority I/O schedulers, backpressure controllers, storage-media probes, and bitrot verification.

## Risks and edge cases
This file controls many performance and safety defaults; mismatches between comments and parser validation can create dangerous operator assumptions. Skipping bitrot verification is security/integrity-sensitive. Large buffers and queues can multiply memory use under concurrency. Deadlock diagnostics are off by default and must not become a hot-path cost unexpectedly.

## Test signals
Tests should cover timeout calculation bounds, priority classification and starvation promotion, lock diagnostic thresholds, bitrot verification toggles, storage-media overrides, and memory behavior under high concurrency.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/object.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/oidc.rs -->
# sources/object-store/rustfs/crates/config/src/constants/oidc.rs

## Purpose
Defines OpenID Connect admin KVS keys, environment names, valid-key arrays, defaults, and subsystem name.

## Important APIs, types, and functions
KVS keys include config URL, client id/secret, scopes, other audiences, redirect URI/static-dynamic controls, claim name/prefix, role policy, display name, groups/roles/email/username claims, and hide-from-UI. Env arrays `ENV_IDENTITY_OPENID_KEYS` and config-key array `IDENTITY_OPENID_KEYS` include enable/comment boundaries. Defaults set scopes to `openid,profile,email`, group claim to `groups`, roles claim empty, email `email`, username `preferred_username`, and subsystem `identity_openid`.

## Control flow
No executable flow; parser code elsewhere maps environment/config entries by these arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with identity provider configuration, console login, STS/IAM claim extraction, and admin config validation.

## Risks and edge cases
Client secret and auth-related keys are sensitive; downstream debug/UI code must respect hidden or redaction policy. The empty default roles claim preserves legacy behavior but may surprise deployments expecting role merging. Array lengths must stay consistent with element count.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. OIDC integration tests should validate default claims, hidden UI behavior, secret redaction, env override mapping, and config-key validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/oidc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/profiler.rs -->
# sources/object-store/rustfs/crates/config/src/constants/profiler.rs

## Purpose
Defines environment names and defaults for RustFS CPU and memory profiling controls.

## Important APIs, types, and functions
Exports global profiling enable, CPU mode/frequency/interval/duration keys, jemalloc memory periodic/interval keys, output directory key, and defaults: profiling disabled, CPU mode `off`, 100 Hz sampling, 300-second interval, 60-second duration, memory periodic disabled, output dir `.`.

## Control flow
No runtime logic; profiler initialization reads these constants and starts continuous/periodic profilers if enabled.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with CPU profiler, jemalloc memory profiling, filesystem output paths, and operator debugging workflows.

## Risks and edge cases
Profiling can create sensitive or large output files and add runtime overhead. Defaults are safe/off, but invalid mode strings must be rejected by downstream parser.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Profiler tests should cover disabled default, mode parsing, periodic scheduling, output directory validation, and memory profiler feature availability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/profiler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/protocols.rs -->
# sources/object-store/rustfs/crates/config/src/constants/protocols.rs

## Purpose
Defines FTP/FTPS, WebDAV, and SFTP protocol server environment keys and defaults, including TLS, host key, multipart upload, handle, backend timeout, and SFTP read-cache controls.

## Important APIs, types, and functions
Important constants include default FTP/FTPS/WebDAV/SFTP bind addresses, passive ports/external IP options, protocol enable/address/TLS/certs env keys, and SFTP host-key reload, idle timeout, part size, read-only, banner, handles-per-session, backend operation timeout, read cache window, and total cache memory keys. Defaults include SFTP idle timeout 600 seconds, host-key reload off, 16 MiB multipart part size, read-only false, and banner `SSH-2.0-RustFS`.

## Control flow
No executable control flow. Server startup and protocol adapters parse the env keys and enforce the documented bounds.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with FTP/FTPS/WebDAV/SFTP server crates, TLS certificate loading, S3 multipart uploads, SFTP handle accounting, backend object-store calls, and cache memory limiters.

## Risks and edge cases
SFTP host-key directory has no default, so enabling SFTP without explicit key configuration should fail clearly. Multipart part size constrains max single upload size through the 10,000-part S3 limit. Cache and handle defaults can multiply memory under many sessions. Bounds documented in comments must be enforced downstream.

## Test signals
Protocol startup tests should verify defaults, required host-key handling, SFTP part-size bounds, read-only behavior, per-session handle cap, backend timeout, and read-cache memory ceilings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/protocols.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/proxy.rs -->
# sources/object-store/rustfs/crates/config/src/constants/proxy.rs

## Purpose
Defines trusted reverse-proxy middleware configuration constants.

## Important APIs, types, and functions
Exports enable/implementation/validation mode/RFC7239/max-hop/chain-continuity/logging keys, default trusted private networks and extra IP/network lists, cache capacity/TTL/cleanup settings, metrics/log/tracing settings, and optional cloud metadata or Cloudflare IP integration keys.

## Control flow
No local logic. Proxy middleware and config loaders use these constants to parse headers and decide whether source addresses and forwarded chains are trusted.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with HTTP request identity extraction, `Forwarded`/`X-Forwarded-*` parsing, metrics, logging, tracing, cloud metadata discovery, and network CIDR parsing.

## Risks and edge cases
Trusted proxy is enabled by default and trusts common private networks; this is convenient behind internal load balancers but dangerous if exposed through untrusted private hops. Cloud metadata discovery is off by default because it can block or leak environment assumptions. Cache TTL affects reaction time to config changes.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Proxy tests should cover hop-by-hop validation, RFC7239 parsing, private-network trust boundaries, cache eviction/TTL, and failed-validation logging.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/proxy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/quota.rs -->
# sources/object-store/rustfs/crates/config/src/constants/quota.rs

## Purpose
Defines quota configuration filename, supported quota type, admin API route, S3-style error codes, and user-facing error messages.

## Important APIs, types, and functions
Key constants are `QUOTA_CONFIG_FILE`, `QUOTA_TYPE_HARD`, quota exceeded/invalid/not-found/internal error codes, `QUOTA_API_PATH`, and messages for unsupported quota types and missing bucket metadata system.

## Control flow
No runtime flow; quota handlers use these constants while parsing/administering bucket quotas and returning errors.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with bucket metadata persistence (`quota.json`), admin API routing, and S3-compatible error response generation.

## Risks and edge cases
Only HARD quota is supported; adding soft quotas requires changing validation and user messages. The API path embeds `{bucket}` and must match router syntax. Error code changes can break clients.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Quota integration tests should cover config file read/write, hard quota enforcement, unsupported type rejection, missing bucket handling, and API route matching.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/quota.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/runtime.rs -->
# sources/object-store/rustfs/crates/config/src/constants/runtime.rs

## Purpose
Defines Tokio runtime, telemetry, transition worker, allocator reclaim, file-cache reclaim, test-injection, and small-object seek support configuration constants.

## Important APIs, types, and functions
Runtime knobs include worker/blocking thread counts, thread stack/keepalive/name, queue/event intervals, I/O events per tick, RNG seed, and Dial9 telemetry output/S3/sampling settings. Transition constants set worker caps, queue capacity, send timeout, and test fault injection envs. Allocator/file-cache reclaim and object seek threshold defaults are also exported.

## Control flow
No local execution; startup/runtime builders and background services consume these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with Tokio runtime construction, telemetry logging/upload, lifecycle transition queues, IAM bootstrap test hooks, allocator reclaim loops, object file-cache hints, and small-object seek buffering.

## Risks and edge cases
Thread and blocking defaults strongly affect resource use. Test-only env vars must not be exposed as production behavior. Seek support threshold has a downstream hard cap, so parser/runtime docs must stay consistent. Telemetry paths can create sizable logs.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Runtime tests should cover env parsing bounds, transition queue backpressure, fault-injection gating, allocator reclaim cadence, and seek threshold cap behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/runtime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/scanner.rs -->
# sources/object-store/rustfs/crates/config/src/constants/scanner.rs

## Purpose
Defines scanner admin config keys, environment names/defaults, alert thresholds, concurrency budgets, idle/cache behavior, and the `ScannerSpeed` preset type.

## Important APIs, types, and functions
`SCANNER_KEYS` lists supported admin keys. Environment constants cover start delay, cycle, cycle object/directory/runtime budgets, speed, delay, max wait, bitrot cycle, alert thresholds, idle mode, cache save timeout, set/disk scan concurrency, yield frequency, and inline-heal compatibility. `ScannerSpeed` exposes `sleep_factor`, `max_sleep`, `cycle_interval`, `parse_str`, `from_env_str`, and `Display` for fastest/fast/default/slow/slowest.

## Control flow
Preset methods map variants to throttling and cycle durations. `parse_str` trims and lowercases input, returning `None` for unknown strings; `from_env_str` falls back to default. Display serializes the canonical lowercase name.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with data scanner scheduling, background bitrot scans, scanner cache persistence, alert generation for excessive versions/folders, heal-candidate enqueue, and admin config validation.

## Risks and edge cases
Scanner defaults can produce significant storage traversal load. `0` has special disable/unbounded semantics for multiple budgets. The deprecated start-delay alias must remain compatible while migration completes. Comments say inline heal is removed but the compatibility flag remains, so downstream behavior must only warn and continue enqueue-based healing.

## Test signals
Tests should cover all speed presets, parser fallback, display strings, budget zero semantics, deprecated alias precedence, cache save minimum, alert thresholds, and scanner/heal enqueue behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/scanner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/targets.rs -->
# sources/object-store/rustfs/crates/config/src/constants/targets.rs

## Purpose
Defines common notify/audit target KVS field names across webhook, MQTT, Kafka, AMQP, NATS, Pulsar, MySQL, Redis, and Postgres plus queue-store compression defaults.

## Important APIs, types, and functions
Field constants cover endpoints, credentials, TLS material, queue dir/limit, retry/timeouts, topics/subjects/channels, broker/address/DSN/table/format, SASL, Redis retry and timeout knobs, and `BASE_DSN_STRING`. `ENV_TARGET_STORE_COMPRESS` defaults queue-store compression to enabled.

## Control flow
No local flow; provider-specific notify modules assemble valid-key and env-key arrays from these names.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with notify/audit target config parsing, persistent event queues, provider clients, TLS loaders, database writers, and queue-store compression.

## Risks and edge cases
These field names are persistent config contract. Renaming breaks stored configuration and environment mapping. Queue compression defaults to on, so readers/writers must agree on `.snappy` handling and migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Provider config tests should validate every key maps to the expected env var and persisted KVS field, especially TLS and queue compression settings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/targets.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/tls.rs -->
# sources/object-store/rustfs/crates/config/src/constants/tls.rs

## Purpose
Defines TLS, mTLS, HTTP/2, HTTP/1, and certificate hot-reload environment names and defaults.

## Important APIs, types, and functions
Security constants include TLS key logging, trust system CA, trust leaf cert as CA, default client CA/cert/key filenames, mTLS client cert/key envs, and server mTLS enable default false. Transport tuning covers HTTP/2 stream/connection window, frame/header size, max concurrent streams, keepalive interval/timeout, HTTP/1 header timeout and buffer size. Reload constants default disabled with 30-second interval.

## Control flow
No local execution; TLS and HTTP server/client builders consume these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with rustls/native cert trust, mTLS authentication, HTTP/2 and HTTP/1 server transport configuration, and certificate reload watchers.

## Risks and edge cases
TLS key logging and trust-leaf-as-CA are high-risk debug/compatibility features and default off. HTTP/2 limits must remain within protocol bounds. Hot reload disabled by default avoids watcher complexity but requires restart for cert rotation unless enabled.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. TLS tests should cover cert path defaults, mTLS enablement, trust settings, HTTP/2 bounds, HTTP/1 header timeout, and reload interval minimums.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/tls.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/workload.rs -->
# sources/object-store/rustfs/crates/config/src/constants/workload.rs

## Purpose
Defines environment names and defaults for workload buffer sizing.

## Important APIs, types, and functions
Exports `ENV_RUSTFS_BUFFER_MIN_SIZE`, `ENV_RUSTFS_BUFFER_MAX_SIZE`, `ENV_RUSTFS_BUFFER_DEFAULT_SIZE`, and defaults 64 KiB minimum, 1 MiB maximum, and 256 KiB unknown-size buffer.

## Control flow
No runtime flow besides unit tests asserting constants and byte math.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with object/read buffering and workload profile selection code that imports `KI_B` and `MI_B` from the config crate.

## Risks and edge cases
Misordered min/default/max parsing downstream can cause inefficient buffering or memory spikes. Constants depend on crate-level KiB/MiB definitions staying stable.

## Test signals
Unit tests pin byte values and env names. Runtime tests should verify env overrides are clamped and selected buffers respect min/default/max relationships.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/workload.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/zero_copy.rs -->
# sources/object-store/rustfs/crates/config/src/constants/zero_copy.rs

## Purpose
Defines environment names and defaults for zero-copy reads and optional Linux Direct I/O.

## Important APIs, types, and functions
`ENV_OBJECT_ZERO_COPY_ENABLE` defaults true for mmap/optimized reads. `ENV_OBJECT_DIRECT_IO_ENABLE` defaults false. `ENV_OBJECT_DIRECT_IO_THRESHOLD` defaults to 128 MiB.

## Control flow
No executable logic. Object I/O layers decide whether platform support, file size, and failure behavior allow mmap or O_DIRECT.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with Unix mmap reads, non-Unix fallback reads, Linux O_DIRECT paths, object read performance tuning, and deployment-specific large-file workloads.

## Risks and edge cases
Zero-copy default on requires robust fallback if mmap fails. Direct I/O has alignment and workload caveats and is off by default. Threshold parsing must be in bytes and prevent tiny files from using O_DIRECT.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. I/O tests should cover mmap success/fallback, non-Unix fallback, O_DIRECT thresholding/alignment, and operator env overrides.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/zero_copy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/lib.rs -->
# sources/object-store/rustfs/crates/config/src/lib.rs

## Purpose
Feature-gated crate root for RustFS configuration constants and optional audit, notify, observability, OPA, and server-config modules.

## Important APIs, types, and functions
With `constants`, it exposes `pub mod constants` and re-exports each constants submodule at crate root, plus a nested `oidc` module. Optional modules are gated by `audit`, `notify`, `observability`, `opa`, and `server-config-model` features.

## Control flow
No runtime flow. Compile-time feature selection determines the public API surface.

## State and persistence behavior
No state or persistence. It controls which constants and config modules are linkable by dependent crates.

## Dependencies and integration points
Integrates with Cargo features and downstream crates that import constants from `rustfs_config::*`.

## Risks and edge cases
Public re-export changes are semver-sensitive. The nested `oidc` re-export differs from most constants modules and must stay documented for callers. Missing feature flags can make modules disappear at compile time.

## Test signals
Feature-matrix compilation is the main test signal. API tests should import representative constants and optional modules under their feature flags.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/amqp.rs -->
# sources/object-store/rustfs/crates/config/src/notify/amqp.rs

## Purpose
Registers AMQP notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_AMQP_KEYS` lists enable, AMQP URL, exchange, routing key, mandatory/persistent flags, username/password, TLS CA/client cert/key, queue dir/limit, and comment. `ENV_NOTIFY_AMQP_KEYS` lists the matching `RUSTFS_NOTIFY_AMQP_*` variables.

## Control flow
No local logic; notify config validation uses the key arrays to accept and map AMQP target settings.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/amqp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/arn.rs -->
# sources/object-store/rustfs/crates/config/src/notify/arn.rs

## Purpose
Defines RustFS notification ARN defaults.

## Important APIs, types, and functions
`DEFAULT_ARN_PARTITION` is `rustfs`, `DEFAULT_ARN_SERVICE` is `sqs`, and `ARN_PREFIX` is built with `const_str::concat!` as `arn:rustfs:sqs:`.

## Control flow
No local logic; notification target code appends target identifiers to the prefix.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/arn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/kafka.rs -->
# sources/object-store/rustfs/crates/config/src/notify/kafka.rs

## Purpose
Registers Kafka notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_KAFKA_KEYS` includes enable, brokers, topic, acks, TLS enable/material, SASL enable/mechanism/username/password, queue dir/limit, and comment. `ENV_NOTIFY_KAFKA_KEYS` mirrors these as `RUSTFS_NOTIFY_KAFKA_*` variables.

## Control flow
No local logic; provider config parsers consume the arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/kafka.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mod.rs -->
# sources/object-store/rustfs/crates/config/src/notify/mod.rs

## Purpose
Aggregates notification target constants and defines shared notification subsystem identifiers and concurrency defaults.

## Important APIs, types, and functions
Re-exports provider modules for AMQP, ARN, Kafka, MQTT, MySQL, NATS, Postgres, Pulsar, Redis, store, and webhook. Defines `DEFAULT_TARGET`, `NOTIFY_PREFIX`, `NOTIFY_ROUTE_PREFIX`, target stream/send concurrency env keys and defaults, subsystem list `NOTIFY_SUB_SYSTEMS`, provider subsystem names, and default Redis channel.

## Control flow
Rust module imports and `pub use` expose provider constants. `NOTIFY_ROUTE_PREFIX` is computed at compile time from `notify` plus the default delimiter.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with event notification routing, admin config subsystem registration, target stream fan-out, provider clients, and persisted notification target names.

## Risks and edge cases
Subsystem names are persistent config/API contract. Concurrency defaults affect throughput and downstream pressure. Dead-code subsystem constants for NSQ/Elasticsearch signal legacy or planned providers and must not be accidentally exposed as supported without implementation.

## Test signals
Tests should validate provider subsystem registration, route prefix construction, concurrency env parsing, and that every listed subsystem has matching key/env arrays.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mqtt.rs -->
# sources/object-store/rustfs/crates/config/src/notify/mqtt.rs

## Purpose
Registers MQTT notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_MQTT_KEYS` covers broker, topic, QoS, username/password, reconnect and keepalive intervals, queue dir/limit, TLS policy/material, leaf-as-CA trust, WebSocket path allowlist, enable/comment. `ENV_NOTIFY_MQTT_KEYS` mirrors the `RUSTFS_NOTIFY_MQTT_*` variables.

## Control flow
No local logic; MQTT target parsing and validation use the arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mqtt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mysql.rs -->
# sources/object-store/rustfs/crates/config/src/notify/mysql.rs

## Purpose
Registers MySQL notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_MYSQL_KEYS` includes DSN string, table, format, TLS CA/client cert/key, queue dir/limit, max open connections, enable/comment. `ENV_NOTIFY_MYSQL_KEYS` maps to `RUSTFS_NOTIFY_MYSQL_*`.

## Control flow
No local logic; database target setup uses these names.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/mysql.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/nats.rs -->
# sources/object-store/rustfs/crates/config/src/notify/nats.rs

## Purpose
Registers NATS notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_NATS_KEYS` includes address, subject, username/password/token/credentials file, TLS CA/client cert/key/required, queue dir/limit, enable/comment. `ENV_NOTIFY_NATS_KEYS` mirrors `RUSTFS_NOTIFY_NATS_*`.

## Control flow
No local logic; NATS target parsing uses these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/nats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/postgres.rs -->
# sources/object-store/rustfs/crates/config/src/notify/postgres.rs

## Purpose
Registers Postgres notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_POSTGRES_KEYS` includes DSN string, table, format, TLS required/material, queue dir/limit, enable/comment. `ENV_NOTIFY_POSTGRES_KEYS` maps to `RUSTFS_NOTIFY_POSTGRES_*`.

## Control flow
No local logic; database target setup consumes the arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/postgres.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/pulsar.rs -->
# sources/object-store/rustfs/crates/config/src/notify/pulsar.rs

## Purpose
Registers Pulsar notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_PULSAR_KEYS` includes broker, topic, auth token, username/password, TLS CA/allow-insecure/hostname verification, queue dir/limit, enable/comment. `ENV_NOTIFY_PULSAR_KEYS` maps to `RUSTFS_NOTIFY_PULSAR_*`.

## Control flow
No local logic; Pulsar target parsing uses these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/pulsar.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/redis.rs -->
# sources/object-store/rustfs/crates/config/src/notify/redis.rs

## Purpose
Registers Redis notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_REDIS_KEYS` includes URL, channel, username/password, keepalive, queue dir/limit, retry/reconnect attempts, min/max retry delay, connection/response timeouts, pipeline buffer size, TLS policy/material/allow-insecure, enable/comment. `ENV_NOTIFY_REDIS_KEYS` mirrors `RUSTFS_NOTIFY_REDIS_*`.

## Control flow
No local logic; Redis target setup and validation consume the arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
The main risk is contract drift: env names, key arrays, and field names are public configuration surface and can break operators or persisted config if renamed without migration.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/redis.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/store.rs -->
# sources/object-store/rustfs/crates/config/src/notify/store.rs

## Purpose
Defines queue-store file suffix constants for notification events.

## Important APIs, types, and functions
`DEFAULT_EXT` is `.unknown`, `COMPRESS_EXT` is `.snappy`, and `NOTIFY_STORE_EXTENSION` is `.event`.

## Control flow
No local logic; event queue store code chooses extensions from these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
Extension changes can break compatibility with existing queue files and compression detection.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/webhook.rs -->
# sources/object-store/rustfs/crates/config/src/notify/webhook.rs

## Purpose
Registers webhook notification target config and environment keys.

## Important APIs, types, and functions
`NOTIFY_WEBHOOK_KEYS` includes endpoint, auth token, queue limit/dir, client cert/key/CA, skip TLS verify, enable/comment. `ENV_NOTIFY_WEBHOOK_KEYS` maps to `RUSTFS_NOTIFY_WEBHOOK_*`.

## Control flow
No local logic; webhook target parsing and HTTP client setup consume the arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Downstream RustFS modules import these constants through `rustfs-config` and use them while parsing environment variables and persisted KVS configuration.

## Risks and edge cases
Webhook auth token and client key are sensitive and must be redacted by downstream config display. `skip_tls_verify` is security-sensitive.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/notify/webhook.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/metrics.rs -->
# sources/object-store/rustfs/crates/config/src/observability/metrics.rs

## Purpose
Defines the default system metrics scrape/collection interval and its environment key.

## Important APIs, types, and functions
`DEFAULT_METRICS_SYSTEM_INTERVAL_MS` is 30000 ms. `ENV_OBS_METRICS_SYSTEM_INTERVAL_MS` is `RUSTFS_OBS_METRICS_SYSTEM_INTERVAL_MS`.

## Control flow
No local logic; observability setup reads this for CPU/memory/disk/network collection cadence.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with system metrics collectors and observability exporters.

## Risks and edge cases
Too-low intervals can add system overhead; too-high intervals can hide short incidents. Parser bounds must be enforced downstream.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Metrics integration should verify interval override and collection cadence.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/mod.rs -->
# sources/object-store/rustfs/crates/config/src/observability/mod.rs

## Purpose
Defines observability environment keys and defaults for OTLP endpoints, per-signal export toggles, logging, log cleanup, compression, and environment names.

## Important APIs, types, and functions
Exports endpoint/header/timeout keys for traces, metrics, logs, profiling, stdout/sample/meter/service metadata keys, per-signal export flags, logger level/stdout/file rotation keys, cleanup sizing/compression/retention/dry-run/match-mode keys, and defaults including 2 GiB total log cap, zstd compression, parallel compression, 30-day compressed retention, and production/development/test/staging environment strings.

## Control flow
Module re-exports `metrics` and uses `const_str::concat!` to build compression extensions. Tests assert env-key names and default values.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with tracing/metrics/log/profiling exporters, file log rotation, cleanup workers, compression libraries, and service metadata.

## Risks and edge cases
Logging cleanup can delete or compress operator artifacts if match modes or exclude patterns are wrong. Endpoint header values may contain secrets. Compression defaults add CPU use but reduce disk pressure. Environment names may drive security-sensitive stdout behavior.

## Test signals
Unit tests pin key/default names. Integration tests should cover per-signal enablement, endpoint-specific headers/timeouts, cleanup dry run, retention, compression fallback, and match/exclude behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/observability/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/opa/mod.rs -->
# sources/object-store/rustfs/crates/config/src/opa/mod.rs

## Purpose
Defines OPA/policy plugin environment keys and subsystem name.

## Important APIs, types, and functions
`ENV_POLICY_PLUGIN_OPA_URL` maps to `RUSTFS_POLICY_PLUGIN_URL`, `ENV_POLICY_PLUGIN_AUTH_TOKEN` maps to `RUSTFS_POLICY_PLUGIN_AUTH_TOKEN`, `ENV_POLICY_PLUGIN_KEYS` lists both, and `POLICY_PLUGIN_SUB_SYS` is `policy_plugin`.

## Control flow
No local flow; policy plugin setup reads the URL/token from environment/config.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with external OPA or policy plugin authorization checks.

## Risks and edge cases
The auth token is sensitive and must not be logged. A configured external policy URL can become an availability dependency for authorization if downstream code fails closed.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Policy integration should cover token redaction, URL validation, and authorization behavior when the plugin is unavailable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/opa/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/server_config.rs -->
# sources/object-store/rustfs/crates/config/src/server_config.rs

## Purpose
Provides the in-memory server configuration model for KVS-based subsystem configuration plus global default and active config registries.

## Important APIs, types, and functions
`KV` stores `key`, `value`, and `hidden_if_empty` with serde alias `hiddenIfEmpty`. `KVS(Vec<KV>)` supports `new`, `get`, `lookup`, `is_empty`, `keys`, `insert`, and `extend`. `Config(HashMap<String, HashMap<String, KVS>>)` supports `new`, `get_value`, `set_defaults`, `unmarshal`, `marshal`, and placeholder `merge`. Globals are `DEFAULT_KVS: OnceLock<HashMap<String, KVS>>` and `GLOBAL_SERVER_CONFIG: RwLock<Option<Config>>`; public helpers register defaults and get/set the global config.

## Control flow
`Config::new` creates an empty map then calls `set_defaults`. `set_defaults` inserts each registered subsystem default under `DEFAULT_DELIMITER` when missing. JSON unmarshal loads the nested map and reapplies defaults; marshal serializes the internal map shape. KVS insert updates existing keys in place or appends new `KV` values.

## State and persistence behavior
Default KVS registration is one-shot via `OnceLock`. Active server config is process-global, mutable behind an `RwLock`, and cloned on reads. Persistence is JSON bytes produced/consumed by `marshal` and `unmarshal`; no file I/O occurs here.

## Dependencies and integration points
Integrates with admin config subsystems, feature-gated `server-config-model`, serde JSON storage, global runtime configuration readers, and constants such as `COMMENT_KEY` and `DEFAULT_DELIMITER`.

## Risks and edge cases
`register_default_kvs` ignores repeated registration failure, so ordering matters and duplicate initialization is silent. `merge` is currently a clone TODO, so default/user overlay semantics may be incomplete. `get` returns empty string for missing keys, which can blur missing versus explicitly empty values. Global config cloning can be stale for callers that cache results.

## Test signals
Unit tests cover KVS lookup/insert/extend/keys, camelCase alias deserialization, JSON marshal/unmarshal shape, `merge` clone behavior, and global config roundtrip. Additional tests should cover default registration ordering and concurrent get/set behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/server_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/Cargo.toml -->
# sources/object-store/rustfs/crates/credentials/Cargo.toml

## Purpose
Declares the `rustfs-credentials` crate metadata, dependencies, and workspace lint inheritance.

## Important APIs, types, and functions
The package describes credential management utilities for authentication/authorization. Dependencies include `base64-simd`, `hmac`, `rand`, `serde`, `serde_json`, `sha2`, and `time` with serde/parsing/formatting/macros features.

## Control flow
Cargo uses this manifest to compile the credentials crate and expose its library with workspace edition/version/license/rust-version settings.

## State and persistence behavior
No runtime state. Dependency and feature choices affect binary composition and serialization/parsing support.

## Dependencies and integration points
Integrates with the workspace dependency versions and crates that import credential generation, global credentials, RPC secret, and serde helpers.

## Risks and edge cases
Security behavior depends on cryptographic dependency versions. The manifest has no feature gates, so all listed dependencies are always included.

## Test signals
Build, cargo metadata, and crate tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/constants.rs -->
# sources/object-store/rustfs/crates/credentials/src/constants.rs

## Purpose
Defines default root credentials, RPC secret env name, IAM policy type strings, and service-account policy claim name.

## Important APIs, types, and functions
`DEFAULT_ACCESS_KEY` and `DEFAULT_SECRET_KEY` are both `rustfsadmin`. `ENV_RPC_SECRET` is `RUSTFS_RPC_SECRET`. IAM constants include embedded/inherited policy type strings and `IAM_POLICY_CLAIM_NAME_SA` as `sa-policy`.

## Control flow
No runtime flow except tests asserting default values and minimum lengths.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Consumed by credential initialization, RPC token derivation, IAM/service-account classification, and operator environment parsing.

## Risks and edge cases
Default access and secret keys are intentionally insecure for production and must be changed. `ENV_RPC_SECRET` fallback behavior is implemented in `credentials.rs`, so docs/comments must stay aligned.

## Test signals
Unit tests pin defaults and length checks. Integration should warn or reject defaults in production paths where applicable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/credentials.rs -->
# sources/object-store/rustfs/crates/credentials/src/credentials.rs

## Purpose
Implements credential generation, process-global active credentials, RPC authentication secret resolution/derivation, redacted formatting, and credential validity helpers.

## Important APIs, types, and functions
Key APIs are `init_global_action_credentials`, global access/secret getters, `gen_access_key`, `gen_secret_key`, `try_get_rpc_token`, deprecated `get_rpc_token`, `Masked`, `Credentials`, and methods `claims_or_empty`, `is_expired`, `is_temp`, `is_service_account`, `is_implied_policy`, `is_valid`, and `is_owner`. Errors use `CredentialsError`. RPC derivation uses HMAC-SHA256 over context `rustfs-rpc-secret:v1` plus access key, URL-safe base64 without padding.

## Control flow
Initialization chooses supplied keys or generates access length 20 and secret length 32, then sets a `OnceLock`. RPC token resolution first returns a cached valid global token, then tries non-empty/non-default `RUSTFS_RPC_SECRET`, otherwise derives from active access/secret credentials. Access key generation uses uppercase alphanumeric random chars and rejects length <3. Secret generation fills random bytes and encodes URL-safe no-padding base64, rejecting length <8.

## State and persistence behavior
Global credentials and RPC secret are one-shot process state in `OnceLock`s. `Credentials` serializes/deserializes JSON with MinIO-style camelCase aliases and optional RFC3339/legacy expiration via `serde_datetime`. No disk I/O occurs here, but serialized credentials are persisted by IAM/config layers.

## Dependencies and integration points
Integrates with `rustfs-credentials` constants, IAM service-account claims, RPC internode/auth setup, serde JSON, `time`, HMAC/SHA256, random generation, and base64-simd.

## Risks and edge cases
OnceLock makes tests/order and reconfiguration tricky; failed or default RPC env secrets intentionally produce a public error. `get_rpc_token` panics on missing secret and is deprecated. `is_owner` is hardcoded false, so owner semantics must live elsewhere. `is_valid` only checks status, key lengths, and expiration; it does not verify policy or signature.

## Test signals
Tests cover expiration/temp/service-account/implied-policy/validity, global credential flow, generation constraints, RPC secret derivation/default rejection/trimming, masked formatting including Unicode, debug redaction, and RFC3339 expiration serialization/deserialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/credentials.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/lib.rs -->
# sources/object-store/rustfs/crates/credentials/src/lib.rs

## Purpose
Crate root for `rustfs-credentials`, exposing constants and credential APIs while keeping the datetime serde helper internal.

## Important APIs, types, and functions
Declares modules `constants`, `credentials`, and `serde_datetime`; publicly re-exports `constants::*` and `credentials::*`.

## Control flow
No runtime flow; module declarations determine public API visibility.

## State and persistence behavior
No state directly, though the re-exported credentials module contains process-global OnceLocks.

## Dependencies and integration points
Used by RustFS crates importing credential constants, generators, global credential accessors, and `Credentials`.

## Risks and edge cases
The datetime module is private, so external callers rely on `Credentials` serde behavior rather than direct helper access. Re-export changes are public API breaks.

## Test signals
Compilation and public API import tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/serde_datetime.rs -->
# sources/object-store/rustfs/crates/credentials/src/serde_datetime.rs

## Purpose
Provides serde helpers for optional credential expiration timestamps, writing RFC3339 and reading either RFC3339 or legacy RustFS human-readable format.

## Important APIs, types, and functions
`legacy_format()` lazily parses and caches an owned time format. `parse_rfc3339_or_legacy` tries well-known RFC3339 first, then legacy. `option::serialize` serializes `Option<OffsetDateTime>` as RFC3339 or null; `option::deserialize` accepts optional strings and parses through the fallback helper.

## Control flow
Deserialization reads `Option<&str>`, returns `Ok(None)` for missing/null, and maps parse errors to serde custom errors. The legacy format cache is initialized once through `OnceLock`.

## State and persistence behavior
State is limited to the process-global parsed legacy format. Serialized timestamps persist in JSON credentials.

## Dependencies and integration points
Integrated by `Credentials.expiration` through `#[serde(default, with = "crate::serde_datetime::option")]` and depends on the `time` crate.

## Risks and edge cases
Legacy parsing widens accepted input and should remain compatible, but malformed strings fail deserialization for the whole credential. RFC3339 output can differ in fractional precision based on `time` formatting.

## Test signals
Credential tests verify RFC3339 serialization and MinIO-style RFC3339 deserialization. Additional tests should cover legacy format acceptance and invalid timestamp rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/serde_datetime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/Cargo.toml -->
# sources/object-store/rustfs/crates/crypto/Cargo.toml

## Purpose
Declares the `rustfs-crypto` crate metadata, dependencies, feature gates, and library settings.

## Important APIs, types, and functions
Default features are `crypto` and `fips`. Optional crypto dependencies include AES-GCM, Argon2, ChaCha20Poly1305, PBKDF2, rand, and sha2. JWT/RSA/serde/serde_json/thiserror are unconditional. Doctests are disabled.

## Control flow
Cargo feature selection controls whether encryption code is active and whether FIPS selects PBKDF2/AES-GCM paths.

## State and persistence behavior
No runtime state. Feature choices alter compiled algorithms and fallback behavior.

## Dependencies and integration points
Integrates with workspace dependency versions, JWT code, encryption/decryption modules, and tests requiring crypto feature dependencies.

## Risks and edge cases
Defaulting to both `crypto` and `fips` means default encryption chooses PBKDF2/AES-GCM instead of non-FIPS Argon2/ChaCha selection. Optional dependency drift can change cryptographic behavior.

## Test signals
Cargo feature-matrix builds and encryption/JWT tests are the key signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec.rs

## Purpose
Module hub for encryption/decryption support.

## Important APIs, types, and functions
Conditionally includes `aes` when not `fips`, exposes crate-private `id` and `stream_io` under test or `crypto`, and always includes crate-private `decrypt` and `encrypt`. Test module is enabled under `cfg(test)`.

## Control flow
No runtime flow; compile-time cfg controls algorithm helper availability.

## State and persistence behavior
No state directly.

## Dependencies and integration points
Integrates encryption, decryption, algorithm id, stream_io compatibility, and AES hardware detection modules.

## Risks and edge cases
Cfg boundaries are important: non-crypto builds make encrypt/decrypt pass-through functions in child modules, while crypto builds perform real AEAD. Feature tests must catch accidental plaintext behavior in production builds.

## Test signals
Feature-matrix compilation and encdec tests validate module availability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/aes.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/aes.rs

## Purpose
Detects whether the current CPU has native AES acceleration needed for algorithm selection.

## Important APIs, types, and functions
`native_aes()` checks AES/PCLMUL on x86/x86_64, AES on aarch64, returns false on powerpc64, checks AES/AESCBC/AESCTR plus AESGCM or GHASH on s390x, and false on other targets.

## Control flow
Uses `cfg_select!` to compile target-specific feature detection. No caching is performed.

## State and persistence behavior
No persistent state; each call queries CPU feature macros.

## Dependencies and integration points
Used by non-FIPS encryption and stream_io code to choose Argon2id+AES-GCM when hardware support exists, otherwise Argon2id+ChaCha20Poly1305.

## Risks and edge cases
Incorrect feature detection can choose a slow or unsupported algorithm. Returning false on powerpc64 may force ChaCha even where AES exists. This module is absent under `fips`.

## Test signals
Cross-architecture build tests and runtime algorithm-id tests on representative CPUs are useful signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/aes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/decrypt.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/decrypt.rs

## Purpose
Decrypts the non-stream AEAD envelope produced by `encrypt_data`, with a plaintext pass-through fallback when crypto is not compiled.

## Important APIs, types, and functions
`decrypt_data` expects header salt(32) + alg_id(1) + nonce(12), derives a key with `ID::get_key`, selects ChaCha20Poly1305 for `Argon2idChaCHa20Poly1305` and AES-256-GCM otherwise, then calls a generic AEAD helper. Non-crypto builds return `data.to_vec()`.

## Control flow
It validates minimum 45-byte header length, parses algorithm id from byte 32, slices body after the header, converts nonce to the AEAD nonce size, and maps decrypt failures to `ErrDecryptFailed`.

## State and persistence behavior
No persistent state. The encrypted byte format is persisted by callers and must remain backward compatible.

## Dependencies and integration points
Integrates with `encdec::id`, AES-GCM, ChaCha20Poly1305, and the public crate error type.

## Risks and edge cases
Header length and algorithm id are format-critical. Non-crypto pass-through can be dangerous if the feature set is misconfigured. Wrong-password, tamper, or truncation must fail without leaking plaintext.

## Test signals
Tests cover roundtrip, wrong password, empty/large/binary/unicode data, corruption, truncation, invalid algorithm id, and feature-backed failures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/decrypt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/encrypt.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/encrypt.rs

## Purpose
Encrypts arbitrary bytes into a compact AEAD envelope with random salt and nonce, with a plaintext fallback when crypto is not compiled.

## Important APIs, types, and functions
`encrypt_data` generates a 32-byte salt, chooses `ID::Pbkdf2AESGCM` under `fips`, otherwise chooses Argon2id AES-GCM when `native_aes()` is true or Argon2id ChaCha20Poly1305 otherwise. `encrypt` creates a random nonce, AEAD-encrypts the data, and outputs salt + id + nonce + ciphertext/tag.

## Control flow
The generic helper reserves output capacity, appends header fields, and maps AEAD errors to `ErrEncryptFailed`. Non-crypto builds return a plaintext copy.

## State and persistence behavior
No persistent state, but the emitted envelope is a storage format consumed by `decrypt_data`.

## Dependencies and integration points
Integrates with CPU AES detection, algorithm id/key derivation, AES-GCM, ChaCha20Poly1305, rand, and FIPS feature selection.

## Risks and edge cases
Random salt/nonce generation is security-critical. The non-crypto fallback must never be used unintentionally for protected data. Algorithm choice must remain compatible with decrypt and persisted ids.

## Test signals
Tests assert distinct ciphertext for same input, envelope structure, many input/password forms, large data, concurrency, and decrypt compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/encrypt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/id.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/id.rs

## Purpose
Defines encrypted-format algorithm identifiers and password-to-key derivation.

## Important APIs, types, and functions
`ID` is a `repr(u8)` enum: `Argon2idAESGCM=0x00`, `Argon2idChaCHa20Poly1305=0x01`, and `Pbkdf2AESGCM=0x02`. `TryFrom<u8>` validates persisted ids. `get_key` derives a 32-byte key using PBKDF2-HMAC-SHA256 with 8192 iterations or Argon2id v1.3 with 64 MiB memory, 1 iteration, parallelism 4, output length 32.

## Control flow
Callers parse the id from encrypted data, then call `get_key(password, salt)` before constructing the selected AEAD.

## State and persistence behavior
No state. The numeric ids are persisted in encrypted headers and cannot change without migration.

## Dependencies and integration points
Integrates with encrypt/decrypt, stream_io, PBKDF2, Argon2, SHA256, and crate error conversion.

## Risks and edge cases
Changing id values or KDF parameters breaks old encrypted data or changes security/performance. Argon2 memory cost can be expensive under concurrency. Empty password/salt are currently allowed by tests, so callers must enforce policy if needed.

## Test signals
Unit tests cover id values, valid/invalid conversion, key determinism, different password/salt behavior, all algorithms, empty inputs, and cross-algorithm differences.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/stream_io.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/stream_io.rs

## Purpose
Implements sio-go compatible fragmented stream encryption/decryption for IAM config data.

## Important APIs, types, and functions
Public APIs are `encrypt_stream_io` and `decrypt_stream_io`. Format header is salt(32) + alg_id(1) + nonce_prefix(8). Body uses DARE-style 16 KiB fragments, 12-byte nonces composed from prefix plus little-endian sequence number, 16-byte AEAD tags, and associated data derived by encrypting an empty block with sequence zero. Algorithm selection mirrors `encrypt_data`: PBKDF2/AES-GCM under FIPS, otherwise native-AES based Argon2id AES-GCM or ChaCha20Poly1305.

## Control flow
Decrypt validates the 41-byte header, derives key, selects AEAD, then iterates fragments using ciphertext chunk size 16384+tag, setting associated-data first byte to `0x80` for the last fragment. Encrypt builds the header, then chunks plaintext into 16 KiB fragments, marks the last fragment, encrypts in place detached, and appends tag per fragment.

## State and persistence behavior
No mutable global state. The stream_io byte format is a persisted interoperability contract for IAM/config encrypted blobs.

## Dependencies and integration points
Integrates with sio-go compatibility expectations, `ID` key derivation, AES-GCM, ChaCha20Poly1305, rand, and crate errors.

## Risks and edge cases
Fragment boundaries, final-fragment marker, nonce sequence, and associated-data construction are all compatibility-sensitive. Empty plaintext currently emits only a header with no final encrypted fragment; decrypt returns empty, but cross-implementation behavior should be checked. Sequence number overflow is not handled for extremely large streams.

## Test signals
Tests cover stream_io roundtrip, >16 KiB fragmentation, wrong password failure, empty data, and header format. Cross-language tests with sio-go vectors would be a stronger signal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/stream_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/tests.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/tests.rs

## Purpose
Test suite for the encryption/decryption and stream_io compatibility modules.

## Important APIs, types, and functions
Uses `encrypt_data`, `decrypt_data`, `encrypt_stream_io`, and `decrypt_stream_io` with fixed password constants and `test-case` parameterization.

## Control flow
Tests run roundtrips over small, empty, binary, unicode, large, and varied-password inputs; verify wrong-password and corrupted/truncated/header-invalid data fail; verify ciphertext differs for repeated encryption; inspect minimum envelope structure; spawn concurrent encryption threads; and validate stream_io roundtrip, fragmentation, wrong password, empty data, and header id.

## State and persistence behavior
No persistent state. Some tests touch global CPU/feature-dependent algorithm choices only through envelope id allowances.

## Dependencies and integration points
Integrates with the entire encdec module, random generation, AEAD error handling, and thread safety.

## Risks and edge cases
Tests are strong for functional roundtrip but do not include external known-answer vectors or cross-language sio-go fixtures. Randomized outputs mean tests assert properties rather than exact ciphertext.

## Test signals
Passing this suite signals correct local encryption, decryption, tamper detection, concurrency safety, and stream_io header/fragment behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/error.rs -->
# sources/object-store/rustfs/crates/crypto/src/error.rs

## Purpose
Defines the common error enum for crypto, JWT, encryption, signature, token, and I/O failures.

## Important APIs, types, and functions
`Error` variants include unexpected header, invalid algorithm id, invalid input, invalid key length, feature-gated digest/AEAD/Argon2 errors, JWT errors, I/O errors, invalid signature, and invalid token. It derives `thiserror::Error` for display/source behavior.

## Control flow
No control flow; other modules construct or convert into these variants through `From` on wrapped errors.

## State and persistence behavior
No state.

## Dependencies and integration points
Integrated by encdec, JWT encode/decode, and any RSA/signature/token code in the crate.

## Risks and edge cases
Feature-gated variants alter the enum shape across builds, so external matching should be cautious. Error messages are part of operator/debug behavior but should not leak secrets.

## Test signals
Compilation under feature combinations and tests for invalid headers/ids/JWT failures are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt.rs -->
# sources/object-store/rustfs/crates/crypto/src/jwt.rs

## Purpose
Module root for JWT helpers and shared claims type.

## Important APIs, types, and functions
Declares `decode` and `encode` modules and re-exports `serde_json::Value` as `Claims`; includes a test module under `cfg(test)`.

## Control flow
No runtime flow; child modules call the `jsonwebtoken` crate.

## State and persistence behavior
No state.

## Dependencies and integration points
Used by authentication/session code that needs HS512 JWT encode/decode over arbitrary JSON claims.

## Risks and edge cases
`Claims` as generic JSON value gives flexibility but little static validation. Callers must enforce required claims, expiration, issuer, and audience semantics.

## Test signals
JWT encode/decode roundtrip and validation failure tests are expected signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/decode.rs -->
# sources/object-store/rustfs/crates/crypto/src/jwt/decode.rs

## Purpose
Provides HS512 JWT decoding using a shared secret.

## Important APIs, types, and functions
`decode(token, token_secret)` returns `jsonwebtoken::TokenData<Claims>` or crate `Error`, using `DecodingKey::from_secret` and `Validation::new(Algorithm::HS512)`.

## Control flow
The function delegates signature and claim validation to `jsonwebtoken::decode` with HS512 validation.

## State and persistence behavior
No state.

## Dependencies and integration points
Integrates with `jwt::Claims`, crate error conversion, and authentication/session token consumers.

## Risks and edge cases
Default `Validation::new` behavior must match product requirements for exp/aud/issuer. Secret length/entropy is not checked here. Algorithm is fixed to HS512, so tokens using other algorithms fail.

## Test signals
Tests should cover valid HS512 tokens, bad signatures, expired tokens if exp validation is expected, malformed JSON claims, and wrong algorithm headers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/decode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/encode.rs -->
# sources/object-store/rustfs/crates/crypto/src/jwt/encode.rs

## Purpose
Provides HS512 JWT encoding using a shared secret.

## Important APIs, types, and functions
`encode(token_secret, claims)` creates a `Header::new(Algorithm::HS512)` and signs arbitrary JSON `Claims` with `EncodingKey::from_secret`.

## Control flow
The function is a direct wrapper around `jsonwebtoken::encode`, mapping errors into crate `Error`.

## State and persistence behavior
No state.

## Dependencies and integration points
Integrates with session/auth token issuance and the decode helper's HS512 expectations.

## Risks and edge cases
Claims are not enriched or validated here; callers must include expiration, subject, issuer, and audience as needed. Secret entropy is not enforced.

## Test signals
Tests should cover encode/decode roundtrip, expected HS512 header, and failure with non-serializable or invalid claims if applicable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/encode.rs -->
