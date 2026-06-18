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
