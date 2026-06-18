# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingLruEviction.java

Purpose: Parameterized stress test for LRU eviction in `S3ACachingInputStream` when prefetch cache capacity is one or two blocks.

Important APIs/types/functions: `Constants.PREFETCH_MAX_BLOCKS_COUNT`, `Constants.PREFETCH_BLOCK_SIZE_KEY`, `enablePrefetching()`, `FSDataInputStream.readFully(position, ...)`, `seek()`, IOStatistics gauges/counters `STREAM_READ_BLOCKS_IN_FILE_CACHE`, `STREAM_EVICT_BLOCKS_FROM_FILE_CACHE`, and `STREAM_FILE_CACHE_EVICTION`.

Control flow: for max blocks `1` and `2`, configuration sets prefetch and cache capacity. The test writes a multi-block file, opens one stream, submits seven concurrent partial read/seek tasks across several blocks, waits for completion, asserts cache gauge settles to the configured capacity while stream is open, then after close asserts cache gauge returns to zero and eviction counters are at least four and internally consistent.

State and persistence: writes one S3 object per parameter. Uses a daemon fixed thread pool and countdown latch; closes stream to release cache.

Dependencies and integration points: prefetch cache LRU policy, concurrent stream reads, IOStatistics, and async prefetch cancellation behavior.

Risks: concurrent use of one input stream can expose timing-dependent behavior; comments note transient failures around async prefetch cancellation; exact eviction count is lower-bounded instead of exact.

Test signals: catches cache-capacity violations, missing cleanup on close, and divergence between eviction counters.
