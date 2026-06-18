# sources/cloud-native/nydus/storage/src/backend/request.rs

## Purpose
`request.rs` is the unified request routing layer used by storage backends. It wraps `Connection`, injects common/custom headers, records diagnostic request context, and chooses between direct HTTP, HTTP proxy, and feature-gated Dragonfly SDK proxy paths. It also normalizes HTTP and Dragonfly SDK responses behind one `Response` enum.

## Important APIs, Types, And Functions
`RequestError` distinguishes generic routing errors, `ConnectionError`, and optional Dragonfly `ProxyError`. `Response` wraps `reqwest::blocking::Response` or feature-gated `GetResponse` and exposes `status`, `headers`, `reader`, `text`, and `copy_to`. `Request::new` stores the connection, proxy config, parsed custom headers, prefetch flag, and dynamic-config id while registering initial proxy settings in `nydus_utils::config`.

`Request::call` is the main API. It takes method, URL, optional query/form/body, mutable headers, status-catching preference, backend context, and a temporary proxy-disable flag. `is_success_status` treats 2xx and 3xx as success, matching backend redirect-handling needs. `parse_custom_headers_from_env` adds `User-Agent: nydusd/1.0.0` and accepts valid `NYDUS_HEADER_*` environment variables.

## Control Flow
Every call first extends caller headers with configured custom headers and populates `BackendContext.method`, `url`, and proxy booleans. If proxying is disabled by request, context, or absent proxy URL, the request goes directly to `Connection::call_with_proxy_control`; auth calls use this path to avoid proxy URL rewriting. With `backend-dragonfly-proxy`, a scheduler endpoint and GET method can route to `ProxySDKClients::request`, with Dragonfly priority derived from `RequestSource`. If SDK is unavailable or disabled, the call falls through to HTTP proxy mode and injects Dragonfly priority/use-p2p headers before using `Connection::call`.

After an HTTP proxy response, feature-gated logic inspects the Dragonfly error-type header. A 429 maps to `ProxyError::TooManyRequests`, a 403 maps to `ProxyError::Forbidden`, and other proxy-marked statuses become common errors. Without the feature, the module is a direct/proxy wrapper around `Connection`.

## State And Persistence Behavior
`Request` keeps immutable construction-time proxy config plus a config id for dynamic reads of the Dragonfly scheduler endpoint. `dragonfly_scheduler_endpoint` calls `nydus_utils::config::get_changed`, allowing scheduler hot reload without rebuilding the request. No file state is persisted. `shutdown` delegates to the shared `Connection`, and `is_shutdown` reads the connection atomic flag.

## Dependencies And Integration Points
The module depends on `reqwest` method/status/header types, `nydus_api::ProxyConfig`, `backend::connection`, `BackendContext`, optional `backend::proxy`, optional Dragonfly client types, and `nydus_utils::config`. It is used by registry, S3/object storage, and other backend implementations as the common transport abstraction.

## Risks And Edge Cases
Custom environment headers are parsed only at construction time; later environment changes do not apply. Header names/values that fail parsing are silently ignored. Header extension can overwrite caller headers with environment-provided headers, including `User-Agent`. SDK proxy mode rejects non-GET methods; callers must disable SDK or avoid proxying for writes/auth. Dynamic config uses the original configured endpoint as the comparison baseline each call, which is fine for fetching current values but means change reporting is not a stored state transition in this object.

## Test Signals
Tests cover environment header parsing, success-status boundaries, request construction, proxy-mode checks, scheduler endpoint hot reload, shutdown state, direct and proxy-disabled calls, custom header injection, feature-gated SDK response adapters, SDK method rejection, Dragonfly HTTP proxy error header translation, Dragonfly priority headers for prefetch/on-demand, HTTP response helpers, and debug formatting. Tests exercise routing behavior with local/mocked HTTP facilities rather than external network services.
