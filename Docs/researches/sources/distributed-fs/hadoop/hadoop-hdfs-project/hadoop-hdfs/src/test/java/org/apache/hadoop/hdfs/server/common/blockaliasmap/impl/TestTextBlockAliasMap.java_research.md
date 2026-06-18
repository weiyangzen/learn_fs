# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestTextBlockAliasMap.java

Purpose: this test covers the text-based `TextFileRegionAliasMap` format used for provided-storage block maps. It validates writer/reader option resolution, compression codec selection, CSV/TSV serialization, multiple independent iterators, and iterator invalidation after reader close.

Important APIs and types: `TextFileRegionAliasMap`, `TextReader`, `TextWriter`, `WriterOptions`, `ReaderOptions`, `FileRegion`, `DataOutputBuffer`, `DataInputBuffer`, `CompressionCodecFactory`, `GzipCodec`, and `fileNameFromBlockPoolID`.

Control flow: overloaded `check` helpers subclass `TextFileRegionAliasMap` and intercept `createWriter` or `createReader` to assert resolved path and codec. `testWriterOptions` checks default output dir, no default codec, BPID-derived filename, and gzip suffix/codec behavior. `testReaderOptions` checks explicit filenames with and without gzip. `testCSVReadWrite` and `testCSVReadWriteTsv` write three `FileRegion` rows into an in-memory buffer using comma or tab delimiters, create a custom reader over that buffer, interleave two iterators to prove independence, and confirm an iterator obtained before close throws `IllegalStateException` afterward.

State and persistence: all data is in memory; no filesystem writes occur. Options are mutable objects, so tests mutate and reuse them deliberately.

Dependencies and integration points: this file guards the human-readable alias-map interchange format, including codec detection by path suffix and delimiter handling. It complements LevelDB tests by covering text import/export style flows.

Risks: tests use simple paths and offsets and do not cover delimiters embedded in path text. The reader/writer factory interception returns null intentionally, so only option resolution is tested there, not actual stream creation.

Test signals: failures suggest path/codec option derivation, file-region text serialization, or iterator lifecycle semantics changed.
