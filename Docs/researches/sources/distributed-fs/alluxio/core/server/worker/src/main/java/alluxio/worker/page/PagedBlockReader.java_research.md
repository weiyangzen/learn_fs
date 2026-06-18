# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockReader.java

## Purpose
`PagedBlockReader` implements `BlockReader` for blocks stored in page cache, with optional fallback to UFS for cache misses. It can also cache UFS-read pages back into Alluxio.

## Important APIs, Types, and Functions
`read(offset,length)` validates and allocates a direct buffer, then delegates to private `read(ByteBuf, offset, length)`. The private read loop computes page IDs and page offsets, calls `CacheManager.get`, updates cache-read metrics, and on misses calls `PagedUfsBlockReader.readPageAtIndex`. `transferTo(ByteBuf)` streams from current position. `close()` records whether the block was read from local cache and/or UFS.

## Control Flow, State, and Persistence
The reader tracks current position, closed state, and whether any bytes came from cache/UFS. Cache hits read existing pages. Cache misses require a UFS reader; if configured to cache into Alluxio, the full UFS page is inserted into `CacheManager`.

## Dependencies and Integration Points
It depends on `CacheManager`, `BlockPageId`, `PagedBlockMeta`, `PagedUfsBlockReader`, `NettyBufTargetBuffer`, `NioDirectBufferPool`, Netty `ByteBuf`, and metrics.

## Risks and Test Signals
Risks include pooled buffer release responsibility, failing when UFS options are absent for cache misses, assuming full requested bytes after UFS page read, and unsupported channel reads. Tests should cover full cache hit, cache miss with cache-fill, missing UFS reader, partial last page, bounds validation, `transferTo`, and close metrics.
