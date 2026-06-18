<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBzip2CompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBzip2CompressorDecompressor.java

Purpose: Native bzip2 compressor/decompressor round-trip and multi-thread smoke coverage.

Important APIs/types/functions: `before()` assumes `Bzip2Factory.isNativeBzip2Loaded`. `testCompressDecompress` uses `Bzip2Compressor` and `Bzip2Decompressor`. `generate` creates deterministic low-entropy data. `testBzip2CompressDecompressInMultiThreads` uses `MultithreadedTestUtil`.

Control flow: single-thread test generates 64 KiB, asserts compressor not finished, sets input, checks `getBytesRead` before compression, calls `finish`, compresses into a same-size buffer, asserts bytes read and compressed size smaller than original, decompresses into original-size output, compares arrays, and resets both objects. Multi-thread test starts 10 testing threads, each running the same method, and waits up to 60 seconds.

State and persistence behavior: no persistent state. Static random generator is shared, including across multi-threaded calls, which can interleave data generation.

Dependencies and integration points: depends on native bzip2 availability, Hadoop bzip2 compressor/decompressor classes, JUnit assumptions, and Hadoop multithreaded test utility.

Risks and edge cases: static `Random` is shared across threads and not synchronized. Tests are skipped when native bzip2 is unavailable. Compressed output buffer assumes compressed data is smaller than raw low-entropy input.

Test signals: validates native bzip2 basic state counters, compression ratio, byte equality after decompression, reset behavior, and concurrent use of separate compressor/decompressor instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBzip2CompressorDecompressor.java -->
