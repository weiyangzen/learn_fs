<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchingInputStreamFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchingInputStreamFactory.java

Purpose: `ObjectInputStreamFactory` implementation for the prefetch stream. It parses prefetch configuration and creates `S3APrefetchingInputStream` instances.

Important APIs/types/functions: extends `AbstractObjectInputStreamFactory`; `streamType()` returns `InputStreamType.Prefetch`; `serviceInit()` reads `PREFETCH_BLOCK_SIZE_KEY` and `PREFETCH_BLOCK_COUNT_KEY`, validates int-sized block size, and constructs `PrefetchOptions`; `readObject()` returns a new `S3APrefetchingInputStream`; `factoryRequirements()` requests `prefetchBlockCount` shared threads, no stream threads, a vectored context with min seek set to zero, and `RequiresFuturePool`.

Control flow: service init prepares shared options; each read creates a wrapper stream. Range merging is disabled for vectored IO by setting min seek to zero to avoid fetching discarded bytes.

State/persistence: stores configured block size/count and immutable options for factory lifetime.

Dependencies/integration: integrates with S3A constants, `S3AUtils` config parsers, `StreamIntegration.populateVectoredIOContext`, and future-pool provisioning.

Risks/test signals: large block sizes above int max fail; low queue counts reduce throughput; vector settings deliberately alter read coalescing. Tests should cover config validation, requirements, and stream creation with validated `ObjectReadParameters`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchingInputStreamFactory.java -->
