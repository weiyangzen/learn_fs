# sources/cloud-native/soci-snapshotter/fs/remote/blob.go

Purpose: implements the lazy remote blob abstraction used by layer readers: range reads, fetched-size accounting, health checks, refresh, and close state over a fetcher.

Important APIs and flow: `Blob` exposes connectivity check, size, fetched size, `ReadAt`, refresh, and close. `makeBlob` constructs a `blob` with fetcher, size, last-check state, interval, and resolver. `Refresh` resolves a new fetcher through the resolver and swaps it only if size matches. `Check` skips network checks until `checkInterval` expires, then calls `fetcher.check` and updates `lastCheck` on success. `ReadAt` bounds empty/out-of-range reads, builds a requested `region`, applies options, fetches the range into a `bytesWriter`, adjusts returned length for EOF, and returns bytes read. `fetchRegion` snapshots the current fetcher, performs a retryable fetch, iterates multipart/singlepart results, copies exactly the requested region size, updates last-check time, and merges fetched regions into `regionSet`.

State and persistence: protects fetcher, last check time, fetched region set, and closed flag with mutexes. It does not cache data itself; fetched bytes flow to the caller and fetched-size state tracks covered ranges only.

Dependencies and integration: depends on `remote.fetcher` implementations from `resolver.go`, Docker hosts/reference types for refresh, OCI descriptors, and `regionSet` from `util.go`. Used by `layer.layer.ReadAt`, state-file reporting, and connection checks.

Risks and test signals: fetched-size accounting marks an entire requested region fetched after successful copy, not individual multipart subregions. `fetchRegion` copies `reg.size()` for every part rather than the part's returned region, which is fine for current single requested region use but would be risky if multiple disjoint regions were passed. Tests cover normal reads, broken body/header, check intervals, and concurrent fetch behavior; they do not test refresh size mismatch.
