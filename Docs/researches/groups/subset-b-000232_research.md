# Research Group: subset-b-000232

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/Cargo.toml -->
# sources/cloud-native/nydus/storage/Cargo.toml

## Purpose
This manifest defines the `nydus-storage` Rust crate, version `0.7.2`, the storage subsystem for Nydus Image Service. It acts as a feature-gated backend crate that can read blobs from local filesystems, local disks, OSS/S3-style object storage, container registries, HTTP proxy servers, and Dragonfly proxy integration.

## Important APIs, Types, and Feature Surface
The manifest exposes backend implementations through Cargo features rather than separate crates. Key feature flags are `backend-localdisk`, `backend-localdisk-gpt`, `backend-localfs`, `backend-oss`, `backend-registry`, `backend-s3`, `backend-http-proxy`, `backend-dragonfly-proxy`, and `dedup`. Optional dependencies map directly to those features: OSS pulls in `base64`, `httpdate`, `hmac`, `sha1`, `reqwest`, and `url`; S3 adds `http`, `sha2`, and `time`; HTTP proxy adds `hyper`, `hyperlocal`, `hyper-util`, `http-body-util`, `reqwest`, and `url`; Dragonfly proxy uses `dragonfly-client-util`; dedup uses `rusqlite`, `r2d2`, and `r2d2_sqlite`.

## Control Flow and Build Behavior
The crate is edition 2021 and relies on workspace crates `nydus-api`, `nydus-utils`, `vm-memory`, and `fuse-backend-rs`. Most source modules are conditionally compiled, so runtime behavior depends strongly on feature combinations. The `backend-localdisk-gpt` feature depends on `gpt` plus `backend-localdisk`, making GPT partition discovery an explicit opt-in extension.

## State, Persistence, and Dependencies
The manifest does not persist runtime state itself, but it declares dependencies that drive persistence in backend modules: `rusqlite` for dedup state, `gpt` for local disk partition tables, metrics via `nydus-utils`, and networking through `reqwest`, `hyper`, and `tokio`. Tokio is always included with runtime and synchronization features, while network client crates are optional.

## Integration Points
This crate integrates with `nydus-api` configuration types, `nydus-utils` metrics and singleflight helpers, FUSE memory slices from `fuse-backend-rs`, and optional cloud/proxy protocol clients. Docs.rs is configured to build all features for multiple common targets.

## Risks and Test Signals
The primary risk is feature matrix complexity: conditional modules can compile and behave differently depending on backend combinations. Tests in backend modules exercise many feature-specific paths, but live-network DNS tests and optional feature combinations require targeted CI coverage. Dependency versions are pinned broadly enough to receive semver-compatible updates, so network client behavior can shift without local code changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/connection.rs -->
# sources/cloud-native/nydus/storage/src/backend/connection.rs

## Purpose
This module provides the blocking HTTP connection layer shared by remote storage backends. It wraps `reqwest::blocking::Client`, optional proxy routing, Hickory DNS resolution, proxy health checks, request body variants, and response status handling.

## Important APIs, Types, and Functions
`ConnectionConfig` normalizes OSS, S3, registry, and HTTP proxy configuration into proxy, TLS, timeout, retry, and custom CA settings. `Connection::new` builds a direct client and, if configured, a proxy client. `Connection::call` and `call_with_proxy_control` send HTTP requests, optionally bypassing proxy use. `ReqBody` supports streaming reads with progress, raw buffers, and form maps. `Progress<R>` wraps a reader and invokes a callback as bytes are consumed. `respond` converts non-success responses into `ConnectionError::ErrorWithMsg` when `catch_status` is enabled.

## Control Flow
Direct clients are built with Hickory DNS and `no_proxy()` so environment proxies do not affect fallback-to-origin behavior. Proxy clients use `reqwest::Proxy::all`. On each call, the module checks `shutdown`, updates `last_active`, tries the proxy when configured and healthy, optionally rewrites `https` to `http` when `proxy.use_http` is set, and falls back to the origin only if proxy fallback is enabled or the proxy is unhealthy with fallback allowed. `call_inner` builds the request, attaches headers/query/body, sends it, logs sanitized debug headers with Authorization removed, and applies status handling.

## State and Persistence Behavior
`Connection` holds a direct client, optional proxy state, an atomic shutdown flag, and an atomic `last_active` timestamp. `ProxyHealth` stores health in an `AtomicBool` plus optional ping URL and timing settings. A thread-local `LAST_FALLBACK_AT` rate-limits unhealthy-proxy fallback warnings. If a ping URL is configured, `start_proxy_health_thread` spawns a background thread that loops for the process lifetime; there is no join handle or shutdown break condition.

## Dependencies and Integration Points
The module depends on `reqwest` blocking APIs, `nydus_api` config structs, `url`, and the local `HickoryDnsResolver`. It is consumed by object storage, registry, and HTTP proxy request paths. Custom CA files are read from disk and added to the client builder.

## Risks
Proxy health threads are unbounded lifecycle-wise and do not observe `Connection::shutdown`. Proxy URL scheme replacement is cached in an atomic and only reasons about initial `http`/`https` prefixes. `call_inner` sends an empty body for no-data requests, which is usually fine but can affect servers sensitive to request bodies. Tests that rely on localhost errors are stable; behavior involving real proxy health timing and custom CA parsing needs integration coverage.

## Test Signals
Unit tests cover `Progress`, proxy health state, status classification, default config conversion, unhealthy proxy fallback/no-fallback, healthy proxy error behavior, and shutdown/disconnected behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/connection.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/hickory.rs -->
# sources/cloud-native/nydus/storage/src/backend/hickory.rs

## Purpose
This module implements a `reqwest::dns::Resolve` adapter backed by `hickory-resolver`. It gives reqwest clients DNS lookup caching, negative caching, IPv4-then-IPv6 ordering, and singleflight deduplication for concurrent lookups.

## Important APIs, Types, and Functions
`HickoryDnsResolver` is the exported resolver wrapper. It owns a lazily initialized `OnceCell<ResolverState>` and a `lookup_count` counter used by tests. `ResolverState` contains the `TokioResolver`, an async `RwLock<HashMap<String, Arc<CachedLookup>>>`, and a `nydus_utils::singleflight::Group`. `CachedLookup` stores resolved IPs, expiration, and optional error text. `SocketAddrs` adapts `IpAddr` values into `SocketAddr` entries with port `0`. `new_resolver_state` reads system resolver config and sets `LookupIpStrategy::Ipv4thenIpv6`.

## Control Flow
`resolve` initializes resolver state on first use, checks the cache under a read lock, and returns either cached addresses or a cached error when the TTL is still valid. Cache misses enter singleflight by domain name; only one task performs the actual Hickory lookup and updates the cache. Successful lookups use Hickory-provided TTLs. Failed lookups are cached for `NEGATIVE_CACHE_TTL` of 60 seconds.

## State and Persistence Behavior
All state is in memory and shared by clones. The cache grows by domain name and has TTL validation but no explicit eviction sweep. Failed lookups persist temporarily as negative cache entries, reducing pressure on DNS infrastructure during repeated failures.

## Dependencies and Integration Points
The resolver implements `reqwest::dns::Resolve`, so `connection.rs` installs it via `Client::builder().dns_resolver(...)`. It relies on Tokio async synchronization even though the surrounding client is blocking reqwest.

## Risks
The cache does not proactively remove expired entries, so long-running processes with many unique domains can accumulate stale keys. Negative cache duration may hide recovery for up to 60 seconds. The live DNS tests use public domains such as `baidu.com`, `qq.com`, and `taobao.com`, which can fail in isolated CI or restricted networks.

## Test Signals
Tokio tests cover successful resolution, concurrent singleflight, cache hits, negative caching, negative cache expiry, per-domain independence, TTL expiry refresh, and concurrent refresh after expiry.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/hickory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/http_proxy.rs -->
# sources/cloud-native/nydus/storage/src/backend/http_proxy.rs

## Purpose
This file implements a blob backend that reads through an HTTP proxy endpoint. The proxy may be a local Unix socket served through Hyper or a remote `http://`/`https://` endpoint routed through the shared request layer.

## Important APIs, Types, and Functions
`HttpProxy` is the `BlobBackend`; `HttpProxyReader` is the `BlobReader`. `Client` distinguishes `Local(LocalClient)` from `Remote(Arc<request::Request>)`, while `Uri` distinguishes local Hyper URIs from remote strings. `range_str_for_header` formats byte ranges. `LocalClient::get_headers` performs HEAD requests and `try_read` performs GET range reads inside a dedicated Tokio runtime. `HttpProxy::new` chooses local or remote mode from `HttpProxyConfig.addr`.

## Control Flow
`get_reader` joins configured `path` and `blob_id`. Local mode builds a `hyperlocal` URI from the Unix socket address and uses `/` as the path; remote mode concatenates `addr` and the joined path. `blob_size` issues HEAD and parses `Content-Length`. `try_read_ctx` sends a GET with `Range: bytes=start-end`, copies the response into the caller buffer, and passes remote reads through `request::Request` so proxy-aware context and retry behavior can apply.

## State and Persistence Behavior
`HttpProxy` stores address, path, cloned client state, and optional metrics. Local mode owns a one-thread Tokio runtime and Hyper Unix client. Remote mode owns a shared request object that wraps connection/proxy state. No data is cached in this backend; persistence is delegated to the proxy service.

## Dependencies and Integration Points
The module integrates `hyper`, `hyperlocal`, `hyper-util`, `http-body-util`, Tokio runtime creation, and the common `BlobBackend`/`BlobReader` traits. Remote mode depends on `connection.rs` and `request.rs`, including Dragonfly proxy behavior when enabled.

## Risks
`range_str_for_header` underflows for `Some(0)` because it computes `offset + len - 1`; zero-length reads could panic in debug or produce an invalid range in release. Local mode ignores per-blob paths in the Hyper URI and always requests `/`, implying the local proxy must infer the blob some other way or this is a behavioral gap. `metrics()` unwraps optional metrics, so callers must provide an ID in production paths. Test servers run infinite accept loops on fixed `/tmp/nydus-test-local-http-proxy.sock` and port `9977`, which can conflict or linger during test runs.

## Test Signals
The integration-style test starts local Unix and remote TCP Hyper servers, validates HEAD content length, validates ranged GETs, and verifies full-buffer reads through both client modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/http_proxy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/localdisk.rs -->
# sources/cloud-native/nydus/storage/src/backend/localdisk.rs

## Purpose
This module implements a local block-device or disk-image backend. It maps blob IDs to byte ranges on a device file, optionally discovering those ranges from GPT partitions.

## Important APIs, Types, and Functions
`LocalDisk` is the backend and `LocalDiskBlob` is the reader. `LocalDisk::new` canonicalizes and opens the configured device path, captures capacity, creates metrics, and optionally scans GPT. `add_blob` manually registers a blob offset and length when not in GPT mode. `get_blob` resolves a blob from the in-memory map or GPT fallback. Under `backend-localdisk-gpt`, `scan_blobs_by_gpt` reads partitions and derives blob IDs from partition names and GUIDs, while `truncate_blob_id` supports legacy 32-byte GPT names.

## Control Flow
Reads use `nix::sys::uio::pread` against cloned file descriptors. `try_read` returns `0` when the requested offset is at or beyond blob length and clamps reads to the remaining blob length. `readv` builds iovecs from FUSE volatile slices and calls a utility `readv` at the absolute device offset. `expect_exact_read` returns `false`, allowing EOF short reads without remote-style retry errors.

## State and Persistence Behavior
Persistent data is the underlying disk image or block device. Runtime state is an `RwLock<HashMap<String, Arc<LocalDiskBlob>>>`, the open device file, capacity, GPT mode flag, and metrics. Manual `add_blob` state is in-memory only and must be reconstructed by higher layers on restart unless GPT discovery is used.

## Dependencies and Integration Points
The backend consumes `nydus_api::LocalDiskConfig`, FUSE `FileVolatileSlice`, `nix` pread/uio, optional `gpt`, and common backend traits. It shares metrics across all blob readers.

## Risks
`readv` validates against the sum of all input slice lengths rather than the `max_size` actually consumed, so callers with larger buffers and smaller `max_size` can be rejected near EOF. GPT mode disallows `add_blob`, making configuration mode important. Lock poisoning is unhandled via `unwrap`. GPT blob ID derivation depends on partition naming conventions and legacy truncation, which can collide in pathological cases.

## Test Signals
Tests cover invalid construction, manual blob registration bounds, duplicate detection, EOF short reads, and GPT blob ID truncation when the feature is enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/localdisk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/localfs.rs -->
# sources/cloud-native/nydus/storage/src/backend/localfs.rs

## Purpose
This module implements a local filesystem blob backend. It opens blob files from either a fixed `blob_file`, a primary directory, or alternative directories.

## Important APIs, Types, and Functions
`LocalFs` is the backend and `LocalFsEntry` is the reader. `LocalFs::new` validates that either `blob_file` or `dir` is configured and requires an ID for metrics. `get_blob_path` resolves a blob path, preferring `blob_file`, then primary `dir`, then `alt_dirs`. `get_blob` caches open file readers by blob ID. `LocalFsEntry` implements `blob_size`, `try_read`, `readv`, and opts out of exact-read enforcement.

## Control Flow
When a reader is requested, the backend first checks the entries map. On a miss it resolves and canonicalizes the path, opens the file read-only, then inserts an `Arc<LocalFsEntry>` under a write lock with a second check to avoid duplicate opens. Reads use `pread` and vector reads use the shared `readv` utility.

## State and Persistence Behavior
Persistent state is the local filesystem file content. Runtime state includes configured path strings, alternate directories, metrics, and an `RwLock` cache of open files. Once a blob is cached, later changes to path resolution will not affect that blob ID until the backend is recreated.

## Dependencies and Integration Points
The backend integrates `nydus_api::LocalFsConfig`, Unix file descriptors, FUSE volatile slices, and the common backend traits. It is a local backend and therefore relies on short-read semantics rather than retrying for exact buffer length.

## Risks
The `is_valid` closure is written as though it receives a directory, but some calls pass a full blob path; this can produce surprising primary-directory checks, especially when `alt_dirs` are present. Zero-byte files are treated as invalid during directory search, which is intentional in tests but may surprise deployments that use valid empty blobs. Lock poisoning is unhandled. Cached file descriptors can keep reading old content after files are replaced on disk.

## Test Signals
Tests cover invalid config, blob path resolution, skipping zero-byte alt-dir candidates, fixed `blob_file` priority, missing paths, reader caching, scalar and vector reads, empty reads, and EOF behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/localfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/mod.rs -->
# sources/cloud-native/nydus/storage/src/backend/mod.rs

## Purpose
This is the central backend abstraction module. It declares feature-gated backend submodules, common error/result types, global pause/QPS controls, request context, retry policy, the `BlobReader` and `BlobBackend` traits, and `BlobBufReader`.

## Important APIs, Types, and Functions
`RequestSource` distinguishes on-demand and prefetch traffic. `BackendContext` carries method, URL, proxy routing flags, Dragonfly SDK flags, request source, and last error. `BackendError` aggregates backend-specific errors plus copy and request errors. `retry_op` is the proxy-aware retry loop. `BlobReader` defines `blob_size`, `try_read`, context-aware reads, exact-read policy, `read`, `read_all`, `readv`, optional streaming reads, metrics, and retry limit. `BlobBackend` defines lifecycle, metrics, and reader acquisition. `BlobBufReader` adapts a `BlobReader` into a buffered `Read` implementation.

## Control Flow
Remote-style reads go through `BlobReader::read_with_source`, which builds a `BackendContext`, calls `retry_op`, and enforces exact buffer length unless the reader overrides `expect_exact_read`. Prefetch gets fewer retries and randomized backoff; on-demand gets more retries and may fall back from proxy to source under a global QPS limiter. Proxy forbidden errors stop immediately, proxy rate limits stop prefetch but force on-demand source fallback, and Dragonfly SDK internal errors disable SDK mode for retry. `readv` either maps a single FUSE slice directly or reads into an allocated buffer and copies out. `BlobBufReader::read` refills from the backend and reports unexpected EOF if a refill returns zero before the expected size is exhausted.

## State and Persistence Behavior
This module owns two lazy globals: `BACKEND_QPS_LIMITER` at 1 QPS for source fallback and `BACKEND_PAUSER` for pausing backend requests. `BackendContext` is per request and mutable across retries. Metrics are updated around every retry attempt, and terminal errors are pushed into `ERROR_HOLDER`.

## Dependencies and Integration Points
The module gates backend implementations by Cargo features and ties them to shared traits used elsewhere in storage. It depends on FUSE volatile slices, `nydus_utils::metrics`, allocation/copy utilities, and local `pauser`/`qps` modules. Dragonfly proxy status helpers are compiled only when the relevant features are enabled.

## Risks
The documented `retry_limit` hook is not used by `retry_op`; retry counts are hardcoded by request source. Exact-read enforcement protects remote backends from silent short reads but can turn legitimate EOF into errors if a backend forgets to override `expect_exact_read`. `read_all` creates a new default context for each loop and may not propagate original request source. Global QPS and pauser state affects all backend users in the process.

## Test Signals
Tests cover error display, basic reader behavior, `read_all`, retry counts, buffered reader refills and EOF, default context, request source display, proxy error helper fallbacks, and context propagation through `read_with_source`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/object_storage.rs -->
# sources/cloud-native/nydus/storage/src/backend/object_storage.rs

## Purpose
This module is the generic object-storage backend foundation used by OSS and S3-like implementations. It separates provider-specific URL/signing state from common blob read, size, stream, metrics, and shutdown behavior.

## Important APIs, Types, and Functions
`ObjectStorageState` requires `url`, `sign`, and `retry_limit`. `ObjectStorage<T>` is the backend wrapper over `request::Request`, provider state, metrics, and optional ID. `ObjectStorageReader<T>` implements `BlobReader`. `ObjectStorageError` covers auth/signing, header construction, transport, and response validation errors. `new_object_storage` wires request, state, metrics, and ID into the generic backend.

## Control Flow
`blob_size` signs and sends a HEAD request, then parses `Content-Length`. `try_read_ctx` builds a closed byte range, signs GET, calls the request layer with the provided context, and copies the response body to the caller buffer. `try_stream_read` signs GET and omits `Range` at offset `0` so Dragonfly can cache the full blob; for nonzero offsets it sends an open-ended range. `get_reader` requires metrics to exist and returns unsupported otherwise.

## State and Persistence Behavior
The backend does not cache object data. It stores shared request/client state, immutable provider state, optional metrics, and reader-local blob IDs. Persistent data lives in the remote object store, while request retries and proxy behavior are delegated to the request/connection layers.

## Dependencies and Integration Points
This module depends on `reqwest` headers/methods, common backend traits, `request.rs`, and provider states such as `OssState`. It is where object-storage providers inherit Dragonfly proxy behavior, exact-read enforcement, and metrics.

## Risks
`try_read_ctx` computes `offset + buf.len() as u64 - 1`, which underflows for zero-length buffers and can overflow for extreme offsets. `blob_size` requires `Content-Length`; chunked or metadata-poor providers fail. `get_reader` fails when constructed without metrics, while constructors allow `id: None`. Stream status checking is probably redundant when `catch_status` is true but remains defensive.

## Test Signals
Tests use a mock `ObjectStorageState` and local TCP server to cover error formatting, backend lifecycle, missing metrics, retry limit propagation, HEAD size reads, missing content length, ranged reads, signing failures, and stream reads with and without Range headers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/object_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/oss.rs -->
# sources/cloud-native/nydus/storage/src/backend/oss.rs

## Purpose
This file implements the Aliyun OSS provider state and constructor on top of generic object storage. It handles OSS URL/resource construction and HMAC-SHA1 request signing.

## Important APIs, Types, and Functions
`OssState` stores access key ID/secret, scheme, object prefix, endpoint, bucket name, and retry limit. `OssState::resource` builds canonical OSS resource paths. `sign_by_url` creates a one-hour pre-signed query string. The `ObjectStorageState` implementation provides `url`, `sign`, and `retry_limit`. `pub type Oss = ObjectStorage<OssState>` exposes the backend type. `Oss::new` converts `OssConfig` to `ConnectionConfig`, constructs `Connection` and `request::Request`, initializes state, and attaches optional metrics.

## Control Flow
`url` prepends `object_prefix` to the object key, creates `scheme://bucket.endpoint/object`, and mirrors optional query strings into both the canonical resource and full URL. `sign` formats the OSS string-to-sign from method, empty MD5/content-type fields, current HTTP date, optional `x-oss-*` canonical headers, and canonical resource; it computes HMAC-SHA1, base64 encodes it, and inserts `Date` and `Authorization` headers.

## State and Persistence Behavior
`OssState` is immutable after construction and shared through `Arc` by `ObjectStorage`. Secrets are stored as plain `String`s in process memory. No blob data is cached here; persistence is in OSS and connection/proxy state.

## Dependencies and Integration Points
The module depends on `base64`, `hmac`, `sha1`, `httpdate`, `reqwest::Method`, `nydus_api::OssConfig`, and the shared connection/request/object-storage layers. It also uses the local URL encoding helper for pre-signed signatures.

## Risks
The current signing path leaves content MD5 and content type empty, which matches simple GET/HEAD but may not generalize. `object_prefix` is concatenated directly with object keys, so configuration must include any desired slash. Secrets have no redaction wrapper in `Debug` for `OssState`, although connection config logging is elsewhere. `Oss::new(None)` succeeds but later `get_reader` fails due to missing metrics.

## Test Signals
Tests cover resource and URL construction, request signing including OSS headers, constructor behavior with and without IDs, retry limit propagation, pre-signed URL creation, and preservation of path separators.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/oss.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/pauser.rs -->
# sources/cloud-native/nydus/storage/src/backend/pauser.rs

## Purpose
This utility module implements a process-local pauser that can block participating threads until a configured pause deadline expires or is cleared.

## Important APIs, Types, and Functions
`Pauser` is a cloneable wrapper around `Arc<Mutex<PauserInner>>` and `Arc<Condvar>`. `set_pause` sets or replaces the pause deadline. `clear_pause` removes it. `wait` blocks until no pause is active and returns the time spent waiting. `is_paused` and `status` expose non-blocking state checks. `Default` delegates to `new`.

## Control Flow
Callers invoke `wait` at participation points. It locks state, compares `pause_until` with `Instant::now`, clears expired pauses, or waits on the condition variable for the remaining duration. `set_pause` and `clear_pause` notify all waiters after updating state.

## State and Persistence Behavior
All state is in-memory. There is no durable pause state across process restarts. A new pause replaces any existing deadline regardless of whether it is shorter or longer.

## Dependencies and Integration Points
The global `BACKEND_PAUSER` in `mod.rs` exposes this mechanism to backend users. The module only depends on standard library synchronization and time primitives.

## Risks
Callers must explicitly call `wait`; the pauser does not intercept backend operations automatically. `is_paused` and `status` do not clear expired pause state, so they can report not paused while leaving `pause_until` set until a later `wait` or replacement. Mutex poisoning is unhandled via `unwrap`.

## Test Signals
Tests cover creation, setting, clearing, immediate waits, timed waits, concurrent wait release, repeated pauses, pause replacement, concurrent setters, non-blocking status, and late pause behavior after waiters have already passed.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/pauser.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/proxy.rs -->
# sources/cloud-native/nydus/storage/src/backend/proxy.rs

## Purpose
This feature-gated module integrates the Dragonfly proxy SDK. It provides constants for Dragonfly headers, maps SDK errors into backend proxy error classes, exposes a singleton Tokio runtime, adapts async SDK readers to blocking `Read`, and caches SDK clients by scheduler endpoint.

## Important APIs, Types, and Functions
Header constants include priority, P2P, output path, piece length, hard link, task ID content, prefetch, and error type names. `ProxyError` classifies common, internal, rate-limited, and forbidden failures. `runtime()` returns the static multi-thread runtime. `SyncAdapter<R>` converts `AsyncRead + Unpin` to blocking `Read`. `ProxySDKClient::request` builds a Dragonfly `GetRequest` and executes it. `ProxySDKClients::get` returns or creates a cached `ProxySDKClient` for an endpoint.

## Control Flow
SDK requests use a five-second timeout, optional priority, task-ID-based digest calculation, and no SDK retries (`max_retries(0)` at client construction). Backend errors can be converted into synthetic successful `GetResponse` values when `catch_status` is false. Proxy 429 and 403 statuses map to dedicated variants so the higher-level retry policy can rate-limit fallback or stop immediately. Client creation uses double-checked locking around a global endpoint map.

## State and Persistence Behavior
State is process-global: one Tokio runtime and one `RwLock<HashMap<String, Arc<ProxySDKClient>>>`. Client state persists for the process lifetime and is not evicted. No on-disk state is managed here; Dragonfly and dfdaemon own any external cache.

## Dependencies and Integration Points
The module is enabled by `backend-dragonfly-proxy` and depends on `dragonfly-client-util`, Tokio, reqwest headers/status, and the shared retry helpers in `mod.rs` through `BackendError::is_proxy_*` methods.

## Risks
`runtime()` panics if runtime initialization failed. `SyncAdapter::read` blocks on the global runtime, which can deadlock if misused from within the same runtime context. The endpoint client cache has no eviction. Error classification depends on SDK error shapes and status propagation. Tests that touch invalid scheduler endpoints depend on current SDK error messages.

## Test Signals
Tests cover blocking adapter reads, empty and partial reads, runtime singleton behavior, runtime spawning, constants, error variants, invalid endpoint handling, and scheduler connection failure surfacing.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/proxy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/qps.rs -->
# sources/cloud-native/nydus/storage/src/backend/qps.rs

## Purpose
This module implements a simple cloneable token-bucket QPS limiter used by backend retry logic to throttle source-backend fallback requests.

## Important APIs, Types, and Functions
`QpsLimiter::new` creates a limiter with capacity and refill rate equal to the configured QPS. `try_acquire` and `try_acquire_tokens` attempt non-blocking token consumption. `acquire` and `acquire_tokens` block until enough tokens are available and return whether waiting occurred. `current_tokens` reports refilled available tokens, and `qps` reports the configured rate. `QpsLimiterInner::refill` computes elapsed time and caps tokens at capacity.

## Control Flow
Fast paths lock, refill, and consume tokens if available. Blocking paths first try the fast path, then wait on a condition variable with a timeout computed from token shortage and rate. There is no producer thread; token availability advances when callers wake by timeout or inspect the limiter.

## State and Persistence Behavior
All state is in-memory inside `Arc<Mutex<QpsLimiterInner>>`. Clones share token state. The limiter does not persist across process restarts and does not expose dynamic reconfiguration.

## Dependencies and Integration Points
`BACKEND_QPS_LIMITER` in `mod.rs` creates a global 1 QPS limiter for direct source fallback after proxy rate limits or final on-demand retry. The implementation uses only standard synchronization/time primitives.

## Risks
`acquire_tokens` with `count > capacity` can block forever because the bucket can never accumulate enough tokens. The condition variable is only notified by timeout, not by explicit refill events, which is acceptable but means wait granularity depends on timeout calculation. Floating-point token accounting can cause small timing variance. Mutex poisoning is unhandled.

## Test Signals
Tests cover construction, initial tokens, exhaustion, refill timing, blocking acquisition, multi-token acquisition, approximate QPS accuracy, low-QPS behavior, concurrent acquisition, and return values indicating rate-limited waits.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/storage/src/backend/qps.rs -->
