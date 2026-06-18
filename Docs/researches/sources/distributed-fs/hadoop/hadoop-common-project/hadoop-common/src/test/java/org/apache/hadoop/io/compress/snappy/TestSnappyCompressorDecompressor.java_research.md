<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/snappy/TestSnappyCompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/snappy/TestSnappyCompressorDecompressor.java

Purpose: Snappy compressor/decompressor contract, direct decompression, stream integration, multi-thread, and native-format compatibility tests.

Important APIs/types/functions: tests use `SnappyCompressor`, `SnappyDecompressor`, `SnappyDirectDecompressor`, `BlockCompressorStream`, `BlockDecompressorStream`, direct `ByteBuffer`s, and nested `BytesGenerator`.

Control flow: validation tests assert null and array-bound exceptions for input and output APIs. Main round trip compresses 54 KiB with max compressed length `32 + size + size / 6`, verifies byte counters, decompresses and compares bytes, then resets. Empty stream test checks 4-byte empty block output and EOF. Block compression test manually compresses input in chunks sized for block overhead. Small-buffer test drains compressor and decompressor loops with 512-byte output buffers. Direct block tests compress data, feed direct input/output buffers to `SnappyDirectDecompressor`, and compare byte-by-byte for sizes from 4 KiB to 1 MiB. Stream test uses block compressor/decompressor streams over 100 KiB. Multithread test runs the main round trip in 10 threads. Compatibility test decodes a hard-coded hex payload compressed by the previous native Snappy codec and verifies raw bytes with the current direct decompressor.

State and persistence behavior: all data is in memory. `BytesGenerator` has static `Random(12345L)` and a fixed nibble-byte cache; generated data depends on call order and may interleave in multi-threaded tests.

Dependencies and integration points: integrates with Snappy codec primitives, block compression stream framing, Commons Codec `Hex`, Java direct buffers, and Hadoop multithreaded utilities.

Risks and edge cases: static random is shared and not synchronized. Some manual block compression writes full block arrays instead of exact compressed lengths, so it mainly asserts nonempty output. Several tests use broad exception handling rather than precise assertions.

Test signals: validates Snappy API error behavior, byte counters, finish/remaining state, empty stream framing, direct decompression, small output buffers, stream wrappers, concurrent use, and compatibility with legacy native Snappy bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/snappy/TestSnappyCompressorDecompressor.java -->
