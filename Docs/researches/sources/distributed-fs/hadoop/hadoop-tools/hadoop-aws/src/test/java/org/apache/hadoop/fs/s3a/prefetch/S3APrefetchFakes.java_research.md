# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchFakes.java

Purpose: factory and fake implementation suite for testing S3A prefetch streams and block managers without S3 or local disk dependency.

Important APIs/types/functions: static factories create `S3AFileStatus`, `S3ObjectAttributes`, `S3AReadOpContext`, S3A URIs, `ChangeTracker`, AWS response streams, object callbacks, fake in-memory/caching streams, and fake caches. Nested `FakeS3AInMemoryInputStream`, `FakeS3FilePerBlockCache`, `FakeS3ACachingBlockManager`, and `FakeS3ACachingInputStream` override remote-object acquisition, cache paths, cache reads/writes, and block-manager creation.

Control flow: fake streams create `MockS3ARemoteObject` on demand with randomized short delays to exercise concurrency. The fake block cache stores cache-file bytes in a `ConcurrentHashMap<Path, byte[]>`, allocates monotonically numbered paths, and injects configurable read/write delay. The fake caching block manager delegates reads to its reader and uses the fake cache.

State and persistence: all status/attribute/context data is synthetic; cached blocks live only in memory and are cleared on close. No real S3 store or filesystem writes occur.

Dependencies/integration: Hadoop prefetch `BlockManager`, `SingleFilePerBlockCache`, `LocalDirAllocator`, `ExecutorServiceFuturePool`, S3A read contexts/statistics/change detection, and AWS SDK response objects.

Risks: random sleeps can affect timing; null callback `submit()` is unsuitable outside tested paths; static configuration may miss production options.

Test signals: used by unit tests to validate read, seek, caching, prefetch, and failure handling deterministically enough without external services.
