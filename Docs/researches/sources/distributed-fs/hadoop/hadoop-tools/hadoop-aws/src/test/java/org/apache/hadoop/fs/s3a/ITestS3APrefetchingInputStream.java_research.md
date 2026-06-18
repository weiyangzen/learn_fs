# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3APrefetchingInputStream.java

Purpose: Validates the prefetching input stream's caching, in-memory small-file path, request counts, memory/cache gauges, random reads, lazy positioned reads, and post-close status probes.

Important APIs/types/functions: `enablePrefetching()`, `Constants.PREFETCH_BLOCK_SIZE_KEY`, `S3APrefetchingInputStream`, `S3AInputStreamStatistics`, IO statistics counters/gauges `STREAM_READ_PREFETCH_OPERATIONS`, `ACTION_HTTP_GET_REQUEST`, `STREAM_READ_OPENED`, `STREAM_READ_BLOCKS_IN_FILE_CACHE`, `STREAM_READ_ACTIVE_MEMORY_IN_USE`, and `ACTION_EXECUTOR_ACQUIRED`.

Control flow: configuration enables prefetch and sets 10 KiB block size. `createLargeFile()` writes a multi-block object and computes block count. Full-read tests read sequentially via stream or positioned `readFully` and assert first block synchronous plus remaining blocks prefetched. Random large-file test partially reads/seeks to create cached blocks and uses `eventually()` for async counters. Small-file test ensures one GET and no prefetch/buffer-pool use. Post-close test verifies `getPos()`, `getIOStatistics()`, and stream statistics remain available after close and `seekToNewSource()` is unsupported.

State and persistence: writes S3 objects; prefetch internals maintain memory/file cache state tracked by IOStatistics. Async prefetch means some assertions use polling.

Dependencies and integration points: S3A prefetch stream, caching input stream, in-memory input stream, IOStatistics, async executor, and client-side-encryption skip behavior.

Risks: exact counters can shift with prefetch strategy changes; asynchronous prefetch makes timing-sensitive assertions; large buffer loop increments bytesRead by buffer length rather than actual read request size but bounded by file-size condition.

Test signals: strong regression coverage for prefetch request economics, resource cleanup, cache gauges, and closed-stream observability.
