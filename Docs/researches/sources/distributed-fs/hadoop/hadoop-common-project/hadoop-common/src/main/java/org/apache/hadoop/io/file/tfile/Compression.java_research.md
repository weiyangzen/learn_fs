# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Compression.java

Purpose: compression abstraction for TFile/BCFile, supporting LZO, GZ, and NONE plus codec pooling and block-flush behavior.

Important APIs/types/functions: enum `Algorithm`; `FinishOnFlushCompressionStream`; algorithm methods `isSupported()`, `getCodec()`, `createCompressionStream()`, `createDecompressionStream()`, `getCompressor()`, `returnCompressor()`, `getDecompressor()`, `returnDecompressor()`, `getName()`; top-level `getCompressionAlgorithmByName()` and `getSupportedAlgorithms()`.

Control flow: LZO lazily loads a configurable codec class and buffers both compressor streams and decompressor streams. GZ uses `DefaultCodec` and adjusts file-buffer settings. NONE returns buffered or raw streams. Pooled compressors/decompressors are reset when acquired and returned to `CodecPool` after use. `FinishOnFlushCompressionStream.flush()` finishes, flushes, and resets compression state to support block boundaries.

State and persistence: enum instances cache codec/loading state and share a static `Configuration`. BCFile persists algorithm names in indexes.

Dependencies and integration: used by `BCFile` block writer/reader; depends on Hadoop compression codecs, `CodecPool`, `ReflectionUtils`, and TFile constants.

Risks: static configuration and LZO lazy state can affect tests; LZO availability is environment-dependent. Tests should cover algorithm name resolution, supported algorithm listing, NONE passthrough, GZ round trip, LZO missing-class failures, compressor return on exceptions, and finish-on-flush block separation.
