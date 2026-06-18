<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/fetcher_test.go

## Purpose
Validates Docker fetcher transport behavior: ranged reads, parallel chunk reads, content encoding, retry behavior, error formatting, and limiter cleanup.

## Important APIs, Types, And Functions
- `TestFetcherOpen` tests serial offset reads and server `Content-Range` handling.
- `TestFetcherOpenParallel` tests concurrent range fetching with configurable chunk size and max downloads.
- `TestFetcherOpenParallel_CloseAfterCopyError` ensures closing a parallel reader after downstream copy failure does not block on unfinished range workers.
- `TestContentEncoding` validates identity, zstd, gzip, deflate, and chained encodings.
- `TestDockerFetcherOpen` covers unexpected registry statuses, Docker error bodies, and retry counts for timeout/too-many-requests/5xx paths.
- `TestDockerFetcherOpenLimiterDeadlock` verifies limiter capacity is released when opening fails during decoding.
- `parseRange` and `httpRange` are test helpers implementing enough RFC 7233 range parsing for local servers.

## Control Flow
Tests create local HTTP servers that vary `Range`, `Content-Range`, `Content-Length`, status codes, and encodings. They construct a `dockerFetcher` with local `RegistryHost` data, call `open`, consume the reader, and compare output bytes or errors. Parallel tests inject transient failures after specific offsets to verify retry policy and error propagation.

## State And Persistence
Test state is local: random deterministic content buffers, atomic failure flags, a semaphore limiter, and server-side toggles. No persistent content store is used.

## Dependencies And Integration Points
Exercises the fetcher with `httptest`, `semaphore.Weighted`, `transfer.ImageResolverPerformanceSettings`, compression libraries, and Docker error serialization from the package.

## Risks And Edge Cases
The tests highlight important operational risks: remote registries may ignore range requests, return wrong ranges, omit content length, close early, or send unsupported/corrupt encodings. Parallel fetch cleanup is especially important because leaked goroutines or unreleased limiter slots can deadlock future pulls.

## Test Signals
This is the main behavioral safety net for fetcher changes. A notable regression guard is the limiter-deadlock test, which confirms failed gzip initialization releases the limiter so a second open can proceed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_test.go -->
