# subset-b-008292 Research

Grouped research report for the requested trusted-proxies and utils files. Each section is bounded by reconciliation markers and titled with the original source path.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/gcp.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/gcp.rs

Purpose: Implements the GCP `CloudMetadataFetcher` for trusted proxy range discovery. `GcpMetadataFetcher` owns a `reqwest::Client` with caller-provided timeout and a metadata endpoint defaulting to `http://metadata.google.internal`.

Important APIs: `new`, `provider_name`, `fetch_network_cidrs`, `fetch_public_ip_ranges`, private `get_metadata`, `subnet_mask_to_prefix_length`, `fetch_gcp_ip_ranges`, `default_gcp_ip_ranges`, and `default_gcp_network_ranges`. The trait methods expose provider name, internal network CIDRs, and public provider ranges.

Control flow: network CIDR discovery lists `instance/network-interfaces/`, parses numeric interface indices, fetches each interface IP and subnet mask concurrently with `tokio::try_join!`, converts masks to prefixes, and falls back to RFC1918/GCP-reserved defaults when metadata is unavailable or empty. Public IP discovery fetches `https://www.gstatic.com/ipranges/cloud.json`, deserializes `prefixes`, and currently keeps only `ipv4_prefix` values from the API; the static fallback includes both IPv4 and IPv6 literals.

State and dependencies: No persistence beyond the HTTP client. Depends on `async_trait`, `reqwest`, `serde`, `ipnetwork`, `tokio`, and structured `tracing`, and returns crate `AppError`.

Integration points: Re-exported through `metadata/mod.rs` and `cloud/mod.rs`; used wherever `CloudMetadataFetcher` implementations are selected. Test signals are indirect from cloud integration tests, which cover provider naming for AWS but do not exercise GCP metadata parsing.

Risks: `Client::builder().build()` falls back silently to `Client::new`; metadata endpoint is fixed and not injectable for tests. `subnet_mask_to_prefix_length` does not reject non-contiguous masks across octet boundaries such as `255.0.255.0` because it resets state per octet. API parsing ignores `ipv6Prefix`/camelCase if the JSON uses that spelling, while the fallback list includes IPv6.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/gcp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/mod.rs

Purpose: Metadata provider module aggregator for cloud-specific trusted proxy discovery.

Important APIs: Declares private submodules `aws`, `azure`, and `gcp`, then publicly re-exports each module's contents with `pub use`. No local functions or state.

Control flow and state: Compile-time module wiring only. It creates the public namespace where fetchers such as `AwsMetadataFetcher`, `AzureMetadataFetcher`, and `GcpMetadataFetcher` become visible to the rest of the crate.

Dependencies and integration: Sits under `cloud/mod.rs` and feeds the crate-level re-exports in `lib.rs`. Consumers can import provider fetchers from `rustfs_trusted_proxies::*` without knowing the file layout.

Risks and tests: Risk is mainly namespace coupling: adding a provider here changes the public API. Integration tests import `AwsMetadataFetcher` through the public path, indirectly confirming these re-exports compile.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/mod.rs

Purpose: Top-level cloud integration module for automatic provider detection, metadata fetching, and static/dynamic IP range sources.

Important APIs: Declares private `detector`, public `metadata`, private `ranges`, and re-exports `detector::*`, `metadata::*`, and `ranges::*`.

Control flow and state: No runtime logic; it is the namespace boundary joining detection, metadata provider implementations, and standalone cloud range helpers.

Dependencies and integration: Re-exported by crate `lib.rs`, making cloud range and metadata types part of the public trusted-proxies API. The listed files integrate with unlisted `detector.rs` through the `CloudMetadataFetcher` trait and provider detection path.

Risks and tests: Public wildcard re-exports can obscure API ownership and increase accidental API surface. Integration tests under `tests/integration/cloud_tests.rs` verify that public detector and metadata fetcher imports compile and basic disabled detection works.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/ranges.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/ranges.rs

Purpose: Provides standalone cloud/provider IP range utilities for Cloudflare, DigitalOcean, and Google Cloud.

Important APIs: `CloudflareIpRanges::fetch` returns a static Cloudflare IPv4/IPv6 list; `CloudflareIpRanges::fetch_from_api` fetches official v4/v6 text endpoints and falls back to static ranges; `DigitalOceanIpRanges::fetch` returns a static set of datacenter/load-balancer ranges; `GoogleCloudIpRanges::fetch` retrieves `cloud.json`.

Control flow: Each fetcher parses string CIDRs into `IpNetwork`, logs structured success/failure details, and returns `AppError::cloud` only for construction/parsing errors that prevent normal operation. Cloudflare API attempts both URL sources independently, appends successful parsed ranges, and falls back only if both yield no ranges. Google Cloud returns an empty vector on HTTP/request failures instead of falling back to static data in this file.

State and dependencies: Stateless async helpers using `reqwest::Client`, `ipnetwork`, `serde` for GCP JSON, `Duration`, and `tracing`.

Integration points: Re-exported through `cloud/mod.rs`; likely contributes optional trusted proxy allowlists when cloud/provider mode is enabled.

Risks and tests: Cloudflare and DigitalOcean static ranges can age. Google Cloud parsing captures only `ipv4_prefix`, so IPv6 API prefixes are dropped. Returning `Ok(Vec::new())` for GCP fetch failures can hide provider range failures from callers. No direct tests in the requested test files cover these helper range fetchers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/cloud/ranges.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/env.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/config/env.rs

Purpose: Small environment helper module for trusted proxy configuration.

Important APIs: `parse_ip_list_from_env`, `parse_string_list_from_env`, `is_env_set`, and `get_all_proxy_env_vars`.

Control flow: `parse_ip_list_from_env` reads an env var or default, splits comma-separated entries, trims empties, parses each entry as `IpNetwork`, logs parse failures, and continues. `parse_string_list_from_env` performs tolerant comma splitting for raw string values such as individual IPs. `get_all_proxy_env_vars` enumerates current proxy-related env values from constants in `rustfs_config`.

State and dependencies: No persistent state. Depends on `std::env`, `ipnetwork`, `rustfs_config` env-name constants, `ConfigError`, and tracing warnings.

Integration points: Used by `ConfigLoader::load_proxy_config` to build CIDR and string lists. Tests in `config_tests.rs` exercise loader defaults/env variables, indirectly checking these helpers.

Risks: `parse_ip_list_from_env` returns `Ok` even when some entries fail, which favors availability but can silently ignore intended trust ranges. `ConfigError` is imported but only used as a return type; invalid entries are logged rather than propagated.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/env.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/loader.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/config/loader.rs

Purpose: Loads complete trusted-proxies runtime configuration from environment and defaults.

Important APIs: `ConfigLoader::from_env`, `from_env_or_default`, `default_config`, and `print_summary`; private loaders for proxy, cache, monitoring, cloud, and server address.

Control flow: `from_env` composes `AppConfig` from five loading steps. Proxy loading parses configured CIDR proxies, extra proxies, individual IPs, validation mode, RFC7239 toggle, max hops, continuity checks, and private networks. Cache, monitoring, and cloud loading are direct env/default reads via `rustfs_utils`. Server binding reads `RUSTFS_ADDRESS` and falls back to IPv6 unspecified plus default port if parsing fails. `from_env_or_default` logs success or falls back to `default_config` on any loader error.

State and dependencies: Stateless loader depending on `rustfs_config` constants, `rustfs_utils` env/address helpers, `IpNetwork`, `SocketAddr`, and crate config/error types.

Integration points: `global::init` calls `from_env_or_default`; middleware/layer construction receives the resulting proxy and cache configs. Unit config tests cover defaults, env override of proxies/mode/max hops, `TrustedProxyConfig` behavior, private network checks, and expected default string constants.

Risks: Individual IP parsing silently drops bad values. Any invalid validation mode causes full fallback in `from_env_or_default`, potentially replacing otherwise valid user config. Server address parse failures are silently normalized to default bind address.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/loader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/config/mod.rs

Purpose: Public configuration module boundary.

Important APIs: Declares `env`, `loader`, and `types`, then publicly re-exports all three.

Control flow and state: Compile-time wiring only. It centralizes env helpers, `ConfigLoader`, and configuration structs/enums under `crate::config` and crate-level re-exports.

Dependencies and integration: `lib.rs` re-exports this module, so downstream users can access config types directly from `rustfs_trusted_proxies`. Most trusted-proxies modules import these public config types through crate re-exports.

Risks and tests: Wildcard re-export broadens public API. Unit config tests import `ConfigLoader`, `TrustedProxy`, `TrustedProxyConfig`, and `ValidationMode` via the crate, indirectly confirming this module exports the expected items.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/types.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/config/types.rs

Purpose: Defines trusted proxy configuration data structures and validation modes.

Important APIs/types: `ValidationMode` (`Lenient`, `Strict`, default `HopByHop`) with `FromStr` and `as_str`; `TrustedProxy` (`Single`, `Cidr`) with `contains` and `Display`; `TrustedProxyConfig` with trust/private-network checks and summaries; `CacheConfig`; `MonitoringConfig`; `CloudConfig`; and `AppConfig`.

Control flow: Runtime behavior is mostly simple predicate/composition logic. `TrustedProxyConfig::is_trusted` checks any configured entry against a socket IP. `CloudConfig`/`CacheConfig` convert second counts into `Duration`. Defaults come partly from `rustfs_config` and partly from hard-coded cache defaults.

State and dependencies: Plain cloneable structs with no persistence. Depends on `serde`, `ipnetwork`, `IpAddr`, `SocketAddr`, and `rustfs_config`.

Integration points: Used by loader, validator, middleware layers, global init, cache, and tests. `ValidationMode` drives chain analyzer behavior.

Risks and tests: `TrustedProxyConfig` is mutable only by replacement, which is simple but means hot reload is absent. `ValidationMode::FromStr` accepts `hopbyhop` and `hop_by_hop` but not hyphenated variants. Unit tests cover mode/config basics, trust matching, private network matching, and default proxy constants.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/config/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/error/config.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/error/config.rs

Purpose: Defines configuration-specific errors for the trusted proxy system.

Important APIs: `ConfigError` enum variants for missing env vars, parse failures, invalid values/IPs, validation failures, conflicts, file errors, and general invalid config. Includes conversions from `AddrParseError` and `ipnetwork::IpNetworkError`, plus helper constructors `missing_env_var`, `env_parse`, and `invalid_value`.

Control flow and state: Error type only; no runtime state. `thiserror` derives display messages used in logs and API responses via `AppError`.

Dependencies and integration: Used by config parsing and `ValidationMode::FromStr`, converted into `AppError::Config` by `error/mod.rs`.

Risks and tests: Many variants are not exercised in requested tests. Loader helper behavior currently logs some parse errors instead of returning this error type, so callers may see fewer `ConfigError`s than the type suggests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/error/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/error/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/error/mod.rs

Purpose: Aggregates trusted-proxies error types and defines the crate-wide `AppError`.

Important APIs: Re-exports `ConfigError` and `ProxyError`; defines `AppError::{Config, Proxy, Cloud, Internal, Io, Http}`, constructors `cloud/internal/http`, recoverability classification, `ApiError` alias, and `From<AppError> for (StatusCode, String)`.

Control flow: Recoverability delegates to `ProxyError::is_recoverable` and treats config/cloud/io/http as recoverable while internal is not. HTTP status mapping returns bad request for config/proxy, service unavailable for cloud, internal server error for internal/io, and bad gateway for HTTP.

State and dependencies: Error-only module using `thiserror`, `http::StatusCode`, and `std::io`.

Integration points: Cloud metadata/range helpers use `AppError::cloud`; application boundaries can convert into API errors.

Risks and tests: Marking all config errors recoverable is a policy choice that may mask startup misconfiguration if used beyond fallback paths. No direct requested tests validate status mappings or recoverability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/error/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/error/proxy.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/error/proxy.rs

Purpose: Defines proxy validation errors and recoverability semantics.

Important APIs: `ProxyError` variants cover malformed XFF/RFC7239 headers, chain validation failure, chain-too-long, untrusted proxy, non-continuity, IP/header parse failures, timeout, and internal errors. Helper constructors create common variants. `From<AddrParseError>` maps to `IpParseError`.

Control flow: `is_recoverable` returns true for untrusted proxy, chain too long, non-continuity, and timeout, enabling middleware fallback to direct peer. Malformed headers, parse errors, chain validation failure, and internal errors are non-recoverable.

State and dependencies: Error-only module with `thiserror` and `AddrParseError`.

Integration points: `ProxyValidator`, `ProxyChainAnalyzer`, middleware fallback path, metrics failure labels, and `AppError` conversion.

Risks and tests: Treating `ChainTooLong` as recoverable means a suspicious oversized proxy header can be downgraded to direct peer rather than rejected. Unit validator tests assert `ChainTooLong` is produced by analyzer, but recoverability behavior is not directly asserted.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/error/proxy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/global.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/global.rs

Purpose: Legacy global singleton entrypoints for initializing and accessing the full trusted proxy system.

Important APIs/state: `init`, `layer`, `config`, `metrics`, and `is_enabled`. State is stored in `OnceLock<Arc<AppConfig>>`, `OnceLock<Option<ProxyMetrics>>`, `OnceLock<LegacyTrustedProxyLayer>`, and `OnceLock<bool>`.

Control flow: `init` reads enabled state, exits early when disabled, loads config, initializes metrics if configured, builds a legacy layer with cache config and maintenance task, logs lifecycle/config summary, and leaves singletons initialized forever. Accessors panic if called before successful initialization.

Dependencies and integration: Uses `ConfigLoader`, `LegacyTrustedProxyLayer`, `ProxyMetrics`, defaults/env keys from `rustfs_config`, and `rustfs_utils`. The simplified default implementation can select this legacy path through `simple.rs`.

Risks and tests: `OnceLock` prevents runtime reconfiguration and makes env-dependent tests sensitive to initialization order. If disabled, `CONFIG` and `PROXY_LAYER` remain unset, so calling `legacy_layer` after disabled init panics. No direct requested tests cover these global accessors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/global.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/lib.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/lib.rs

Purpose: Crate root for trusted proxy middleware, configuration, cloud helpers, validation, metrics, and utility exports.

Important APIs: Declares modules `cloud`, `config`, `error`, `global`, `middleware`, `proxy`, `simple`, and `utils`. Re-exports all cloud/config/error/proxy/utils items; aliases legacy global functions and middleware types; exports simplified default API from `simple.rs` as `init`, `layer`, `is_enabled`, `implementation`, `TrustedProxyLayer`, and `TrustedProxyMiddleware`.

Control flow and state: No runtime logic; API selection is encoded by re-export names. The public default path is simplified, while legacy names remain available.

Dependencies and integration: Tests import public types through this file, confirming crate-level access. Application users likely layer `TrustedProxyLayer` into Tower/Axum services.

Risks and tests: Having both legacy and simplified `TrustedProxyLayer` names, with aliases for legacy, can confuse users and create migration risk. Compile-time coverage is strong because many tests import through the crate root.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/middleware/layer.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/middleware/layer.rs

Purpose: Legacy Tower `Layer` implementation that wraps services with the full proxy validator.

Important APIs/state: `TrustedProxyLayer` holds `Arc<ProxyValidator>` and an `enabled` flag. Constructors: `new`, `with_cache_config`, `enabled`, `disabled`, and `is_enabled`. Implements `tower::Layer`.

Control flow: `with_cache_config` builds `ProxyValidator` with config/cache/metrics and starts cache maintenance if enabled. `disabled` constructs a lenient empty config with no metrics. `layer` clones the validator into `LegacyTrustedProxyMiddleware`.

Dependencies and integration: Uses `ProxyValidator`, `TrustedProxyConfig`, `CacheConfig`, `ProxyMetrics`, and Tower. `global.rs` and simplified legacy wrapper use this layer.

Risks and tests: Spawning maintenance only when enabled is correct, but constructor assumes a Tokio runtime is available; validator handles missing runtime by logging. Integration proxy tests exercise this layer in Axum routing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/middleware/layer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/middleware/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/middleware/mod.rs

Purpose: Middleware module aggregator for the legacy Tower layer and service.

Important APIs: Declares `layer` and `service`, then re-exports both.

Control flow and state: Compile-time namespace wiring only. Exposes `TrustedProxyLayer` and `TrustedProxyMiddleware` from the legacy implementation.

Dependencies and integration: `lib.rs` re-exports these as `LegacyTrustedProxyLayer` and `LegacyTrustedProxyMiddleware` to avoid colliding with simplified defaults.

Risks and tests: No local runtime risk. Integration tests import `LegacyTrustedProxyLayer` through crate root and confirm layer composition compiles and returns HTTP 200.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/middleware/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/middleware/service.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/middleware/service.rs

Purpose: Legacy Tower `Service` wrapper that validates proxy headers and inserts `ClientInfo` into request extensions.

Important APIs/state: `TrustedProxyMiddleware<S>` stores inner service, `Arc<ProxyValidator>`, and enabled flag. Constructors `new` and `from_layer`; implements `Service<Request<ReqBody>>`.

Control flow: Disabled mode passes through. Enabled mode reads peer `SocketAddr` from request extensions, calls `validate_request`, inserts successful `ClientInfo`, falls back to direct peer for recoverable errors, and logs non-recoverable validation failures without inserting replacement info. It always forwards the request to the inner service.

Dependencies and integration: Uses `http::Request`, Tower, `ClientInfo`, `ProxyValidator`, and tracing. Relies on upstream server layers to populate `SocketAddr` in request extensions.

Risks and tests: Non-recoverable validation errors still allow request processing and may leave no `ClientInfo`, which can surprise downstream code expecting it. Missing peer address falls back to `0.0.0.0:0`. Integration tests cover pass-through success but not error insertion semantics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/middleware/service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/cache.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/cache.rs

Purpose: Moka-backed cache for direct-peer trusted proxy decisions.

Important APIs/state: `IpValidationCache` stores `Cache<IpAddr, bool>`, capacity, enabled flag, and optional `ProxyMetrics`. Public methods: `new`, `is_trusted`, `clear`, `run_maintenance`, `stats`, and `is_enabled`. `CacheStats` reports size/capacity.

Control flow: Disabled cache executes the validator closure directly. Enabled cache checks Moka for an IP, records hits/misses, invokes the validator on miss, and caches only positive trust decisions to avoid accumulating untrusted client IPs. Maintenance runs pending tasks and updates metrics.

Dependencies and integration: Used by `ProxyValidator` for direct peer trust checks. Metrics methods are optional and no-op when disabled.

Risks and tests: Positive-only caching means repeated untrusted peers always re-run CIDR matching, which is intentional but can cost CPU under hostile traffic. Cache size metric is approximate until pending tasks run. Unit validator tests check trusted decisions populate cache while untrusted/missing/unspecified peers do not.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/chain.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/chain.rs

Purpose: Analyzes proxy IP chains to identify the real client and validate trust according to configured mode.

Important APIs/state: `ChainAnalysis` returns client IP, hop count, continuity, warnings, mode, and trusted suffix. `ProxyChainAnalyzer` owns `TrustedProxyConfig` and a precomputed `HashSet<IpAddr>` for single IPs and small IPv4 CIDRs (`/24` or narrower).

Control flow: `analyze_chain` validates header IPs, appends current direct proxy, enforces max hops, dispatches to lenient/strict/hop-by-hop logic, checks continuity, collects warnings, and validates the chosen client IP. Lenient trusts the full chain if the last proxy is trusted. Strict requires every IP in the chain to be trusted. Hop-by-hop walks from right to left until the first untrusted IP and treats that as the client boundary.

Dependencies and integration: Called by `ProxyValidator::validate_trusted_proxy_request`. Uses `HeaderMap`, `TrustedProxyConfig`, `ValidationMode`, `ProxyError`, and IP utilities.

Risks and tests: Strict mode appears to require the client IP itself to be trusted because it checks every IP including the first chain element, which may not match common proxy semantics. Duplicate warning only reports the first duplicate. Unit tests cover hop-by-hop success and chain-too-long error.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/chain.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/metrics.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/metrics.rs

Purpose: Metrics collection wrapper for proxy validation, cache behavior, and validation modes.

Important APIs: `ProxyMetrics::new`, `increment_validation_attempts`, `record_validation_success`, `record_validation_failure`, `record_validation_mode`, `record_cache_hit`, `record_cache_miss`, `set_cache_size`, `record_cache_metrics`, `print_summary`, and `default_proxy_metrics`.

Control flow: Constructor stores enabled flag/app label and registers metric descriptions if enabled. Every recorder returns immediately when disabled. Success/failure recorders emit counters, gauges, and histograms with `app` and error/mode labels. Failure type is derived by matching `ProxyError` variants.

State and dependencies: Lightweight cloneable struct with no metric state of its own; uses the global `metrics` facade and tracing.

Integration points: Optional in `ProxyValidator`, `IpValidationCache`, and global initialization. `default_proxy_metrics` uses app name `trusted-proxy`.

Risks and tests: Metric descriptions include `rustfs_trusted_proxy_validation_mode` gauge only indirectly through recorder, but no description is registered for that name. `record_cache_metrics` increments counters by supplied values, so callers must pass deltas rather than totals. Requested tests do not assert metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/mod.rs

Purpose: Proxy validation module aggregator.

Important APIs: Declares `cache`, `chain`, `metrics`, and `validator`, then publicly re-exports all of them.

Control flow and state: Compile-time wiring only. Exposes cache stats, chain analyzer, metrics collector, `ClientInfo`, and `ProxyValidator` through a single module and crate root.

Dependencies and integration: `lib.rs` re-exports this module; middleware and tests import proxy types through crate root.

Risks and tests: Wildcard re-export makes internal-ish helpers such as `ProxyChainAnalyzer` public. Unit validator tests import both analyzer and validator, confirming these exports compile.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/validator.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/validator.rs

Purpose: Core legacy request validator that decides whether a request came through a trusted proxy and extracts verified client metadata.

Important APIs/state: `ClientInfo::direct` and `from_trusted_proxy`; `ProxyValidator::new`, `with_cache_config`, `validate_request`, `cache_stats`, `parse_x_forwarded_for`, and crate-private `spawn_cache_maintenance_task`. The validator owns config, a `ProxyChainAnalyzer`, an `Arc<IpValidationCache>`, and optional metrics.

Control flow: `validate_request` wraps internal validation with attempt/result metrics. Internal validation handles missing/unspecified peer as direct, checks direct peer trust through positive-only cache, then either validates trusted proxy headers or returns direct info. Trusted proxy validation prefers RFC7239 when enabled, falls back to legacy X-Forwarded headers, runs chain analysis, enforces hop/continuity, and builds `ClientInfo`.

Dependencies and integration: Used by legacy layer/service/global path. It depends on `HeaderMap`, `CacheConfig`, `ProxyChainAnalyzer`, `ProxyMetrics`, and `ProxyError`.

Risks and tests: Header parsing is intentionally permissive and does not sanitize forwarded host/proto. Legacy `parse_x_forwarded_for` splits non-bracketed values at the first colon, so bare IPv6 addresses without brackets are misparsed. RFC7239 parser handles only the first comma-separated entry. Unit tests cover direct info, XFF count, hop-by-hop chain, chain-too-long, cache behavior, and cache bypass for missing/unspecified peers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/proxy/validator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/simple.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/simple.rs

Purpose: Default simplified trusted-proxy implementation for RustFS, with an env switch to use the legacy full validator.

Important APIs/state: `TrustedProxyImplementation::{Simple, Legacy}`, global `init`, `is_enabled`, `implementation`, `layer`, public enum `TrustedProxyLayer`, public enum `TrustedProxyMiddleware`, `SimpleTrustedProxyLayer`, and `SimpleTrustedProxyMiddleware`. State uses `OnceLock` for enabled, implementation, and layer.

Control flow: `build_layer` returns disabled simple layer when globally disabled, simple layer by default, or initializes/wraps legacy global layer when env selects legacy/full. Simple middleware reads peer `SocketAddr`, trusts forwarded headers only when the peer IP is internal (private, loopback, or link-local), chooses client IP from XFF, X-Real-IP, or Forwarded, sanitizes host/proto, and inserts `ClientInfo`.

State and dependencies: No persistent dynamic state beyond once-only globals. Depends on Tower, Axum HTTP, `rustfs_config` env defaults, `rustfs_utils`, and legacy types.

Integration points: Re-exported as the crate's default `TrustedProxyLayer`/`init`/`layer`. Tests cover implementation parsing, header priority/fallback, host/proto preservation and sanitization, public-peer rejection of forwarded headers, missing peer behavior, token parsing, internal IP detection, and env-selected legacy mode.

Risks: The simplified model treats all internal peers as trusted proxies, which is pragmatic for internal deployments but risky if untrusted clients can connect from private/link-local networks. `OnceLock` makes env changes after first access ineffective. Host validation rejects whitespace/control but not all authority syntax edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/simple.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/utils/ip.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/utils/ip.rs

Purpose: IP classification, parsing, range membership, and canonicalization helpers.

Important APIs: `IpUtils` methods for valid/reserved/private/loopback/link-local/documentation classification; `parse_ip_or_cidr`, `parse_ip_list`, `parse_network_list`, `ip_in_networks`, `get_ip_type`, `canonical_ip`; free `is_valid_ip_address`.

Control flow: Classification uses std `IpAddr` methods plus explicit octet/segment pattern matches. Parsing splits comma lists, trims empty entries, and returns errors on invalid non-empty tokens. `get_ip_type` orders checks as private, loopback, link-local, documentation, reserved, public.

State and dependencies: Stateless; depends on `ipnetwork` and std net types.

Integration points: `ProxyChainAnalyzer` uses the free `is_valid_ip_address`; tests import `IpUtils` through crate root.

Risks and tests: `is_valid_ip_address` allows documentation/reserved/private addresses, intentionally separating syntax/usefulness from policy. Reserved IPv4 matching includes private and multicast ranges, while `get_ip_type` masks private before reserved. Unit IP tests cover all classifications, parsing, network membership, type ordering, and canonical formatting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/utils/ip.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/utils/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/utils/mod.rs

Purpose: Utility module aggregator for trusted-proxies.

Important APIs: Declares `ip` and `validation`, then publicly re-exports both.

Control flow and state: Compile-time wiring only. It exposes `IpUtils`, `ValidationUtils`, and free helper functions through `crate::utils` and crate root.

Dependencies and integration: Re-exported by `lib.rs`; validator/chain code and tests import helpers through crate-level paths.

Risks and tests: No runtime risk. Unit tests for IP and validation utilities indirectly confirm the exports.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/utils/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/utils/validation.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/src/utils/validation.rs

Purpose: General validation utilities for headers, forwarded proxy values, CIDRs, strings, rate-limit/cache parameters, and redaction.

Important APIs/state: `ValidationUtils` with email/URL validation, `validate_x_forwarded_for`, `extract_ip_part`, `validate_forwarded_header`, `validate_ip_in_range`, header checks, port/CIDR/proxy-chain checks, `is_safe_string`, rate/cache parameter validation, and `mask_sensitive_data`. Regexes are cached in `OnceLock`.

Control flow: XFF validation splits comma entries and parses extracted IP parts; bracketed IPv6 is handled, but unbracketed colon splitting favors IPv4-with-port. Header validation enforces name length, value length, and control-character rules. Redaction builds case-insensitive regexes from caller-supplied patterns and logs invalid pattern compilation.

Dependencies and integration: Uses `http::HeaderMap`, `regex`, `ipnetwork`, and tracing. These helpers are public but are not heavily used by the core validator.

Risks and tests: `validate_x_forwarded_for` treats entries with no extractable IP as continue rather than failure in some branches. URL/email regexes are intentionally simple and not standards-complete. Unit validation tests cover representative happy/failure cases for email, URL, XFF, Forwarded, CIDR range, header length, port, and CIDR syntax.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/src/utils/validation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/integration/cloud_tests.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/integration/cloud_tests.rs

Purpose: Minimal async integration coverage for cloud provider detection/metadata exports.

Important APIs tested: `CloudDetector::new(false, timeout, None).detect_provider()` and `AwsMetadataFetcher::new(...).provider_name()`.

Control flow: Disabled detector should return `None` without external metadata calls. AWS metadata fetcher construction should expose provider name `aws`.

State and dependencies: Uses Tokio tests and imports public crate APIs. No persistent state.

Integration points: Confirms crate-level public re-exports for `CloudDetector`, `AwsMetadataFetcher`, and `CloudMetadataFetcher`.

Risks and coverage gaps: Does not test enabled detection, GCP/Azure fetchers, network CIDR parsing, public range fetches, or failure fallback behavior. It intentionally avoids real cloud metadata/network dependency.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/integration/cloud_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/integration/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/integration/mod.rs

Purpose: Integration test module registry for trusted-proxies.

Important APIs: Under `#[cfg(test)]`, declares `cloud_tests` and `proxy_tests`.

Control flow and state: Compile-time test wiring only. No runtime logic or persistence.

Integration points: Ensures grouped integration tests compile when the test target includes this module.

Risks and tests: No direct behavioral risk. If new integration files are added, they must be registered here or as standalone test targets.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/integration/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/integration/proxy_tests.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/integration/proxy_tests.rs

Purpose: Axum/Tower integration smoke test for the legacy trusted proxy layer.

Important APIs tested: `TrustedProxyConfig::new`, `TrustedProxy::Single`, `ValidationMode::HopByHop`, `LegacyTrustedProxyLayer::enabled`, Axum router layering, and `tower::ServiceExt::oneshot`.

Control flow: Builds a route returning `OK`, layers the legacy proxy layer, sends a request with `X-Forwarded-For`, and asserts HTTP 200.

State and dependencies: Async Tokio test with no external state. It does not insert peer `SocketAddr` into request extensions, so validator follows missing-peer direct fallback.

Integration points: Confirms the legacy layer composes with Axum and does not reject requests.

Risks and coverage gaps: It does not assert inserted `ClientInfo`, trusted proxy behavior, header parsing, or error fallback. Because peer address is missing, it does not fully exercise trusted proxy validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/integration/proxy_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/proxy_layer.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/proxy_layer.rs

Purpose: Standalone Tower tests for the default simplified `TrustedProxyLayer`.

Important APIs tested: `TrustedProxyLayer::enabled().layer(service)`, request extension insertion of peer `SocketAddr`, and downstream access to `ClientInfo`.

Control flow: The first test inserts an internal peer (`10.0.0.5`) with XFF and expects response body to be forwarded client IP. The second inserts a public peer (`8.8.8.8`) with XFF and expects the direct peer IP, proving forwarded headers are ignored from non-internal peers.

State and dependencies: Uses Axum body/request/response types, Tower `service_fn`, `Layer`, and `ServiceExt`.

Integration points: Exercises the crate's default public layer rather than legacy aliases.

Risks and coverage gaps: Tests only XFF, not X-Real-IP/RFC7239/host/proto behavior or disabled layer. It confirms the core security boundary of simple mode: only internal peers can override client IP.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/proxy_layer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/config_tests.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/config_tests.rs

Purpose: Unit tests for trusted proxy config loading and config data structures.

Important APIs tested: `ConfigLoader::from_env_or_default`, `ConfigLoader::from_env`, `TrustedProxyConfig::new`, `TrustedProxy::contains`, `TrustedProxyConfig::is_trusted`, `is_private_network`, `ValidationMode`, and default proxy constants.

Control flow: Serial env tests clear/set relevant variables using `temp_env`, verify defaults and env overrides, then independent tests validate single-IP/CIDR matching and private-network matching.

State and dependencies: Uses serial execution for env-mutating tests. Depends on `rustfs_config` constants and public trusted-proxies exports.

Integration points: Covers config path consumed by global legacy initialization and validator construction.

Risks and coverage gaps: Does not assert invalid env values, fallback behavior when validation mode is malformed, cloud/cache/monitoring env fields, or individual IP list parsing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/config_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/ip_tests.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/ip_tests.rs

Purpose: Unit tests for `IpUtils` parsing, classification, membership, and canonicalization.

Important APIs tested: `is_valid_ip_address`, reserved/private/loopback/link-local/documentation classifiers, `parse_ip_or_cidr`, `parse_ip_list`, `parse_network_list`, `ip_in_networks`, `get_ip_type`, and `canonical_ip`.

Control flow: Tests construct representative IPv4/IPv6 addresses, verify positive and negative classification boundaries, ensure parse failures propagate on invalid list entries, and compare canonical strings or re-parsed IPv6 equality where formatting can vary.

State and dependencies: Pure tests with no global state. Uses std `IpAddr` parsing and public crate exports.

Integration points: Provides confidence for chain validation's `is_valid_ip_address` assumptions and public utility behavior.

Risks and coverage gaps: Does not exhaust all special-use IP ranges. Tests document that reserved and valid are separate concepts: documentation IPv6 is still valid for general use.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/ip_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/mod.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/mod.rs

Purpose: Unit test module registry for trusted-proxies.

Important APIs: Under `#[cfg(test)]`, declares `config_tests`, `ip_tests`, `validation_tests`, and `validator_tests`.

Control flow and state: Compile-time test wiring only.

Integration points: Ensures unit test modules are included when this module target is compiled.

Risks and tests: No runtime behavior. New unit test files require registration here unless compiled as separate integration targets.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validation_tests.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validation_tests.rs

Purpose: Unit tests for `ValidationUtils`.

Important APIs tested: email/URL validation, X-Forwarded-For validation, RFC7239 Forwarded syntax validation, CIDR membership, header value length/control checks, port validation, and CIDR syntax validation.

Control flow: Each test asserts a simple valid case and, where relevant, a simple invalid case. CIDR membership verifies an IP in `10.0.0.0/8` matches a string list.

State and dependencies: Pure tests with no global mutation. Regex initialization occurs through `OnceLock` in the production module.

Integration points: Confirms public validation utilities compile and handle basic cases.

Risks and coverage gaps: Does not test multiline/control header rejection beyond overlong value, sensitive-data masking, safe-string validation, rate/cache parameter validation, or IPv6/port edge cases in forwarded headers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validation_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validator_tests.rs -->
# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validator_tests.rs

Purpose: Unit tests for legacy `ProxyValidator`, `ProxyChainAnalyzer`, and `ClientInfo`.

Important APIs tested: `ClientInfo::direct`, `ProxyValidator::parse_x_forwarded_for`, `ProxyChainAnalyzer::analyze_chain`, `ProxyValidator::with_cache_config`, `validate_request`, and `cache_stats`.

Control flow: A helper config trusts one single IP and `10.0.0.0/8`. Tests check direct info, XFF parsing count, hop-by-hop analysis success, chain-too-long error shape, positive cache insertion for trusted peer, no negative caching for untrusted peer, and cache bypass for missing or unspecified peer.

State and dependencies: Pure unit tests with in-memory cache; no env mutation. Uses `HeaderMap`, `IpAddr`, `SocketAddr`, and crate public APIs.

Integration points: Exercises the validator used by legacy middleware/global path.

Risks and coverage gaps: Does not assert RFC7239 parsing, forwarded host/proto extraction, strict/lenient semantics, malformed header errors, continuity failure, metrics, or cache maintenance task behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/trusted-proxies/tests/unit/validator_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/Cargo.toml -->
# sources/object-store/rustfs/crates/utils/Cargo.toml

Purpose: Cargo manifest for `rustfs-utils`, a feature-gated utility crate used by RustFS components.

Important APIs/config: Package metadata identifies utilities for hashing, compression, and network support. Dependencies are mostly workspace dependencies and optional behind features. Feature sets include `ip` default, `net`, `io`, `path`, `compress`, `string`, `crypto`, `hash`, `os`, `integration`, `http`, `obj`, and `full`.

Control flow/state: Build-time dependency selection only. Target-specific Windows dependency exposes filesystem APIs under `os`.

Integration points: `trusted-proxies` uses env/address utilities from this crate. Other RustFS crates can enable only needed utility surfaces to reduce dependency cost.

Risks and tests: Optional dependencies must stay aligned with source modules; enabling source files without matching features can break builds if module gating is absent elsewhere. Default is only `ip`, so consumers requiring env/crypto/hash/compress must request the proper feature set or rely on a broader workspace feature.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/compress.rs -->
# sources/object-store/rustfs/crates/utils/src/compress.rs

Purpose: Block compression/decompression helpers for several algorithms.

Important APIs: `CompressionAlgorithm` enum (`None`, `Gzip`, `Deflate`, `Zstd`, default `Lz4`, `Brotli`, `Snappy`) with `as_str`, `Display`, and `FromStr`; `compress_block`; `decompress_block`.

Control flow: Compression dispatches to the selected library writer/encoder and returns compressed bytes. Decompression dispatches to matching readers/decoders. `None` compression returns the input bytes, while `None` decompression returns an empty vector.

State and dependencies: Stateless. Depends on `flate2`, `zstd`, `lz4`, `brotli`, `snap`, `tokio::io` for error type, and std I/O.

Integration points: Enabled by the utils `compress` feature. Tests exercise round-trip behavior for all actual algorithms and print benchmark/comparison output.

Risks and tests: Several compression paths ignore `write_all`/`flush` errors or use `expect`, making some failures panic or degrade to empty output. `decompress_block(None)` returning empty instead of original bytes is a semantic trap if callers treat `None` as pass-through. Benchmark tests print timing and may be noisy but assert round-trip correctness.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/compress.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/crypto.rs -->
# sources/object-store/rustfs/crates/utils/src/crypto.rs

Purpose: Crypto encoding and digest helpers for base64url, hex, HMAC, and SHA-256.

Important APIs: `base64_encode_url_safe_no_pad`, `base64_decode_url_safe_no_pad`, `hex`, `is_sha256_checksum`, `hmac_sha1`, `hmac_sha256`, `hex_sha256`, and `hex_sha256_chunk`.

Control flow: Base64 uses SIMD URL-safe no-padding codec. Hex uses `hex_simd` lowercase. SHA-256 helpers compute fixed 32-byte digest, encode into a stack `MaybeUninit` buffer via `hex_simd`, and pass the temporary string to a caller closure to avoid allocation. Chunk hashing updates a single hasher across `hyper::body::Bytes` slices.

State and dependencies: Stateless. Depends on `base64-simd`, `hex-simd`, `hmac`, `sha1`, `sha2`, and `hyper::body::Bytes`.

Integration points: Enabled by utils `crypto` feature and likely used by signing/checksum paths.

Risks and tests: HMAC constructors unwrap, though HMAC accepts arbitrary key lengths for these algorithms. Closure-based hex APIs require consumers not to retain borrowed string beyond callback. Tests cover base64 round trip and strict lowercase SHA-256 checksum validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/crypto.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/dirs.rs -->
# sources/object-store/rustfs/crates/utils/src/dirs.rs

Purpose: Best-effort project root discovery helper.

Important APIs: `get_project_root() -> Result<PathBuf, String>`.

Control flow: Tries `CARGO_MANIFEST_DIR`, then derives from `current_exe` by popping executable and target profile directories, then derives from current directory by popping one level. Returns a string error only if all methods fail.

State and dependencies: Stateless, using `std::env`, `PathBuf`, and tracing debug logs.

Integration points: General utility likely used by tests/tools needing a root path.

Risks and tests: The `current_exe` and `current_dir` heuristics are build-layout assumptions and can return the wrong root outside Cargo target layouts. Unit test only asserts returned path exists, not that it is the workspace or crate root.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/dirs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/dunce.rs -->
# sources/object-store/rustfs/crates/utils/src/dunce.rs

Purpose: Windows path simplification utilities adapted from the `dunce` behavior: convert safe verbatim disk paths such as `\\?\C:\...` to ordinary paths.

Important APIs: `simplified`, `canonicalize`, `is_simplified`, and hidden alias `realpath`. Helper functions validate Windows filenames, detect reserved DOS device names, and attempt prefix stripping.

Control flow: On non-Windows, `simplified` is a no-op and `canonicalize` delegates to `fs::canonicalize`. On Windows, `canonicalize` resolves the path then simplifies only safe verbatim disk paths. Simplification rejects non-UTF-8 paths, invalid/reserved names, `..` components, other UNC forms, and paths over MAX_PATH limits.

State and dependencies: Stateless. Uses platform cfgs, std filesystem/path APIs, and Windows-only path component matching.

Integration points: Enabled by utils `os` feature; useful when passing canonical paths to tools that do not accept verbatim UNC paths.

Risks and tests: Strict UTF-8 and MAX_PATH checks intentionally leave many paths unchanged. Tests cover reserved names, filename validity, Windows simplification under cfg, Unix no-op behavior, and `is_simplified`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/dunce.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/envs.rs -->
# sources/object-store/rustfs/crates/utils/src/envs.rs

Purpose: Central environment parsing and compatibility helpers for RustFS.

Important APIs/state: Numeric getters for signed/unsigned/floating types, optional variants, `get_env_str`, `get_env_bool`, alias-aware variants, `ExternalEnvCompatReport`, `build_external_env_compat_report`, and `apply_external_env_compat`. Warning de-duplication uses `OnceLock<Mutex<HashSet<String>>>`.

Control flow: Canonical env key takes precedence. Deprecated aliases are checked next with one-time warnings. For `RUSTFS_*` keys, selected external-prefix variables are accepted when the suffix is in an allowlist or dynamic notification/audit prefix. Parsing failures generally fall back to defaults or `None`; bool parsing accepts many truthy/falsy tokens. Compatibility report maps source-prefixed variables to missing `RUSTFS_*` names and records conflicts when both exist with different values. `apply_external_env_compat` copies mappable values into the current process and is marked unsafe because env mutation should occur before threads.

Dependencies and integration: Used by trusted-proxies config loader for booleans/strings/numbers and by broader RustFS configuration bootstrap.

Risks and tests: Generic numeric getters do not log invalid values except specialized alias-aware paths, which can hide bad config. Global warning state makes warning assertions order-dependent. Tests cover source-prefix mapping, conflicts, dynamic suffixes, ignored keys, alias precedence, invalid i32 alias fallback, and applying compatibility mappings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/envs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/hash.rs -->
# sources/object-store/rustfs/crates/utils/src/hash.rs

Purpose: Hashing utilities for bitrot protection, bucket distribution, and compatibility.

Important APIs/state: `HashAlgorithm` enum (`SHA256`, `HighwayHash256`, default `HighwayHash256S`, legacy streaming HighwayHash key, `BLAKE2b512`, `Md5`, `None`), private `HashEncoded` storage, `hash_encode`, `size`, `EMPTY_STRING_SHA256_HASH`, `DEFAULT_SIP_HASH_KEY`, `sip_hash`, and `crc_hash`.

Control flow: `hash_encode` dispatches to the chosen algorithm, returning fixed-size stack arrays behind an `AsRef<[u8]>` enum. HighwayHash variants use fixed 32-byte keys converted into four `u64`s; legacy mode preserves main-branch compatibility. `sip_hash` and `crc_hash` hash string keys then mod by cardinality.

State and dependencies: Stateless. Depends on `sha2`, `blake2`, `md-5`, `highway`, `siphasher`, `crc-fast`, `serde`, and `hex-simd` in tests.

Integration points: Enabled by utils `hash` feature; likely used by object storage bitrot and sharding logic.

Risks and tests: `sip_hash`/`crc_hash` divide by `cardinality`, so zero cardinality will panic. MD5 is included and should only be used where non-cryptographic compatibility is acceptable. Tests cover output sizes, deterministic/different hashes, bitrot self-test vectors, and HighwayHash compatibility data.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/hash.rs -->
