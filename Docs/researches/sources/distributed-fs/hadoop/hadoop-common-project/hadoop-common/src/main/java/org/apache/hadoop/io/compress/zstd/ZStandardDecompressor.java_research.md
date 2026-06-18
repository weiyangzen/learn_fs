# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardDecompressor.java

Purpose: Hadoop Zstandard `Decompressor` plus direct decompressor backed by `zstd-jni` streaming decompression.

Important APIs and control flow: construction allocates direct buffers and `ZstdDecompressCtx`; `getRecommendedBufferSize()` uses `ZstdInputStream.recommendedDInSize()`. `setInput()` copies compressed caller bytes into the direct buffer. `needsInput()` drains uncompressed output first, then refills compressed input from saved user data. `decompress()` calls `decompressDirectByteBufferStream`, updates consumed compressed offset, tracks `remaining`, marks finished only when the zstd frame is done and no compressed bytes remain, then drains output. `inflateDirect()` performs the same streaming call against caller direct buffers for the nested `ZStandardDirectDecompressor`.

State and persistence: tracks zstd context, direct buffers, compressed offsets/counts, user input counters, `remaining`, and `finished`. `reset()` clears stream and buffer state; `end()` closes the context; `finalize()` calls `end()`.

Dependencies and integration: implements Hadoop `Decompressor` and nested `DirectDecompressor`, depends on `com.github.luben.zstd`.

Risks and test signals: test concatenated frames/remaining bytes, direct buffer source/destination positions, reset after corrupt data, unsupported dictionary calls, and after-close errors. Finish semantics depend on both zstd frame completion and local buffer exhaustion.
