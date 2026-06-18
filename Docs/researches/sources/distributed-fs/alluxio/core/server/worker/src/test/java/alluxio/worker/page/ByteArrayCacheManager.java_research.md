# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/ByteArrayCacheManager.java

Purpose: test-only in-memory `CacheManager` storing pages as byte arrays for paged block reader tests.

Important APIs and helpers: `put` copies a `ByteBuffer` into a map and increments `mPagesCached`; `get` writes cached bytes into a `ReadTargetBuffer` and increments `mPagesServed`; `getAndLoad` reads from cache or calls an external supplier and caches the result. It also supports `delete`, `deleteFile`, `deleteTempFile`, `getUsage`, `state`, and `close`.

Control flow and state: page contents are held in `Map<PageId, byte[]>`. Missing pages return zero bytes; loaded pages are cached before returning. `Usage` reports used bytes from page lengths and unbounded integer capacity/availability.

Dependencies and integration: implements `alluxio.client.file.cache.CacheManager`, uses `CacheContext`, `ReadTargetBuffer`, `PageId`, and optional `CacheUsage`.

Risks and test signals: not thread-safe and does not implement append or file commit. It provides deterministic cache-hit/cache-miss behavior for reader tests without local page-store side effects.
