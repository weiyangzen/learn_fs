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
