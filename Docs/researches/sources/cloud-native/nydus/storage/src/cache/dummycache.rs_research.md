# sources/cloud-native/nydus/storage/src/cache/dummycache.rs

Purpose: provides `DummyCacheMgr` and its private `DummyCache`, a `BlobCacheMgr`/`BlobCache` implementation that does not persist cached chunks. It either reports all chunks as cached for local-disk style backends or reports none cached for remote on-demand reads, while still handling backend reads, decompression, decryption, and validation through the common `BlobCache` helper methods.

Important APIs and control flow: `DummyCacheMgr::new` captures backend, `cached` readiness behavior, and cache validation setting. `get_blob_cache` rejects ZRan blobs, obtains a backend `BlobReader`, and builds a `DummyCache` with a `NoopChunkMap`. `DummyCache::read` validates non-empty IO, uses a fast path when a single full chunk can be read directly into the destination volatile slice, otherwise allocates one temporary uncompressed buffer per user IO descriptor, calls `read_chunk_from_backend`, and scatters data with `copyv`. Prefetch APIs are intentionally inert: start/stop succeed, active is false, and actual prefetch returns `Unsupported`.

State and persistence behavior: there is no data cache or persistent state. Readiness is entirely represented by `NoopChunkMap::new(self.cached)`. `destroy` is idempotent via `AtomicBool` and shuts down the backend once.

Dependencies and integration points: integrates with `BlobBackend`, `BlobReader`, `BlobInfo`, `BlobIoVec`, `BlobIoDesc`, `BlobPrefetchRequest`, `NoopChunkMap`, volatile FUSE buffers, Nydus compression/digest/crypto helpers, and the common `BlobCache` default methods.

Risks and test signals: the unsafe slice conversion in the fast path depends on the destination slice being valid for the requested chunk size. Multi-descriptor reads only push buffers for `user_io`, so offsets passed to `copyv` must match the first descriptor assumptions. Tests cover metadata accessors, unsupported prefetch, direct and multi-buffer reads, manager destroy/gc/backend access, and validation of config wiring.
