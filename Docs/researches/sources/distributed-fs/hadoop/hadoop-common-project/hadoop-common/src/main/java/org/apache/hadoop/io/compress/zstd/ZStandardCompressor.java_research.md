# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardCompressor.java

Purpose: Hadoop `Compressor` backed by `zstd-jni` streaming compression, with configurable compression level, worker count, and direct-buffer sizes.

Important APIs and control flow: constructors allocate direct buffers and a `ZstdCompressCtx`; `getRecommendedBufferSize()` uses `ZstdOutputStream.recommendedCOutSize()`. `setInput()` copies caller bytes into the direct input buffer. `needsInput()` considers pending compressed output, partially consumed direct input, and saved user input. `compress()` always invokes `compressDirectByteBufferStream`, using `CONTINUE` until `finish()` is set and all input is consumed, then `END`; it tracks consumed input/output bytes, manages `keepUncompressedBuf`, marks `finished` when zstd reports end, and drains compressed output to the caller. `reinit()` reloads level/workers from `ZStandardCodec`.

State and persistence: state includes `ZstdCompressCtx`, direct buffers, saved input offsets, direct-buffer offsets, finish flags, read/write counters, compression level, and worker count. `end()` closes the context; `finalize()` also closes.

Dependencies and integration: implements Hadoop `Compressor`, uses `ZStandardCodec` and Hadoop configuration defaults, and depends on `com.github.luben.zstd`.

Risks and test signals: test multi-threaded workers, `finish()` with internally buffered zstd output, small output arrays, input larger than direct buffer, reinit/reset, and operations after `end()`. Streaming API semantics are subtle because `CONTINUE` may leave jobs in flight.
