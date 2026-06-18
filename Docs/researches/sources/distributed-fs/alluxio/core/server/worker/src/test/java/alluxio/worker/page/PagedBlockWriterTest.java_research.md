# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockWriterTest.java

Purpose: parameterized tests for `PagedBlockWriter` appending bytes into temporary page-cache files and preserving data across page boundaries.

Important APIs and helpers: setup configures page size, creates a local page store, FIFO evictor, `DefaultPageMetaStore`, `LocalCacheManager`, waits for read-write state, and constructs a writer. Tests cover appending Netty `ByteBuf` and Java `ByteBuffer` inputs for several page sizes.

Control flow and state: each test appends a series of increasing-byte chunks, closes the writer, commits the temp file ID to final block file ID in both page metadata and page-store dir, then reads cached pages back through the cache manager and validates byte patterns.

Dependencies and integration: depends on `LocalCacheManager`, `PageStore`, `LocalPageStoreDir`, `BlockPageId`, `CacheContext`, `ByteArrayTargetBuffer`, and worker page-store configuration.

Risks and test signals: strong for write chunking, temp-file commit naming, and cache readback. It does not exercise `PagedBlockStore` commit-to-master behavior or cache eviction while writing.
