# sources/cloud-native/stargz-snapshotter/fs/remote/blob.go

## Purpose
Implements `Blob`, the lazy remote byte-range reader and cache manager for layer blobs. It handles cache-first reads, HTTP/IPFS handler-backed fetching, chunk-aligned prefetching, health checks, refresh, fetched byte accounting, and singleflight coalescing.

## Important APIs, Types, And Functions
`Blob` exposes `Check`, `Size`, `FetchedSize`, `ReadAt`, `Cache`, `Refresh`, and `Close`. `makeBlob` constructs internal state. `ReadAt` maps arbitrary reads to chunk-aligned `region`s, `prepareChunksForRead` tries cache and schedules misses, `fetchRange` coalesces identical range misses with `singleflight`, `fetchRegions` streams multipart results into cache and readers, and `cacheChunkData` commits fetched chunks.

## Control Flow
Reads first reject closed blobs and empty/out-of-range requests, compute aligned regions, and fill any cache hits directly into the caller buffer. Misses are represented by writers that copy only the requested subsection while the whole chunk is cached. Fetches use the current fetcher snapshot, request missing regions, parse multipart/singlepart responses, update `lastCheck`, and verify every requested region was delivered. Shared fetch callers copy the completed chunks from cache.

## State And Persistence
Persistent data lives in the supplied `cache.BlobCache`. In-memory state tracks fetcher, blob size, chunk sizes, check interval, fetch timeout, fetched `regionSet`, closed flag, and locks. `FetchedSize` sums merged fetched regions, not cache contents discovered before this process.

## Dependencies And Integration
Depends on `remote.fetcher` from `resolver.go`, `cache.BlobCache`, OCI descriptors, source registry hosts, errgroup, and singleflight. It is the remote content backend used by snapshotter filesystem code when source labels resolve to registry or custom handlers.

## Risks And Test Signals
Risks include incomplete multipart bodies, cache writer commit errors, stale signed redirect URLs, singleflight key granularity, and context/fetch timeout behavior. `blob_test.go` covers read/cache matrices, broken bodies/headers, parallel download coalescing, and check interval updates.
