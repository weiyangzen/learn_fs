<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecPool.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecPool.java

Purpose: Unit and concurrency coverage for `CodecPool` leasing, returning, duplicate returns, configuration reinitialization, and `@DoNotPool` compressor/decompressor behavior.

Important APIs/types/functions: setup creates a configured `DefaultCodec`. Tests call `CodecPool.getCompressor`, `returnCompressor`, `getLeasedCompressorsCount`, `getDecompressor`, `returnDecompressor`, and leased decompressor counts. Reflection inspects compressor field `level`. Gzip built-in compressor/decompressor tests use `AlreadyClosedException` interception through `LambdaTestUtils`.

Control flow: pool count tests lease two instances, return them one by one, and verify counts including duplicate return. duplicate-return tests return the same instance twice, then request 10 instances and assert they are all unique, preventing same object from being checked out multiple times. Configuration test returns a compressor created with one compression level, then gets a compressor for another codec configuration and reflects its level. Multi-threaded tests use producer/consumer callables and a blocking queue to lease and return compressors/decompressors across threads, then assert no leases remain. `@DoNotPool` tests return built-in gzip compressor/decompressor and assert later use through gzip streams throws `AlreadyClosedException`.

State and persistence behavior: global/static pool state is exercised and mutated; tests reset by returning leased objects. In-memory gzip data is generated for decompressor tests.

Dependencies and integration points: depends on `DefaultCodec`, `GzipCodec`, zlib built-in gzip classes, `ZlibFactory`, `ReflectionUtils`, Java executors/queues, and Hadoop `LambdaTestUtils`.

Risks and edge cases: pool state is global, so parallel tests involving same codec types could interact. Reflection over field name `level` is implementation-sensitive. Timeouts protect against deadlock but the multi-thread tests use a long await.

Test signals: validates lease accounting, thread-safe return paths, duplicate return defense, configuration reinitialization, and enforcement that non-poolable gzip wrappers are closed after return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecPool.java -->
