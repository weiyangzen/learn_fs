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
