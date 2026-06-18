## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CacheRequestManager.java

### Purpose
`CacheRequestManager` handles synchronous and asynchronous requests to cache a block on the worker. It deduplicates active requests by block id, chooses local UFS versus remote-worker source, performs the copy/read into the local block store, and records cache metrics.

### Important APIs and Types
- Constructor takes an executor, `DefaultBlockWorker`, and `FileSystemContext`.
- `submitRequest(CacheRequest)` is the public entry point.
- Inner `CacheTask` executes one request and defines equality/hash by block id.
- `CacheResult` distinguishes `SUCCEED`, `FAILED`, and `ALREADY_CACHED`.
- `cacheBlockFromUfs` reads the whole block through UFS fallback reader and commits temp metadata.
- `cacheBlockFromRemoteWorker` creates a temp local block, copies from `RemoteBlockReader` to `BlockWriter`, then commits.
- `getRemoteBlockReader` is visible for testing.

### Control Flow
`submitRequest` increments request metrics, rejects duplicate active block ids, and either returns for async duplicates or waits up to 30 seconds for sync duplicates. New requests are submitted to the cache executor. Sync callers wait on the future and receive translated exceptions. The task removes its block id from `mActiveCacheRequests` in `finally` and increments success/failure/size counters. Source selection compares `sourceHost` to local host; local reads go through UFS and remote reads go through a remote block stream.

### State and Persistence
Active requests are tracked in a `ConcurrentHashMap<Long, CacheRequest>`. Persistent effects are local temp/committed block files and metadata created through `DefaultBlockWorker`/`BlockStore`. Failed UFS and remote copies abort matching temp blocks when present.

### Dependencies and Integration Points
The manager is owned by `DefaultBlockWorker` and uses `BlockReader`, `BlockWriter`, `RemoteBlockReader`, `NetworkAddressUtils`, `BufferUtils`, sessions reserved for cache, and worker cache metrics.

### Risks
- Sync duplicate waiting is bounded to 30 seconds and can report cancellation even if the original request later succeeds.
- Remote cache creates a local temp block before opening the remote reader, so failures must reliably abort to avoid leaked temp files.
- UFS cache assumes full-block sequential read; partial reads do not satisfy caching.
- The async executor rejection path is best-effort for async but fatal to sync callers.

### Test Signals
Cache behavior is typically tested through `DefaultBlockWorker` cache tests and by mocking `getRemoteBlockReader`; source references show several worker grpc tests exercising cache/fallback paths.
