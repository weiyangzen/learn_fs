## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UfsInputStreamCache.java

### Purpose
`UfsInputStreamCache` reuses seekable UFS input streams per file id to reduce open/close overhead for UFS block reads and load reads. Non-seekable UFSes or disabled cache mode fall back to always opening and closing streams.

### Important APIs and Types
- Constructor builds a Guava cache of resource id to `CachedSeekableInputStream` with maximum size, expire-after-access, and async removal listener.
- `acquire(UnderFileSystem, path, fileId, OpenOptions)` returns a cached or newly opened input stream positioned at the requested offset.
- `release(InputStream)` returns cached streams to available state or closes non-cached/expired streams.
- Inner `StreamIdSet` tracks in-use and available resource ids per file.

### Control Flow
Acquire exits early for non-seekable/disabled cache. Otherwise it cleans up expired entries, gets/creates a `StreamIdSet`, tries to atomically acquire an available cached stream id, seeks the stream to the requested offset, and returns it. If none is available, it generates a new random non-negative id, opens a seekable UFS stream, wraps it, and stores it in the cache. Release moves the id from in-use to available if still tracked; otherwise it closes the stream. The removal listener removes ids from tracking and closes only streams that were available, logging if an in-use stream expires.

### State and Persistence
State is in-memory cache and per-file id sets. It persists nothing. UFS stream resources remain open while cached and available.

### Dependencies and Integration Points
Used by `UnderFileSystemBlockReader` and `UfsIOManager`. Depends on UFS seekability, `OpenOptions`, Guava cache, async removal executor, and `CachedSeekableInputStream`.

### Risks
- In-use streams can expire from Guava cache; the listener removes them from tracking but does not close them until release, which is intentional but easy to mis-handle.
- `availableIds()` returns an unmodifiable view over the mutable set; iteration is protected by synchronizing on `streamIds` in current code.
- Cache key space uses random longs; collisions loop until free.
- Removal-thread lifecycle is not exposed for shutdown in this class.

### Test Signals
`UnderFileSystemBlockReaderTest` uses `UfsInputStreamCache` and covers stream reuse/caching via UFS reader behavior. Dedicated cache tests may exist outside the searched references.
