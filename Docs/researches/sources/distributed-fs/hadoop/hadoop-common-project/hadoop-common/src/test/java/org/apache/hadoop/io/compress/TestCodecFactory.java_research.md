<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecFactory.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecFactory.java

Purpose: Tests `CompressionCodecFactory` discovery, extension matching, class/name lookup, service-loaded defaults, configured codec lists, and override precedence.

Important APIs/types/functions: local `BaseCodec` implements `CompressionCodec` with stub stream/compressor/decompressor methods and default extension `.base`. Subclasses define `BarCodec` (`bar`), `FooBarCodec` (`.foo.bar`), `FooCodec` (`.foo`), and `NewGzipCodec` (`.gz`). Helper `setClasses` configures codec classes through `CompressionCodecFactory.setCodecClasses`; `checkCodec` asserts expected class or null.

Control flow: `testFinding` first checks default factory behavior for unknown `.bar`, built-in gzip/bzip2/deflate by extension, class name, short name, and case variants. It then configures an empty explicit list and verifies service-loaded codecs still include gzip, bzip2, snappy, and lz4 but not `BarCodec`. It configures custom classes and checks longest extension match (`.foo.bar` before `.bar`/`.foo`), case-insensitive extensions, name lookup, and class lookup. Finally it overrides `.gz` with `NewGzipCodec` and checks whitespace-padded `io.compression.codecs` parsing does not throw.

State and persistence behavior: configuration-local state only; no files are written. Factory instances build in-memory mappings from configuration and service loader state.

Dependencies and integration points: integrates with `CompressionCodecFactory`, `CommonConfigurationKeys.IO_COMPRESSION_CODECS_KEY`, Hadoop `Path`, and default codec service discovery.

Risks and edge cases: stub codecs return null for stream creation and should only be used for factory lookup. Raw extension `"bar"` lacks a leading dot, exercising factory normalization. Service loader contents must include expected built-ins or assertions fail.

Test signals: verifies default and configured lookup paths, case-insensitivity, custom extension precedence, short-name matching, override behavior, and robust config parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecFactory.java -->
