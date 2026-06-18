# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipCompressor.java

Purpose: pure-Java gzip `Compressor` used when Hadoop needs a gzip stream wrapper around `java.util.zip.Deflater`, marked `@DoNotPool`.

Important APIs and control flow: `init()` creates a raw `Deflater` (`nowrap=true`) with `ZlibFactory` compression level/strategy and starts in `HEADER_BASIC`. `compress()` emits the fixed gzip header, deflates data in `INFLATE_STREAM`, then fills and emits the gzip trailer when the deflater finishes. `setInput()` passes bytes to the deflater and updates CRC-32 and uncompressed-size accumulator. `finish()` delegates to `Deflater.finish()`, while `finished()` requires both deflater completion and trailer emission.

State and persistence: stores mutable header/trailer offsets, CRC, accumulated length, extra-byte count, deflater, and shared gzip state labels from `BuiltInGzipDecompressor.GzipStateLabel`. No persistence; `reset()` and `reinit()` rebuild stream state.

Dependencies and integration: implements Hadoop `Compressor`; uses `DataChecksum.newCrc32()`, `ZlibFactory`, Java `Deflater`, and `AlreadyClosedException`. Gzip output is consumed by Hadoop gzip streams and Java gzip tools.

Risks and test signals: test partial header/trailer writes, very small output buffers, `compress()` after finished/ended, CRC/ISIZE trailer correctness, and reinit strategy handling. `accuBufLen` is an `int`, matching gzip trailer modulo 2^32 behavior but requiring large-stream coverage.
