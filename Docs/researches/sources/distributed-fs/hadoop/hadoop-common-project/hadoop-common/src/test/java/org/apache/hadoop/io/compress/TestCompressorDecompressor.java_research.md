<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorDecompressor.java

Purpose: Shared compressor/decompressor coverage for Snappy, LZ4, and built-in zlib implementations through `CompressDecompressTester`.

Important APIs/types/functions: `testCompressorDecompressor`, `testCompressorDecompressorWithExceedBufferLimit`, and static `generate(int size)`. It uses pairs `SnappyCompressor/SnappyDecompressor`, `Lz4Compressor/Lz4Decompressor`, and `BuiltInZlibDeflater/BuiltInZlibInflater`.

Control flow: first test generates 44 KiB of low-entropy bytes and runs single-block, block, error-contract, and empty-stream strategies. Second test generates 100 KiB and creates Snappy/LZ4 pairs with 64 KiB internal buffers, then runs block, error, and empty-stream strategies to exercise inputs larger than the internal buffer.

State and persistence behavior: deterministic static `Random(12345L)` supplies data; compressor objects are terminated by the shared harness. No file persistence.

Dependencies and integration points: depends on the generic harness in `CompressDecompressTester`, codec-specific compressor/decompressor classes, Guava `ImmutableSet`, and `GenericTestUtils.assertExceptionContains` in catch blocks.

Risks and edge cases: catch blocks call `GenericTestUtils.assertExceptionContains` with a message that likely is not contained in thrown exceptions, causing failures to surface but with odd semantics. Static random data advances between tests, so exact bytes depend on test order.

Test signals: validates common compressor API contracts and round-trip behavior for built-in non-native compressor paths and large-buffer scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorDecompressor.java -->
