<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/CompressDecompressTester.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/CompressDecompressTester.java

Purpose: Shared test harness for compressor/decompressor pair implementations. It defines reusable strategies for error handling, single-block round trips, empty block streams, and multi-block round trips.

Important APIs/types/functions: generic `CompressDecompressTester<T extends Compressor,E extends Decompressor>` stores immutable raw data, a builder of `TesterPair`, selected `CompressionTestStrategy` values, and a `PreAssertionTester` availability filter. Fluent APIs are `of`, `withCompressDecompressPair`, `withTestCases`, and `test`. Nested `TesterPair` owns compressor/decompressor instances and calls `reinit`, `end` on cleanup. `CompressionTestStrategy` contains `COMPRESS_DECOMPRESS_ERRORS`, `COMPRESS_DECOMPRESS_SINGLE_BLOCK`, `COMPRESS_DECOMPRESS_WITH_EMPTY_STREAM`, and `COMPRESS_DECOMPRESS_BLOCK`.

Control flow: `test()` finalizes pair list, filters unavailable native-dependent pairs through `isAvailable`, then runs each selected strategy against a defensive copy of the original data. Error strategy verifies `NullPointerException` and `ArrayIndexOutOfBoundsException` for both set-input and compress/decompress APIs. Single-block strategy drives `finish()`/`finished()` loops and verifies bytes. Empty-stream strategy closes a `BlockCompressorStream` without writes, checks codec-specific empty output sizes, and verifies decompression EOF. Block strategy chunks input into zlib-sized blocks, compresses each independently, then decompresses each stored compressed segment.

State and persistence behavior: no persistent state. Compressor and decompressor instances are stateful and are reset between strategy phases; `endAll` terminates them after testing.

Dependencies and integration points: integrates with `Compressor`, `Decompressor`, `BlockCompressorStream`, `BlockDecompressorStream`, codec-specific native availability checks for LZ4, Snappy, built-in zlib, native zlib, and Guava immutable collections.

Risks and edge cases: `isAvailable` uses `compressor.getClass().isAssignableFrom(Lz4Compressor.class)` style checks, which are reversed from the more common `X.class.isAssignableFrom(compressor.getClass())`; exact classes pass but subclasses may behave unexpectedly. Empty stream expected sizes are hard-coded by compressor class. The block strategy only exercises block mode when original data length exceeds the threshold.

Test signals: downstream tests use this harness to assert API contract failures, data integrity after compression/decompression, EOF for empty streams, and cleanup through `end()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/CompressDecompressTester.java -->
