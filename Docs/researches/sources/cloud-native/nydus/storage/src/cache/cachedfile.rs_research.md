# sources/cloud-native/nydus/storage/src/cache/cachedfile.rs

## Purpose
`cachedfile.rs` implements the common local file-backed blob cache object used by userspace file cache and fscache-based cache managers. `FileCacheEntry` reads blob chunks from local cache files when possible, fetches/decompresses/decrypts/validates backend data on misses, persists ready chunks, manages prefetch, supports optional at-rest cache encryption, and integrates optional content-addressable deduplication.

## Important APIs, Types, And Functions
`FileCacheMeta` owns asynchronous or synchronous loading of `BlobCompressionContextInfo` with retry/backoff and a shared error flag. `BlobCCI` wraps blob compression context access, especially for batch chunks where compressed size comes from blob metadata rather than the chunk object. `FileCacheEntry` is the central cache object and implements `AsRawFd`, `BlobCache`, and `BlobObject`.

Key persistence helpers are `persist_cached_data`, `persist_chunk_data`, `delay_persist_chunk_data`, `cache_chunk_data`, and `_update_chunk_pending_status`. Range/read helpers include `extend_pending_chunks`, `strip_ready_chunks`, `get_blob_range`, `prefetch_range`, `do_fetch_chunks`, `read`, `read_iter`, `dispatch_one_range`, `dispatch_cache_fast`, `dispatch_cache_slow`, `dispatch_backend`, `read_single_chunk`, and `read_file_cache`. `DataBuffer`, `Region`, and `FileIoMergeState` support buffer ownership and IO-region coalescing.

## Control Flow
Reads enter `BlobCache::read`. Single-entry requests dispatch directly; multi-entry requests are merged with `BlobIoMergeState` and processed range by range. `dispatch_one_range` checks and marks chunk readiness/pending state. Ready plaintext chunks without validation use `CacheFast` and read directly from the cache file into caller buffers. Chunks needing validation/decryption/decompression or non-direct maps use `CacheSlow`, which loads and validates a whole chunk before copying the requested segment. Missing chunks use `Backend`, where contiguous compressed ranges can be extended for read amplification, fetched through `BlobCache::read_chunks_from_backend`, decompressed by the trait helper, copied to user buffers, and persisted asynchronously.

Prefetch paths sort and merge requested IO ranges, mark chunks pending, fetch backend ranges, persist raw compressed ranges or per-chunk uncompressed data, and update chunk-map readiness. `BlobObject` methods allow fetching compressed/uncompressed ranges and checking all-data-ready for direct object use. Dedup, when enabled, is attempted before backend fetch in `dispatch_one_range`; successful copy from CAS marks the chunk ready.

## State And Persistence Behavior
`FileCacheEntry` persists cached bytes into `file` at compressed offsets for raw-data caches or uncompressed offsets for decoded caches. Cache-at-rest encryption pads writes to 4096-byte pages and derives cipher metadata from chunk digest bytes. Readiness/pending state is kept in `chunk_map`, which may be persistent depending on the map implementation. Metrics track total reads, hits, buffered backend bytes, prefetch merge counts, and entry count increments when chunks become ready. `prefetch_state` is an atomic activity counter; `workers` receives async prefetch tasks. With feature `dedup`, `Drop` triggers CAS garbage collection.

## Dependencies And Integration Points
The file is tightly integrated with `BlobCache` trait helpers in `cache/mod.rs` for backend reads, decompression, and validation. It depends on `BlobReader`, `ChunkMap`, async worker types, `CasMgr`, blob device metadata (`BlobInfo`, `BlobChunkInfo`, `BlobIo*`), compression metadata, crypto utilities, metrics, `nix::sys::uio::pwrite`, `FileRangeReader`, Tokio runtime, and fscache/file-cache managers that construct entries.

## Risks And Edge Cases
Correctness depends on pending bits always being cleared or promoted; the code has explicit cleanup paths, but any missed error path can stall a chunk until timeout. Asynchronous persistence means user data may be returned before cache writes finish; failed writes clear pending and leave future reads to retry. Direct IO requires capacity/page alignment and padding, and encrypted cache writes can persist padded bytes beyond logical chunk size. ZRan and batch chunks need metadata; missing async metadata returns errors after polling. Region merging relies on chunk ordering and continuity assertions. `DataBuffer::from_mut_slice` uses unsafe ownership tricks and must only be used where the underlying slice lifetime is controlled.

## Test Signals
Tests cover buffer ownership conversion, region type joinability, region append/continuity behavior, file IO merge splitting, batch metadata lookup through `BlobCCI`, entries-count metric increments, and `FileCacheMeta` immediate/wait/error/clone behavior. The largest runtime paths (`dispatch_backend`, async persistence, encryption, direct IO, dedup integration, and real backend failures) are mostly covered indirectly elsewhere or require integration tests.
