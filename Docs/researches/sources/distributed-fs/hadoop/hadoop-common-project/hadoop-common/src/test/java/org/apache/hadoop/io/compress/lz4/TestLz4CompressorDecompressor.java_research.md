<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/lz4/TestLz4CompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/lz4/TestLz4CompressorDecompressor.java

Purpose: LZ4 compressor/decompressor API contract, round-trip, stream integration, multithread, and backwards compatibility tests.

Important APIs/types/functions: tests cover `Lz4Compressor`, `Lz4Decompressor`, `BlockCompressorStream`, `BlockDecompressorStream`, `SequenceFile.Reader`, and `MultithreadedTestUtil`. Helper `generate` produces deterministic low-entropy byte arrays.

Control flow: early tests assert null input and invalid index/length exceptions for compressor and decompressor `setInput`, `compress`, and `decompress`. Size tests feed input larger than the default buffer and assert nonzero compressed output. `testCompressDecompress` compresses 54 KiB, checks byte counters, decompresses by compressed size, asserts finished and byte equality, resets, and checks no remaining bytes. Empty stream test closes a block compressor without writes and expects 4 bytes of framing and EOF on decompression. Stream test writes 100 KiB through block compression streams and reads back through block decompression. Multithread test runs the core round trip in 10 threads. Compatibility test opens a resource `/lz4/sequencefile` created by the old native codec and verifies 2000 key/value records.

State and persistence behavior: mostly in-memory. Compatibility test reads a classpath resource and does not write. Static random generator is shared.

Dependencies and integration points: covers LZ4 codec primitives, Hadoop block compression streams, SequenceFile compatibility, Hadoop filesystem access for resource path, and multithreaded testing.

Risks and edge cases: static random is shared across threads. Some tests use broad `try/catch` with `fail` messages instead of `assertThrows`. Stream read uses a single `read(result)` call, which assumes the full buffer is filled in one call.

Test signals: validates argument validation, state counters, compression/decompression equality, empty block framing, stream wrappers, concurrent instances, and compatibility with pre-HADOOP-17292 LZ4 sequence files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/lz4/TestLz4CompressorDecompressor.java -->
