# sources/cloud-native/nydus/rafs/src/prefetch.rs

## Purpose
`prefetch.rs` implements a streaming blob prefetcher for RAFS images. Instead of issuing per-chunk range requests, it groups chunks by blob and performs rangeless/streaming reads from each blob, then extracts chunk byte ranges by compressed offset and persists them through the configured `BlobCache`. The module is explicitly aimed at Dragonfly proxy efficiency: one streaming connection per blob replaces many small range requests.

## Important APIs, Types, And Functions
`BlobPrefetcher::new()` builds an `Arc<BlobPrefetcher>` from a `RafsSuper`, a cache vector indexed by blob index, thread count, and optional bandwidth limit. `start()` spawns the controller thread, `stop()` sets a stop flag and waits up to five seconds, and `progress()` exposes atomic counters. Internal `BlobWork` holds one `BlobInfo` and compressed-offset-sorted `BlobChunkInfo` entries. `PrefetchProgress` tracks total and completed blobs/chunks/bytes. `RateLimiter` is a token bucket with two seconds of capacity. Core internals are `build_blobs()`, `prefetch_all()`, `prefetch_one_blob()`, and `stream_and_cache()`.

## Control Flow
The controller traverses the RAFS tree from `root_ino`, collecting regular-file chunks and descending directories with `get_child_by_index()`. Chunks are grouped by `blob_index` and keyed by `compressed_offset`, which both deduplicates same-offset chunks and naturally sorts streaming order. `prefetch_all()` creates a bounded worker pool, sends each `BlobWork` with its matching cache, and workers retry each blob up to `DEFAULT_MAX_RETRY`. `prefetch_one_blob()` checks cache readiness, finds the first missing chunk, calls `BlobReader::stream_read(start_offset, RequestSource::Prefetch)`, and delegates stream matching. `stream_and_cache()` accumulates 1 MiB reads, matches complete chunk ranges inside the buffer, calls `cache_chunk_data()`, updates counters, trims old bytes while keeping the largest chunk window, and exits when all chunks are done or the stream passes the last chunk end.

## State, Persistence, And Dependencies
State is process-local and concurrency-oriented: `State` owns the stop flag, counters, thread handle, condvar, worker count, rate limiter, and retry limit. Persistence happens only via the external `BlobCache`; the prefetcher itself does not write metadata. It depends on `nydus_storage` cache/backend/device traits and RAFS inode/superblock metadata.

## Integration Points
The cache vector must align with RAFS blob indexes. Backend implementations must support `stream_read`; cache implementations must expose `ChunkMap` and `cache_chunk_data()`. Logs use standard `info!`, `warn!`, and `error!` macros.

## Risks
Deduplication by compressed offset can collapse distinct chunk IDs if different chunks share an offset. The retry loop treats per-chunk cache errors inside `stream_and_cache()` as warnings, so a blob may be counted as prefetched even if some chunks failed to cache. `total_bytes` is never populated. `stop()` may detach the controller thread after timeout.

## Test Signals
The in-file tests cover rate limiter behavior, progress defaults, stream accumulation across read boundaries, pre-marked chunks, cache errors, stop behavior, fully cached blobs, empty blobs, and constructor defaults. These tests are strong for local buffer/control logic but do not exercise real backend streaming, RAFS traversal, or Dragonfly behavior.
