# sources/cloud-native/stargz-snapshotter/fs/remote/blob_test.go

## Purpose
Tests remote blob byte-range reads, cache population, multipart and single-range transports, failure handling, concurrent fetch coalescing, and health-check timing.

## Important APIs, Types, And Functions
`TestReadAt` drives the main matrix. `cacheAll`, `checkRead`, `checkCache`, and `checkAllCached` verify cache state. `TestFailReadAt` covers HTTP errors, truncated bodies, and missing headers. `TestParallelDownloadingBehavior` checks `fetchRange` singleflight behavior. `multiRoundTripper`, `failRoundTripper`, `brokenBodyRoundTripper`, and `brokenHeaderRoundTripper` simulate registries.

## Control Flow
The matrix varies request sizes, offsets, blob sizes, prefetch size, cache state, and multi-range support. Tests build `blob` instances with memory cache and fake HTTP fetchers, seed cache where needed, perform `ReadAt` or `Cache`, and compare returned data plus full chunk cache contents. Parallel tests launch three goroutines with identical, overlapping, or disjoint region maps and assert round-trip counts.

## State And Persistence
Only in-memory cache and mock transport counters are used. `callsCountRoundTripper.count` is atomic to support concurrent assertions.

## Dependencies And Integration
Depends on `cache.NewMemoryCache`, HTTP response construction, multipart writers, and the production `blob`/`httpFetcher` internals. It gives direct signals for registry range behavior without real network access.

## Risks And Test Signals
Strong signals are byte-accurate partial reads, chunk cache completeness, fallback from multi-range-disabled transports, error returns on malformed registry responses, singleflight behavior for identical requests, and `Check` avoiding work until expiration. Gaps include no real registry auth, no disk cache implementation, and limited stress for huge header/range lists.
