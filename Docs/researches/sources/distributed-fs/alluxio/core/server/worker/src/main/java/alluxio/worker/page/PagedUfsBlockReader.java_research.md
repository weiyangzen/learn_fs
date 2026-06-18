# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedUfsBlockReader.java

## Purpose
`PagedUfsBlockReader` reads block data from UFS, optimized for page-sized reads and stream reuse through `UfsInputStreamCache`. It supports both direct reads and page-fill reads used by `PagedBlockReader`.

## Important APIs, Types, and Functions
The constructor validates offset, stores UFS options, allocates a direct last-page cache, and initializes UFS bytes-read metrics tagged by UFS and optional user. `read()` fills an output buffer from the cached last page and a UFS channel. `readPageAtIndex()` reads a whole page, caches it in `mLastPage`, copies it to caller buffer, and increments UFS metrics. `transferTo()` streams from current position to Netty or `ByteBuffer`. Inner `UfsReadableChannel` lazily acquires an `InputStream` from `UfsInputStreamCache` with proper UFS offset and releases it on close.

## Control Flow, State, and Persistence
State includes current reader position, closed flag, last page index and buffer, and UFS stream/channel state per channel. No block data is persisted by this class; callers may cache returned pages into `CacheManager`.

## Dependencies and Integration Points
It integrates `UfsManager`, `UnderFileSystem`, `OpenOptions`, `UfsInputStreamCache`, `BlockMeta`, `UfsBlockReadOptions`, `NioDirectBufferPool`, UFS read metrics, and `PagedBlockReader`.

## Risks and Test Signals
Risks include pooled buffers returned from `read()` needing release discipline, last-page buffer mutation assumptions, stream-cache release during concurrent reads, metric map being instance-local rather than shared, and exact offset math combining block offset and UFS file offset. Tests should cover page reads, last-page partial reads, repeated same-page reads, transferTo, close behavior, UFS missing/unavailable errors, and user-tagged metrics.
