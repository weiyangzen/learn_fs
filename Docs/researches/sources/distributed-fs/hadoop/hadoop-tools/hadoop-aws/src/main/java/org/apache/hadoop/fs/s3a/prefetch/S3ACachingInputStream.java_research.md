<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingInputStream.java

Purpose: remote input stream for larger objects that reads block-by-block, prefetches ahead on sequential reads, and caches partially consumed blocks to local disk when seek patterns suggest reuse.

Important APIs/types/functions: constructor builds `BlockManagerParameters` with future pool, block data, buffer pool size `prefetchBlockCount + 1`, configuration, `LocalDirAllocator`, max cache blocks, stream statistics, and tracker factory. `ensureCurrentBuffer()` is the main read-position algorithm. `createBlockManager()` returns `S3ACachingBlockManager` and is overridable for tests. `close()` closes the block manager then remote stream.

Control flow: on read, `ensureCurrentBuffer()` validates offset, detects out-of-order reads via `FilePosition.setAbsolute()`, releases fully read blocks, caches partially read ones, cancels prefetches after seeks, queues one block after a seek or `numBlocksToPrefetch` blocks for sequential reads, fetches the current block with duration tracking, then binds it into `FilePosition`.

State/persistence: maintains prefetch count and a block manager that may store blocks in local temporary files and memory buffers. Close deletes cached files and frees buffers through the block manager.

Dependencies/integration: integrates `S3ARemoteInputStream`, prefetch framework `BlockManager`, `BufferData`, `FilePosition`, S3A statistics, local directory allocation, and stream statistic name `STREAM_READ_BLOCK_ACQUIRE_AND_READ`.

Risks/test signals: seek-heavy workloads can cause cancellations and local cache churn; local disk configuration and max block count constrain behavior. Tests should cover sequential prefetch, lazy seek, partial-buffer caching, full-buffer release, cache cleanup, and statistics tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ACachingInputStream.java -->
