# sources/cloud-native/nydus/storage/src/backend/registry.rs

## Purpose
`registry.rs` implements the `BlobBackend` for OCI/Docker registry-backed blobs. It turns a `RegistryConfig` into a `Registry` object, creates per-blob `RegistryReader`s, handles registry authentication challenges, reads blob byte ranges, follows registry redirects to object storage, caches redirect/auth state, and exposes metrics/retry metadata to the storage layer.

## Important APIs, Types, And Functions
`RegistryError` is the backend-specific error surface and converts into `BackendError`, preserving feature-gated Dragonfly proxy errors as request errors so retry classification can still see forbidden/rate-limit cases. `RegistryState` holds shared backend configuration and mutable caches: scheme, host, repo, retry limit, auth caches, redirect cache, bearer token expiration, and cached bearer challenge parameters. `Registry::new` validates base64 basic auth, builds `Connection` and `request::Request`, initializes `RegistryState`, registers dynamic config auth, and starts the refresh thread.

`RegistryReader` implements `BlobReader` with `blob_size`, `try_read_ctx`, and `try_stream_read`. The internal `request` method handles the standard 401 challenge flow for Basic and Bearer auth. `_try_read` handles ranged blob reads, redirect caching, redirect URL rewriting, HTTPS-to-HTTP fallback when `skip_verify` allows it, and response copying into caller buffers. `_stream_read` opens a streaming response and intentionally omits `Range` for offset zero so Dragonfly can cache the whole blob.

`Cache` and `HashCache<T>` provide lock-protected string/hash caches for auth headers, config-auth snapshots, method fallback, and redirects. `First` serializes only the initial request across concurrent readers so the first request can populate shared auth state before the startup surge of blob reads proceeds. `TokenResponse`, `BasicAuth`, `BearerAuth`, and `Auth` model registry authentication.

## Control Flow
Construction flows through `Registry::new`: config to `ConnectionConfig`, `Connection::new`, `Request::new`, auth trimming/validation, `RegistryState` allocation, and background token refresh. A reader is cheap and shares state/request/metrics. Reads call through `First::handle_force`, then either `HEAD /v2/<repo>/blobs/<digest>` for size or `GET` with a `Range` header for data. If no redirect is cached, the reader hits the registry API path, optionally authenticates via a 401 challenge, handles TLS fallback, follows 3xx `location`, optionally rewrites scheme/host, and then reads from the redirected URL. If a cached redirected URL returns 401/403, it is invalidated and the read retries once through the registry API.

Auth control flow starts with any cached `Authorization` header. On 401 with an auth header, the request is retried without the stale header to get a correct `www-authenticate` challenge. Bearer token fetching tries POST first unless GET was previously cached for that host; on POST failure it retries GET and remembers GET. Successful auth headers are cached for later registry requests.

## State And Persistence Behavior
No durable state is written by this file. Mutable process state includes `cached_auth`, dynamic-config auth snapshots, redirect URL cache keyed by blob id, cached GET-vs-POST auth method, bearer token expiry, and cached bearer challenge. The refresh thread polls config and token expiry every five seconds until `Request::shutdown` is observed. `Scheme` is an atomic HTTPS/HTTP switch, so fallback changes process-wide behavior for the registry instance. Metrics are allocated per registry id and released in `Drop`.

## Dependencies And Integration Points
This module depends on `reqwest` headers/status/methods, `url::Url`, `arc_swap`, `base64`, `serde_json`, `nydus_api::RegistryConfig`, `nydus_utils::config`, and `BackendMetrics`. It integrates with `backend::connection` for transport, `backend::request` for direct/proxy/Dragonfly routing, `BlobBackend`/`BlobReader` traits for cache consumers, and optional Dragonfly proxy error typing.

## Risks And Edge Cases
`parse_auth` is intentionally simple and splits challenge parameters on `",` and `=`, which is vulnerable to unusual quoted values containing delimiters. Redirect caching assumes redirected URLs are reusable until 401/403; other expiry/failure modes will surface as read errors rather than cache invalidation. HTTPS-to-HTTP fallback mutates shared scheme for the backend and is only gated by `skip_verify`; once set, later reads use HTTP. The refresh thread is detached and only exits after shutdown polling. `HeaderValue::to_str().unwrap()` and header parsing `unwrap()` can panic if a registry returns invalid header values in paths that are otherwise expected.

## Test Signals
The local test module covers cache helpers, fallback scheme behavior, auth config validation and dynamic updates, URL construction, auth challenge parsing, `First` concurrency/renewal behavior, token response decoding, error conversion/display, `respond` status handling, config auth helpers, fallback error classification, and stream-read unsupported behavior. The tests are mostly unit-level with mocked/simple objects; live registry redirect/auth integration is not covered here.
