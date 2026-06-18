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
