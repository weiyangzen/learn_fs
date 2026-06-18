<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zlib/TestZlibCompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zlib/TestZlibCompressorDecompressor.java

Purpose: Native zlib compressor/decompressor tests for generic compressor contracts, configuration, compression levels, direct decompression, dictionaries, factory settings, gzip built-in error handling, and multithreaded operation.

Important APIs/types/functions: class-level `before()` assumes `ZlibFactory.isNativeZlibLoaded`. Tests use `ZlibCompressor`, `ZlibDecompressor`, `ZlibDirectDecompressor`, `ZlibFactory`, `BuiltInGzipDecompressor`, generic `CompressDecompressTester`, and helper `compressDecompressZlib`.

Control flow: generic harness tests run zlib pair through single-block, block, error, and empty-stream strategies, including a large-buffer constructor path. Configuration tests obtain compressors/decompressors from `ZlibFactory`, run repeated round trips, and reinitialize. Compression-level test sets `zlib.compress.level` to `FOUR`. Direct test compresses with Java `DeflaterOutputStream`, then verifies direct-buffer decompression for sizes from 1 byte to 1 MiB. Dictionary test checks null and invalid-range exceptions. Factory test verifies default and set compression level/strategy values. Built-in gzip decompressor test checks argument exceptions, counters, reset/end, and invalid gzip header bytes. Multi-thread test runs the core zlib round trip in 10 threads.

State and persistence behavior: in-memory only. Native availability is global. Static random generator is shared across tests and threads. Factory configuration lives in `Configuration` objects.

Dependencies and integration points: integrates native zlib, Java zlib streams, Hadoop compression interfaces, `DecompressorStream`, `DataInputBuffer`, and multithread test utilities.

Risks and edge cases: class-level native assumption skips all tests without native zlib. Static random is unsynchronized in threaded tests. Helper predicates for dictionary exceptions return booleans but the test does not assert their return values, weakening coverage. Some branches assert native zlib loaded in `else`, producing failure instead of skip if assumption were bypassed.

Test signals: validates zlib round trips, API error contracts, native direct decompression, config-driven level/strategy, gzip header validation errors, counter behavior, reset/reinit, and multi-threaded independent instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zlib/TestZlibCompressorDecompressor.java -->
