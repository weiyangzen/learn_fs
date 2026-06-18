# Research: subset-b-007357

Grouped source research for Hadoop compression and erasure-code files. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CRC.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CRC.java

Purpose: package-private CRC-32 helper for Hadoop's BZip2 implementation. It stores the BZip2 polynomial lookup table and computes block/global CRC values used to sanity-check compressed data.

Important APIs and control flow: `initialiseCRC()` resets `globalCrc` to `0xffffffff`; `updateCRC(int)` and `updateCRC(int,int)` fold one byte or a repeated byte run through `crc32Table`; `getFinalCRC()` returns bitwise complement; `getGlobalCRC()` and `setGlobalCRC(int)` expose the current accumulator to the BZip2 encoder/decoder pipeline.

State and persistence: all state is in the instance field `globalCrc`; the static table is immutable in practice but declared as an array, so it is mutable from package code. No persistence or I/O.

Dependencies and integration: used inside the `org.apache.hadoop.io.compress.bzip2` package, based on Ant/Keiron Liddle BZip2 code. It is not public API and assumes callers pass byte values in the low 8 bits.

Risks and test signals: regression tests should compare CRCs against known BZip2 block vectors, including repeated-byte runs. Risks are accidental table mutation, signed-byte misuse by callers, and off-by-one errors in repeat updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CRC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/package-info.java

Purpose: package documentation and classification for Hadoop's BZip2 compression/decompression implementation.

Important APIs and control flow: it declares no executable code; it marks the package `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` and documents that the package implements the BZip2 algorithm.

State and persistence: no runtime state. The annotations are compile-time/source-level API signals.

Dependencies and integration: imports Hadoop classification annotations and scopes BZip2 classes under `org.apache.hadoop.io.compress.bzip2`, integrating with Hadoop compression codecs outside this file.

Risks and test signals: no direct unit tests are needed beyond checking Javadoc/annotation compilation. Any public exposure changes should be reviewed because the package is explicitly private and unstable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Compressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Compressor.java

Purpose: Hadoop `Compressor` adapter backed by `net.jpountz.lz4`, supporting regular and high-compression LZ4 modes with direct ByteBuffer staging.

Important APIs and control flow: constructors select `LZ4Factory.fastestInstance().fastCompressor()` or `highCompressor()`, allocate direct input and output buffers, and size the output buffer using the LZ4 compress-bound formula. `setInput()` validates user arrays, copies data into the direct input buffer when possible, or stores the user buffer for later chunking. `needsInput()` returns false while compressed output, a full input buffer, or saved user data remains. `compress()` drains pending compressed bytes first, then fills the input direct buffer from saved data if needed, calls `compressDirectBuf()`, clears input state, updates byte counters, and returns up to the caller's requested length.

State and persistence: state includes direct buffers, saved user buffer offsets, `finish`/`finished`, `uncompressedDirectBufLen`, `bytesRead`, and `bytesWritten`. No persistent storage; `reset()` clears buffers/counters and `end()` is a no-op.

Dependencies and integration: implements Hadoop `Compressor`, uses `Configuration` only for `reinit()` reset semantics, and depends on lz4-java. It is used by Hadoop block compression streams that follow the `needsInput()`/`setInput()`/`compress()` contract.

Risks and test signals: test with input larger than direct buffer, empty `compress()` calls, small output buffers, `finish()`/`finished()` transitions, and both HC/non-HC construction. The class is synchronized; behavior changes should preserve thread safety and direct-buffer position/limit discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Compressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Decompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Decompressor.java

Purpose: Hadoop `Decompressor` adapter for LZ4 using `LZ4SafeDecompressor` and direct buffers.

Important APIs and control flow: construction allocates direct compressed and uncompressed buffers and initializes safe decompression through lz4-java. `setInput()` stores the caller buffer, copies up to `directBufferSize` into the compressed direct buffer, and resets the uncompressed buffer to empty. `needsInput()` first drains uncompressed output, then reloads saved input if present, otherwise asks for more input. `decompress()` drains pending uncompressed bytes, or calls `decompressDirectBuf()` for the current compressed chunk, marks `finished` after saved input is consumed, and returns up to `len`.

State and persistence: tracks compressed buffer length, saved user buffer offsets, direct buffers, and a `finished` flag. `getRemaining()` deliberately returns 0 because Hadoop's block decompressor stream should not use it here. `reset()` reinitializes buffer positions and saved input counters.

Dependencies and integration: implements Hadoop `Decompressor`, depends on lz4-java. It does not support dictionaries and has no direct decompressor nested class in this file.

Risks and test signals: important tests include chunk boundaries at direct-buffer size, partial output reads, malformed LZ4 data exceptions from lz4-java, and ensuring `needsInput()` does not release user buffers early. Note the logger is created with `Lz4Compressor.class.getName()`, which is harmless but can confuse log attribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/Lz4Decompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/package-info.java

Purpose: package-level documentation for Hadoop's LZ4 compression/decompression implementation.

Important APIs and control flow: no executable code; provides Javadoc link to LZ4 and marks the package as `Private` and `Unstable`.

State and persistence: no runtime state.

Dependencies and integration: classification annotations integrate with Hadoop's compatibility policy. The package contains `Lz4Compressor` and `Lz4Decompressor` implementations used by Hadoop compression codecs.

Risks and test signals: compile/Javadoc checks are enough. Any annotation change affects API compatibility expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyCompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyCompressor.java

Purpose: Hadoop `Compressor` implementation backed by Xerial Snappy, using direct buffers to bridge Hadoop's byte-array API to `Snappy.compress(ByteBuffer, ByteBuffer)`.

Important APIs and control flow: `setInput()` validates input and either copies into the direct input buffer or saves the user buffer for later chunking. `needsInput()` accounts for pending compressed output, full direct input, and saved user data. `compress()` drains pending output, initializes output buffer, feeds saved data when no input is staged, compresses the direct buffer with `Snappy.compress`, clears consumed input, sets `finished` once saved user data is exhausted, and updates byte counters.

State and persistence: maintains direct buffers, saved user buffer offsets, input length, finish flags, and read/write counters. `reset()` clears all in-memory state; `end()` is a no-op.

Dependencies and integration: implements Hadoop `Compressor`, uses `Configuration` only for `reinit()` reset, and depends on `org.xerial.snappy.Snappy`. It integrates with Hadoop compression streams and codec pooling.

Risks and test signals: test with inputs larger than 64 KiB, tiny output arrays, empty input after `finish()`, and counter values. There is no synchronization, unlike the LZ4 class, so callers must respect Hadoop compressor threading assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyCompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyDecompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyDecompressor.java

Purpose: Hadoop `Decompressor` plus nested `DirectDecompressor` implementation for Snappy using Xerial's ByteBuffer API.

Important APIs and control flow: `setInput()` stores caller bytes and copies a direct-buffer chunk. `needsInput()` drains pending uncompressed bytes, then refills compressed direct input from saved data or asks for more. `decompress()` drains pending uncompressed output or calls `Snappy.uncompress` through `decompressDirectBuf()`. `decompressDirect(ByteBuffer,ByteBuffer)` temporarily swaps the instance buffers to operate directly on caller-provided direct buffers, advances source/destination positions, and restores original state in `finally`.

State and persistence: holds direct buffers, compressed input length, saved user input offsets, and `finished`. `getRemaining()` intentionally returns 0 for `BlockDecompressorStream`. `SnappyDirectDecompressor` adds `endOfInput` to combine direct source exhaustion with frame completion.

Dependencies and integration: implements Hadoop `Decompressor`/`DirectDecompressor`, depends on Xerial Snappy, and uses direct buffers asserted by direct decompressor calls.

Risks and test signals: cover array and direct-buffer paths, nonzero destination positions, partial outputs, corrupt compressed data, and reset after direct decompression. The direct path assumes Snappy consumes the whole source or throws.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/SnappyDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/package-info.java

Purpose: package-level documentation for Hadoop's Snappy compression/decompression code.

Important APIs and control flow: contains no runtime logic; declares package annotations `Private` and `Unstable` and links to Snappy documentation.

State and persistence: no state.

Dependencies and integration: imports Hadoop classification annotations and scopes Snappy codec implementation classes.

Risks and test signals: compile/Javadoc only. Annotation changes alter Hadoop's advertised compatibility stance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/snappy/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipCompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipCompressor.java

Purpose: pure-Java gzip `Compressor` used when Hadoop needs a gzip stream wrapper around `java.util.zip.Deflater`, marked `@DoNotPool`.

Important APIs and control flow: `init()` creates a raw `Deflater` (`nowrap=true`) with `ZlibFactory` compression level/strategy and starts in `HEADER_BASIC`. `compress()` emits the fixed gzip header, deflates data in `INFLATE_STREAM`, then fills and emits the gzip trailer when the deflater finishes. `setInput()` passes bytes to the deflater and updates CRC-32 and uncompressed-size accumulator. `finish()` delegates to `Deflater.finish()`, while `finished()` requires both deflater completion and trailer emission.

State and persistence: stores mutable header/trailer offsets, CRC, accumulated length, extra-byte count, deflater, and shared gzip state labels from `BuiltInGzipDecompressor.GzipStateLabel`. No persistence; `reset()` and `reinit()` rebuild stream state.

Dependencies and integration: implements Hadoop `Compressor`; uses `DataChecksum.newCrc32()`, `ZlibFactory`, Java `Deflater`, and `AlreadyClosedException`. Gzip output is consumed by Hadoop gzip streams and Java gzip tools.

Risks and test signals: test partial header/trailer writes, very small output buffers, `compress()` after finished/ended, CRC/ISIZE trailer correctness, and reinit strategy handling. `accuBufLen` is an `int`, matching gzip trailer modulo 2^32 behavior but requiring large-stream coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipCompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipDecompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipDecompressor.java

Purpose: pure-Java gzip `Decompressor` that parses gzip members manually and delegates raw deflate bytes to `java.util.zip.Inflater`, marked `@DoNotPool`.

Important APIs and control flow: `setInput()` stores the caller buffer without copying. `decompress()` drives a state machine: parse basic/optional header fields, feed remaining bytes to `Inflater`, update CRC with produced output, rewind unconsumed trailer bytes from `Inflater.getRemaining()`, parse CRC and size trailer, and enter `FINISHED`. `needsInput()` is special: while not in `FINISHED`, it may ask for more input even outside the deflate stream. `getRemaining()` reports bytes after the current gzip member.

State and persistence: state includes `GzipStateLabel`, `Inflater`, user buffer offsets, a small local header/trailer buffer, CRC, header/trailer byte counters, and flags for optional fields. `reset()` clears the member parser; `end()` closes the inflater and sets `ENDED`.

Dependencies and integration: implements Hadoop `Decompressor`; depends on Java `Inflater`, `DataChecksum`, `AlreadyClosedException`, and gzip RFC layout. It is used when native zlib is unavailable or when a built-in gzip codec path is selected.

Risks and test signals: test basic gzip, optional filename/comment/extra/header-CRC fields, concatenated member leftover handling, one-byte input buffers, CRC/size failures, and calls after `end()`. The state machine depends on caller preserving input until `needsInput()` says it is safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibDeflater.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibDeflater.java

Purpose: wrapper that adapts Java `Deflater` to Hadoop's `Compressor` interface for non-native zlib compression.

Important APIs and control flow: constructors mirror `Deflater` constructors. `compress()` delegates to `deflate(byte[],int,int)`. `reinit(Configuration)` resets, applies configured compression level, applies configured strategy when Java supports it, and falls back to `DEFAULT_STRATEGY` with a warning if unsupported.

State and persistence: inherited `Deflater` stream state is the only runtime state. No persistent storage.

Dependencies and integration: used by `ZlibFactory` when native zlib is not loaded. Implements `Compressor` and reads compression options through `ZlibFactory`.

Risks and test signals: test native-disabled fallback, unsupported strategy warnings, `reinit(null)`, and equivalence with `ZlibCompressor` for ordinary zlib streams. Callers must still invoke inherited `end()` to release native JDK zlib resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibDeflater.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibInflater.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibInflater.java

Purpose: wrapper that adapts Java `Inflater` to Hadoop's `Decompressor` interface for non-native zlib decompression.

Important APIs and control flow: constructors mirror `Inflater`; `decompress()` delegates to `inflate()` and converts `DataFormatException` to `IOException`.

State and persistence: all stream state is inherited from `Inflater`; no additional fields or persistence.

Dependencies and integration: selected by `ZlibFactory` when native zlib is unavailable. It participates in Hadoop's decompressor pool through the standard `Decompressor` API.

Risks and test signals: cover invalid compressed data error conversion, `nowrap` behavior, reset/end lifecycle inherited from `Inflater`, and parity with native `ZlibDecompressor` for common streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibInflater.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibCompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibCompressor.java

Purpose: native Hadoop zlib `Compressor` backed by JNI, with configurable compression level, strategy, and zlib/gzip/raw headers.

Important APIs and control flow: enum types map Java configuration to zlib integer parameters. Static initialization calls `NativeCodeLoader` and JNI `initIDs()`. Constructors call native `init()` and allocate direct buffers. `setInput()` copies user bytes into `uncompressedDirectBuf`; `needsInput()` considers pending compressed output, unconsumed direct input (`keepUncompressedBuf`), saved user data, and direct-buffer capacity. `compress()` drains pending output, calls native `deflateBytesDirect()`, updates direct-input tracking based on bytes consumed by JNI, and returns caller-sized output. `reinit()` resets, destroys the old native stream, reloads level/strategy, and creates a new native stream.

State and persistence: state includes native `stream` pointer, direct buffers, offsets/lengths, `keepUncompressedBuf`, saved user input, and finish flags. `end()` releases native stream; `checkStream()` throws after close. No persistence.

Dependencies and integration: implements Hadoop `Compressor`, uses Hadoop native libraries and `ZlibFactory` configuration keys. `ZlibFactory` selects this class only when both native compressor/decompressor loaded.

Risks and test signals: test JNI availability fallback, reinit after data, dictionaries, all `CompressionHeader` modes, output buffer smaller than native output, `finish()` drain behavior, and `end()` idempotence. Native pointer lifecycle and direct-buffer position accounting are the main risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibCompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.java

Purpose: native Hadoop zlib `Decompressor` with array and direct-buffer decompression paths and configurable header detection.

Important APIs and control flow: static initialization mirrors `ZlibCompressor`. `setInput()` stores caller bytes and copies up to the direct buffer. `needsInput()` drains uncompressed output, reloads saved compressed input, or asks for more. `decompress()` drains pending output, rewinds output direct buffer, calls native `inflateBytesDirect()`, and returns available bytes. `getRemaining()` combines saved user input with native remaining bytes. `inflateDirect()` temporarily points instance buffers at caller direct buffers and advances source based on native-consumed offsets.

State and persistence: stores native `stream`, header mode, compressed/uncompressed direct buffers, compressed offsets/lengths, user input offsets, `finished`, and `needDict`. `reset()` clears native and Java state; `end()` releases native stream; `finalize()` calls `end()`.

Dependencies and integration: implements Hadoop `Decompressor`; nested `ZlibDirectDecompressor` implements `DirectDecompressor`. Used by `ZlibFactory` for native zlib and direct decompression.

Risks and test signals: cover dictionary-needed streams, autodetect gzip/zlib mode, direct decompressor nonzero positions, concatenated/post-stream remaining bytes, reset after corrupt data, and closed-stream access. JNI/native state and direct buffer mutation are the key correctness risks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibFactory.java

Purpose: central factory and configuration helper for choosing native or built-in zlib compressor/decompressor implementations.

Important APIs and control flow: static initialization calls `loadNativeZLib()`, which checks `NativeCodeLoader` plus native zlib compressor/decompressor readiness and logs success/failure. Factory methods return native `ZlibCompressor`/`ZlibDecompressor` or Java `BuiltInZlibDeflater`/`BuiltInZlibInflater`. Direct decompression is available only for native zlib. Setter/getter methods store compression strategy and level as enum values in `Configuration`.

State and persistence: a static boolean `nativeZlibLoaded` controls factory choices; `setNativeZlibLoaded()` exists for tests. Configuration keys persist only in caller-provided `Configuration`.

Dependencies and integration: integrates Hadoop compression codecs with native zlib, Java fallback classes, `Configuration`, `NativeCodeLoader`, and `DirectDecompressor`.

Risks and test signals: test native-loaded and native-disabled branches, direct decompressor null fallback, configuration round trips, and library-name access when native is absent. Static mutable state must be isolated in tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/package-info.java

Purpose: package-level documentation for Hadoop zlib/gzip compression code.

Important APIs and control flow: no executable code; marks package `Private` and `Unstable` and documents implementation of the zlib compression algorithm.

State and persistence: none.

Dependencies and integration: imports Hadoop classification annotations and scopes native zlib, Java fallback, and gzip wrapper classes.

Risks and test signals: compile/Javadoc checks only. Annotation changes would affect compatibility promises.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardCompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardCompressor.java

Purpose: Hadoop `Compressor` backed by `zstd-jni` streaming compression, with configurable compression level, worker count, and direct-buffer sizes.

Important APIs and control flow: constructors allocate direct buffers and a `ZstdCompressCtx`; `getRecommendedBufferSize()` uses `ZstdOutputStream.recommendedCOutSize()`. `setInput()` copies caller bytes into the direct input buffer. `needsInput()` considers pending compressed output, partially consumed direct input, and saved user input. `compress()` always invokes `compressDirectByteBufferStream`, using `CONTINUE` until `finish()` is set and all input is consumed, then `END`; it tracks consumed input/output bytes, manages `keepUncompressedBuf`, marks `finished` when zstd reports end, and drains compressed output to the caller. `reinit()` reloads level/workers from `ZStandardCodec`.

State and persistence: state includes `ZstdCompressCtx`, direct buffers, saved input offsets, direct-buffer offsets, finish flags, read/write counters, compression level, and worker count. `end()` closes the context; `finalize()` also closes.

Dependencies and integration: implements Hadoop `Compressor`, uses `ZStandardCodec` and Hadoop configuration defaults, and depends on `com.github.luben.zstd`.

Risks and test signals: test multi-threaded workers, `finish()` with internally buffered zstd output, small output arrays, input larger than direct buffer, reinit/reset, and operations after `end()`. Streaming API semantics are subtle because `CONTINUE` may leave jobs in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardCompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardDecompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardDecompressor.java

Purpose: Hadoop Zstandard `Decompressor` plus direct decompressor backed by `zstd-jni` streaming decompression.

Important APIs and control flow: construction allocates direct buffers and `ZstdDecompressCtx`; `getRecommendedBufferSize()` uses `ZstdInputStream.recommendedDInSize()`. `setInput()` copies compressed caller bytes into the direct buffer. `needsInput()` drains uncompressed output first, then refills compressed input from saved user data. `decompress()` calls `decompressDirectByteBufferStream`, updates consumed compressed offset, tracks `remaining`, marks finished only when the zstd frame is done and no compressed bytes remain, then drains output. `inflateDirect()` performs the same streaming call against caller direct buffers for the nested `ZStandardDirectDecompressor`.

State and persistence: tracks zstd context, direct buffers, compressed offsets/counts, user input counters, `remaining`, and `finished`. `reset()` clears stream and buffer state; `end()` closes the context; `finalize()` calls `end()`.

Dependencies and integration: implements Hadoop `Decompressor` and nested `DirectDecompressor`, depends on `com.github.luben.zstd`.

Risks and test signals: test concatenated frames/remaining bytes, direct buffer source/destination positions, reset after corrupt data, unsupported dictionary calls, and after-close errors. Finish semantics depend on both zstd frame completion and local buffer exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/ZStandardDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/package-info.java

Purpose: package-level documentation for Hadoop's Zstandard compression/decompression implementation.

Important APIs and control flow: no executable code; marks the package private/unstable and links to Zstandard.

State and persistence: none.

Dependencies and integration: imports Hadoop classification annotations and scopes the zstd compressor/decompressor adapters.

Risks and test signals: compile/Javadoc checks only. Annotation changes should be reviewed as API-compatibility changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zstd/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecRegistry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecRegistry.java

Purpose: singleton registry mapping erasure codec names to ordered `RawErasureCoderFactory` implementations discovered through `ServiceLoader`.

Important APIs and control flow: constructor loads `RawErasureCoderFactory` providers and calls `updateCoders()`. `updateCoders()` groups factories by codec, rejects duplicate coder names, inserts native RS/XOR factories at the front as defaults, and rebuilds coder-name arrays plus compact comma-separated maps. Public methods expose coder names, factories, codec names, lookup by codec/coder name, and compact codec-to-coder map.

State and persistence: singleton `instance` holds mutable maps in memory. No disk persistence; provider availability depends on classpath service metadata.

Dependencies and integration: depends on raw coder factory classes, Java `ServiceLoader`, and Hadoop testing annotation. Used by `CodecUtil` to select raw encoder/decoder factories.

Risks and test signals: test duplicate coder registration, native factory precedence, empty/missing codec behavior, and compact map freshness. `getCoderByName()` assumes `getCoders()` is non-null; callers must check codec availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecUtil.java

Purpose: factory utility for high-level erasure codecs/coders and raw erasure coders, driven by Hadoop configuration and `CodecRegistry`.

Important APIs and control flow: constants define configuration keys for codec class names, raw coder order, and native enablement. `createEncoder()`/`createDecoder()` resolve the codec class name for a schema, instantiate it reflectively with `(Configuration, ErasureCodecOptions)`, and return its encoder/decoder. `createRawEncoder()`/`createRawDecoder()` obtain ordered raw coder names from configuration or the registry, skip native coders when disabled, try factories in order, and fall back on exceptions until one succeeds.

State and persistence: stateless utility; all durable choices are in `Configuration` or classpath service registration.

Dependencies and integration: integrates `ECSchema`, `ErasureCodecOptions`, high-level codec classes, raw coder factories, reflection, and `CodecRegistry`. It is the main bridge from HDFS/EC policy configuration to actual coding implementations.

Risks and test signals: test default RS/XOR/HHXOR class resolution, custom codec missing config errors, native-disabled fallback, factory failure fallback, and reflection constructor failures. `createRawCoderFactory()` can return null, so fallback tests should cover null/exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlock.java

Purpose: minimal block-level metadata wrapper for erasure coding, representing whether a block is parity and whether it is erased/missing.

Important APIs and control flow: constructors set `isParity` and `isErased`; setters and getters expose those flags. There is no validation or behavior beyond flag storage.

State and persistence: two mutable booleans, no persistence. It intentionally avoids HDFS block details so higher layers can subclass or wrap.

Dependencies and integration: used by `ECBlockGroup`, `BlockGrouper`, and coder step selection to identify input/output blocks.

Risks and test signals: tests should ensure erased/parity flags propagate into decoder output selection. Since fields are mutable, callers must avoid sharing instances across concurrent recovery calculations without coordination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlockGroup.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlockGroup.java

Purpose: groups data and parity `ECBlock` arrays for one erasure coding operation.

Important APIs and control flow: constructor stores data/parity arrays; getters return those arrays directly. `getErasedCount()` iterates data then parity blocks and counts `isErased()` flags.

State and persistence: stores mutable array references and mutable block objects. No persistence or defensive copying.

Dependencies and integration: produced by `BlockGrouper`; consumed by `ErasureEncoder` and `ErasureDecoder` to select coding input/output blocks.

Risks and test signals: tests should cover erased count across both arrays and caller mutation effects. There is no null checking, so higher layers must supply complete arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlockGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECChunk.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECChunk.java

Purpose: wraps a `ByteBuffer` slice or byte array as the chunk-level data unit passed to raw erasure coders.

Important APIs and control flow: constructors wrap whole buffers/arrays or slice a `ByteBuffer` using offset/length. `toBuffers()` converts nullable `ECChunk[]` to nullable `ByteBuffer[]`. `toBytesArray()` copies remaining bytes without changing the original buffer position via mark/reset. `allZero` is a metadata flag for optimized handling.

State and persistence: stores one `ByteBuffer` and mutable `allZero`; underlying buffer content is external mutable state. No persistence.

Dependencies and integration: used by `ErasureCodingStep.performCoding()`, `ErasureEncodingStep`, `ErasureDecodingStep`, and HH-XOR steps to bridge block/chunk abstractions to raw byte-buffer coders.

Risks and test signals: test array-backed/direct buffers, slices, null conversion, mark/reset behavior, and all-zero propagation. Buffer position/limit semantics are critical because raw coders often advance positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECChunk.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECSchema.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECSchema.java

Purpose: serializable public/evolving value object describing an erasure coding schema: codec name, number of data units, number of parity units, and codec-specific extra options.

Important APIs and control flow: map constructor extracts `codec`, `numDataUnits`, and `numParityUnits`, validates positive integers, removes those entries from the provided map, and stores remaining options as unmodifiable extras. Direct constructors accept key parameters and optional extras. Getters expose fields; `toString()`, `equals()`, and `hashCode()` include all fields including extras.

State and persistence: immutable final fields plus unmodifiable map; serializable with fixed `serialVersionUID`. The map constructor mutates its input map while stripping core keys.

Dependencies and integration: used by `ErasureCodecOptions`, codec creation, `BlockGrouper`, and EC policy handling outside this subset.

Risks and test signals: test validation messages, input-map mutation, equality/hash with extra options, and serialization compatibility. Direct constructors rely on assertions for validation, so production callers should validate before construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECSchema.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeConstants.java

Purpose: shared constant names for built-in erasure codecs and raw coder implementations.

Important APIs and control flow: defines codec names such as `rs`, `rs-legacy`, `xor`, and `hhxor`, plus coder names such as `rs_java`, `rs_native`, `xor_java`, `xor_native`, and `dummy`. No executable methods.

State and persistence: static constants only.

Dependencies and integration: referenced by `CodecUtil`, codec/coder classes, and raw coder factories to avoid string drift in configuration and registration.

Risks and test signals: tests should catch renamed constants through codec factory/configuration integration. Changing values is a compatibility risk for persisted EC policies and configuration keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeNative.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeNative.java

Purpose: native erasure-code library availability probe and library-name accessor.

Important APIs and control flow: static initialization checks `NativeCodeLoader.isNativeCodeLoaded()`, calls native `initIDs()`, and sets `nativeLoaded` based on success. `checkNativeCodeLoaded()` throws a `RuntimeException` when unavailable. `isNativeCodeLoaded()` exposes the boolean, and `getLibraryName()` is native.

State and persistence: static boolean `nativeLoaded` is process-local. No persistence.

Dependencies and integration: used by native raw coder implementations and factories to determine ISA-L/native support. Depends on Hadoop native loader and JNI symbols.

Risks and test signals: test no-native and native-loaded paths, error messages from `checkNativeCodeLoaded()`, and library-name availability. Static initialization can hide root causes because it catches `Throwable`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeNative.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodecOptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodecOptions.java

Purpose: small options carrier for high-level erasure codecs, currently wrapping only an `ECSchema`.

Important APIs and control flow: constructor stores schema; `getSchema()` returns it. No validation or derived behavior.

State and persistence: one mutable-reference field; no persistence.

Dependencies and integration: passed into `ErasureCodec` constructors by `CodecUtil`, then used to derive `ErasureCoderOptions`.

Risks and test signals: test null-schema behavior at callers, because this class does not reject null. Future options should consider immutability and compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodecOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCoderOptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCoderOptions.java

Purpose: immutable raw/high-level coder options capturing data/parity unit counts and behavior flags.

Important APIs and control flow: constructors set `numDataUnits`, `numParityUnits`, computed `numAllUnits`, `allowChangeInputs`, and `allowVerboseDump`. Getters expose counts and flags.

State and persistence: final primitive fields only. No validation, persistence, or mutation.

Dependencies and integration: produced by `ErasureCodec` from `ECSchema` and passed into high-level and raw erasure coders.

Risks and test signals: test count propagation into raw coders and behavior when invalid counts are supplied. Since validation is external, factory tests should cover schema-to-options invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCoderOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/DummyErasureCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/DummyErasureCodec.java

Purpose: test/performance codec that creates dummy encoders/decoders which avoid real erasure math.

Important APIs and control flow: extends `ErasureCodec`; `createEncoder()` returns `DummyErasureEncoder`, and `createDecoder()` returns `DummyErasureDecoder`, both using inherited coder options.

State and persistence: no additional state beyond `ErasureCodec`.

Dependencies and integration: integrates dummy high-level coders into the same codec abstraction used by real RS/XOR/HHXOR codecs.

Risks and test signals: useful as a test signal itself for isolating HDFS pipeline overhead. Verify it is not selected accidentally for production schemas unless explicitly configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/DummyErasureCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/ErasureCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/ErasureCodec.java

Purpose: abstract high-level erasure codec base that owns schema/options, creates encoder/decoder instances, and supplies a block grouper.

Important APIs and control flow: constructor extracts schema from `ErasureCodecOptions` and creates `ErasureCoderOptions` with `allowChangeInputs=false` and verbose dump disabled. Getters expose name, schema, codec options, and coder options. Abstract `createEncoder()`/`createDecoder()` are implemented by concrete codecs. `createBlockGrouper()` creates a `BlockGrouper` and attaches the schema.

State and persistence: stores schema, codec options, and coder options in memory. Protected setters allow subclasses to replace options.

Dependencies and integration: created reflectively by `CodecUtil`; used by EC manager logic to obtain coders and grouping behavior.

Risks and test signals: test schema-to-coder-option count propagation, block grouper schema assignment, and subclass option mutation. Default `allowChangeInputs=false` is an integration contract with raw coders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/ErasureCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/HHXORErasureCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/HHXORErasureCodec.java

Purpose: concrete high-level Hitchhiker-XOR codec.

Important APIs and control flow: constructor delegates to `ErasureCodec`; `createEncoder()` returns `HHXORErasureEncoder`, and `createDecoder()` returns `HHXORErasureDecoder`.

State and persistence: no additional state beyond base codec fields.

Dependencies and integration: selected by `CodecUtil` for `hhxor` schemas and bridges to HH-XOR coder classes that compose RS and XOR raw coders.

Risks and test signals: integration tests should verify `hhxor` schema resolution and that generated coders receive the expected data/parity counts. HH-XOR has stronger assumptions about parity counts and sub-packetization in the coder step classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/HHXORErasureCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/RSErasureCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/RSErasureCodec.java

Purpose: concrete high-level Reed-Solomon erasure codec.

Important APIs and control flow: constructor delegates to `ErasureCodec`; `createEncoder()` returns `RSErasureEncoder`; `createDecoder()` returns `RSErasureDecoder`.

State and persistence: no additional state beyond inherited schema/options.

Dependencies and integration: selected for `rs` and currently also `rs-legacy` by `CodecUtil`; uses RS high-level coders which lazily create raw RS coders.

Risks and test signals: test codec class resolution for both RS names and raw coder fallback. The TODO in `CodecUtil` around `rs-legacy` means legacy behavior may need separate validation outside this thin class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/RSErasureCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/XORErasureCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/XORErasureCodec.java

Purpose: concrete high-level XOR erasure codec.

Important APIs and control flow: constructor delegates to `ErasureCodec` and asserts the schema has exactly one parity unit. `createEncoder()` returns `XORErasureEncoder`; `createDecoder()` returns `XORErasureDecoder`.

State and persistence: no additional fields.

Dependencies and integration: selected by `CodecUtil` for `xor` schemas and bridges to XOR high-level coders.

Risks and test signals: test one-parity schema enforcement with assertions enabled and upper-layer validation with assertions disabled. XOR recovery can only tolerate one erased block, enforced more directly by grouping/recovery decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/XORErasureCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/package-info.java

Purpose: package-level documentation for the erasure codec framework.

Important APIs and control flow: no executable code; marks package `Private` and `Unstable`.

State and persistence: none.

Dependencies and integration: classification annotations advertise the API status of high-level codec classes.

Risks and test signals: compile/Javadoc only. Annotation changes affect API compatibility expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureDecoder.java

Purpose: high-level decoder for the dummy codec, intended for tests and performance isolation.

Important APIs and control flow: `prepareDecodingStep()` creates a `DummyRawDecoder`, builds input blocks via base decoder logic, calculates erased indexes, selects output blocks, and returns `ErasureDecodingStep`.

State and persistence: no cached raw decoder; each coding step creates a new dummy raw decoder. No persistence.

Dependencies and integration: extends `ErasureDecoder` and uses `DummyRawDecoder`, `ECBlockGroup`, and `ErasureDecodingStep`.

Risks and test signals: verify erased-index ordering and output-block selection match base decoder behavior. It should not be used to validate data correctness because it performs no real reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureEncoder.java

Purpose: high-level encoder for the dummy codec, used to isolate non-codec overhead.

Important APIs and control flow: `prepareEncodingStep()` creates a `DummyRawEncoder`, selects data input blocks and parity output blocks, and wraps them in `ErasureEncodingStep`.

State and persistence: no cached raw encoder; no persistence.

Dependencies and integration: extends `ErasureEncoder` and delegates to `DummyRawEncoder`.

Risks and test signals: useful for pipeline/performance tests, but not data-correctness tests. Verify it creates step shapes consistent with real encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCoder.java

Purpose: common interface for high-level erasure encoders and decoders that calculate coding steps over `ECBlockGroup`.

Important APIs and control flow: exposes data/parity counts, `ErasureCoderOptions`, `calculateCoding(ECBlockGroup)`, direct-buffer preference, and `release()`. Implementations are also Hadoop `Configurable`.

State and persistence: interface only; lifecycle contract requires implementations to release raw coder resources.

Dependencies and integration: used by codec classes and higher-level EC managers to decouple block group planning from raw chunk computation.

Risks and test signals: implementation tests should ensure `calculateCoding()` returns valid step input/output block arrays and that `release()` closes cached native/raw resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCodingStep.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCodingStep.java

Purpose: operation-level interface describing one encoding or decoding step over chunks.

Important APIs and control flow: exposes input/output `ECBlock[]`, `performCoding(ECChunk[],ECChunk[])`, and `finish()`. Current framework comments state only one step is supported, but the abstraction anticipates multi-step codecs.

State and persistence: interface only. Implementations may hold raw coder resources and block arrays.

Dependencies and integration: returned by `ErasureCoder.calculateCoding()` and consumed by callers that read/write chunks for selected blocks.

Risks and test signals: tests should verify chunk array lengths align with block arrays and that `finish()` releases or finalizes resources when implementations require it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCodingStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecoder.java

Purpose: abstract high-level decoder base implementing `ErasureCoder` for recovery calculations.

Important APIs and control flow: constructor stores counts/options. `calculateCoding()` delegates to subclass `prepareDecodingStep()`. Default `getInputBlocks()` concatenates data and parity blocks. Default `getOutputBlocks()` returns all erased data blocks followed by erased parity blocks. `getErasedIndexes()` computes indexes in the concatenated input array. `preferDirectBuffer()` defaults false and `release()` is no-op.

State and persistence: final count/options fields; configuration inherited from `Configured`. No persistence.

Dependencies and integration: base for RS, XOR, HH-XOR, and dummy decoders. It defines the block ordering contract passed to raw decoders.

Risks and test signals: test erased-index ordering, zero-erasure behavior, data/parity output ordering, and subclass overrides such as XOR. Block ordering mismatches will corrupt recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecodingStep.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecodingStep.java

Purpose: concrete decoding step that delegates chunk reconstruction to a `RawErasureDecoder`.

Important APIs and control flow: constructor stores input/output blocks, erased indexes, and raw decoder. `performCoding()` calls `rawDecoder.decode(inputChunks, erasedIndexes, outputChunks)`. Getters expose block arrays. `finish()` is only a TODO placeholder and does not release the raw decoder in this source version.

State and persistence: holds references to block arrays, erased indexes, and raw decoder resource. No persistence.

Dependencies and integration: created by high-level decoders and consumed by EC callers with chunk buffers.

Risks and test signals: verify erased-index/output-chunk alignment and raw decoder error propagation as `IOException`. Resource lifecycle must be handled by owning coders or future changes because this step's `finish()` currently does not release the raw decoder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecodingStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncoder.java

Purpose: abstract high-level encoder base implementing `ErasureCoder` for parity generation.

Important APIs and control flow: constructor stores counts/options. `calculateCoding()` delegates to subclass `prepareEncodingStep()`. `getInputBlocks()` returns data blocks; `getOutputBlocks()` returns parity blocks. Direct-buffer preference defaults false and `release()` defaults no-op.

State and persistence: final data/parity counts and options; Hadoop configuration from `Configured`. No persistence.

Dependencies and integration: base for RS, XOR, HH-XOR, and dummy encoders. It defines the normal data-to-parity block mapping for encoding steps.

Risks and test signals: test block array selection and count propagation. Subclasses with cached raw encoders should override `release()` as RS and HH-XOR do.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncodingStep.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncodingStep.java

Purpose: concrete encoding step that delegates parity generation to a `RawErasureEncoder`.

Important APIs and control flow: constructor stores input/output blocks and raw encoder. `performCoding()` calls `rawEncoder.encode(inputChunks, outputChunks)`. Getters expose block arrays. `finish()` is a no-op in this source version.

State and persistence: holds block arrays and raw encoder reference. No persistence.

Dependencies and integration: created by high-level encoders and invoked by chunk-level EC execution.

Risks and test signals: test chunk length validation through raw encoders and output chunk mutation. Resource lifecycle must be handled by owning coders or future changes because this step's `finish()` currently does not release the raw encoder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncodingStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHErasureCodingStep.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHErasureCodingStep.java

Purpose: abstract base for Hitchhiker coding steps, adding HH-specific sub-packetization and shared block storage.

Important APIs and control flow: constructor stores input/output blocks. `getSubPacketSize()` returns fixed value 2. Getters expose blocks. `finish()` is currently a no-op.

State and persistence: stores input/output block arrays and a constant sub-packet size. No persistence.

Dependencies and integration: extended by HH-XOR encoding/decoding steps. The fixed sub-packet size drives expected chunk array shapes.

Risks and test signals: test HH chunk array sizing as `numUnits * 2`. If future HH variants need different sub-packet sizes, this constant becomes a compatibility point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHErasureCodingStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecoder.java

Purpose: high-level Hitchhiker-XOR decoder that composes RS raw decoding with XOR raw encoding for piggyback recovery.

Important APIs and control flow: lazily creates and caches an RS raw decoder and XOR raw encoder through `CodecUtil`. `prepareDecodingStep()` builds concatenated input blocks, erased indexes, output blocks, and returns `HHXORErasureDecodingStep`. `release()` releases both cached raw coders.

State and persistence: caches raw decoder/encoder references in memory. No persistence.

Dependencies and integration: extends `ErasureDecoder`, uses `ErasureCodeConstants.RS_CODEC_NAME` and `XOR_CODEC_NAME`, and delegates complex recovery to HH-XOR decoding step.

Risks and test signals: test cached raw coder reuse and release, native/raw fallback selection, and erased-index/output alignment for single and multiple erasures. The raw coder configuration must be present for both RS and XOR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecodingStep.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecodingStep.java

Purpose: implements HH-XOR chunk recovery logic using RS decoding plus piggyback XOR adjustments.

Important APIs and control flow: constructor computes `pbIndex`, piggyback partition indexes, and stores erased indexes plus raw coders. `performCoding()` converts chunks to buffers and exits early with no erasures. It reshapes flat input/output arrays into `[subPacket][unit]` matrices. Single data erasure uses `doDecodeSingle()`: decode second sub-packet with RS, derive a piggyback from read parity, recover first sub-packet by XORing the piggyback with surviving inputs, and advance input positions. Multiple erasures or parity erasures use `doDecodeMultiAndParity()`: RS-decode first sub-stripe, compute piggybacks, remove piggybacks from available parity, RS-decode second sub-stripe, then reapply/remove piggybacks for recovered parity outputs.

State and persistence: stores piggyback indexes, erased indexes, raw RS decoder, and XOR encoder. It mutates `ByteBuffer` contents and positions during coding; no persistence.

Dependencies and integration: depends on `HHUtil`, `RSUtil.GF`, `RawErasureDecoder`, and `RawErasureEncoder`. Created by `HHXORErasureDecoder`.

Risks and test signals: cover single data erasure, multiple data erasures, parity erasures, direct and heap buffers, buffer positions, and invalid array lengths. The method name typo `fisrtValidInput` is harmless; the substantive risk is position/index arithmetic and piggyback partition assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecodingStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncoder.java

Purpose: high-level Hitchhiker-XOR encoder that composes RS raw encoding with XOR raw encoding.

Important APIs and control flow: lazily creates cached RS and XOR raw encoders through `CodecUtil`; `prepareEncodingStep()` selects data/parity blocks and returns `HHXORErasureEncodingStep`; `release()` releases both cached encoders.

State and persistence: caches raw encoder references in memory. No persistence.

Dependencies and integration: extends `ErasureEncoder`, uses RS and XOR raw coders, and creates the HH-XOR-specific encoding step.

Risks and test signals: test raw coder fallback for both codecs, repeated coding step creation with cached encoders, and release idempotence. Configuration must support both RS and XOR raw coders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncodingStep.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncodingStep.java

Purpose: implements HH-XOR parity generation by RS-encoding sub-packets and adding piggybacks to selected second-sub-packet parity outputs.

Important APIs and control flow: constructor stores RS/XOR raw encoders and computes piggyback partition indexes. `performCoding()` converts chunks to buffers, validates flat input/output lengths as `dataUnits * 2` and `parityUnits * 2`, reshapes to sub-packet matrices, and calls `doEncode()`. `doEncode()` computes piggybacks from the first sub-packet with `HHUtil.getPiggyBacksFromInput()`, RS-encodes each sub-packet, then XORs piggybacks into second-sub-packet parity indexes 1..N.

State and persistence: stores piggyback index and raw encoders. Mutates output buffer content without changing the intended logical positions. No persistence.

Dependencies and integration: depends on `HHUtil`, `ECChunk`, `RawErasureEncoder`, and direct/heap `ByteBuffer` operations. Created by `HHXORErasureEncoder`.

Risks and test signals: test direct vs heap paths, parity count edge cases, invalid input/output lengths, and parity byte-for-byte compatibility with HH-XOR decode. Piggyback indexing assumes `numParityUnits > 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncodingStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureDecoder.java

Purpose: high-level Reed-Solomon decoder that creates an `ErasureDecodingStep` backed by a raw RS decoder.

Important APIs and control flow: `prepareDecodingStep()` obtains input/output block arrays, lazily creates a raw decoder through `CodecUtil.createRawDecoder(..., RS_CODEC_NAME, ...)`, and returns `ErasureDecodingStep` with erased indexes. `release()` releases the cached raw decoder.

State and persistence: caches one raw decoder reference; no persistence.

Dependencies and integration: extends `ErasureDecoder` and relies on `CodecUtil`/`CodecRegistry` raw coder fallback.

Risks and test signals: test all erased-index combinations up to parity count, raw coder fallback, release behavior, and configuration propagation. A TODO in the paired encoder notes codec-specific raw coder selection may need refinement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureEncoder.java

Purpose: high-level Reed-Solomon encoder that creates an `ErasureEncodingStep` backed by a raw RS encoder.

Important APIs and control flow: `prepareEncodingStep()` lazily creates a raw RS encoder via `CodecUtil.createRawEncoder(..., RS_CODEC_NAME, ...)`, selects data/parity blocks, and returns `ErasureEncodingStep`. `release()` releases the cached raw encoder. `preferDirectBuffer()` returns false despite possible native raw coder preference.

State and persistence: caches one raw encoder reference; no persistence.

Dependencies and integration: extends `ErasureEncoder`; raw coder choice comes from configuration/registry.

Risks and test signals: test raw coder fallback, cached encoder reuse, release, and parity output correctness across heap/direct chunks. The TODO about codec-specific raw coder selection should be tracked for `rs-legacy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureDecoder.java

Purpose: high-level XOR decoder for recovering one missing data or parity block.

Important APIs and control flow: `prepareDecodingStep()` creates a raw XOR decoder through `CodecUtil`, builds default input blocks and erased indexes, uses an overridden `getOutputBlocks()` that orders erased parity blocks before data blocks, and returns `ErasureDecodingStep`.

State and persistence: no cached raw decoder; each step creates one. No persistence.

Dependencies and integration: extends `ErasureDecoder`, uses `ErasureCodeConstants.XOR_CODEC_NAME`, and delegates math to raw XOR decoder.

Risks and test signals: test one-erasure recovery, parity-before-data output ordering, and upper-layer rejection of multiple erasures. Comments contain typos but signal that recoverability is checked above this class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureEncoder.java

Purpose: high-level XOR encoder that creates parity with a raw XOR encoder.

Important APIs and control flow: `prepareEncodingStep()` creates a raw XOR encoder through `CodecUtil`, selects data blocks and parity output blocks, and returns `ErasureEncodingStep`.

State and persistence: no cached raw encoder; no persistence.

Dependencies and integration: extends `ErasureEncoder` and delegates to configured raw XOR encoder.

Risks and test signals: test parity generation, raw coder fallback, and resource release via step `finish()`. Repeated step creation creates repeated raw encoders, unlike RS/HH-XOR cached implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/package-info.java

Purpose: package-level documentation for the high-level erasure coder framework.

Important APIs and control flow: no executable code; marks package `Private` and `Unstable`.

State and persistence: none.

Dependencies and integration: classification annotations cover encoder/decoder/step framework classes.

Risks and test signals: compile/Javadoc checks only. Annotation changes affect API compatibility expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/util/HHUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/util/HHUtil.java

Purpose: static utility methods for Hitchhiker-XOR piggyback partitioning, piggyback generation, buffer allocation, and valid-input discovery.

Important APIs and control flow: `initPiggyBackIndexWithoutPBVec()` partitions data units across parity-derived piggyback sets; `initPiggyBackFullIndexVec()` maps each data unit to its piggyback set. `getPiggyBacksFromInput()` repeatedly builds temporary input/output buffers, uses a raw encoder to encode each piggyback group, clones selected parity output, and restores input positions. `getPiggyBackForDecode()` derives the piggyback needed for single-erasure recovery from read parity and decoded parity, using GF addition. `findFirstValidInput()` returns the first non-null input or throws `HadoopIllegalArgumentException`.

State and persistence: stateless utility, but methods allocate temporary heap/direct buffers and mutate positions on temporary and passed buffers carefully.

Dependencies and integration: used by HH-XOR encoding/decoding steps; depends on `RawErasureEncoder`, `RSUtil.GF`, and `ByteBuffer`.

Risks and test signals: test partition indexes for varied data/parity counts, direct/heap clone behavior, input-position restoration, all-null input failures, and piggyback decode math. `numDataUnits / (numParityUnits - 1)` can be dangerous for unsupported parity counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/util/HHUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/grouper/BlockGrouper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/grouper/BlockGrouper.java

Purpose: schema-aware helper for forming block groups and determining whether erased blocks are recoverable.

Important APIs and control flow: `setSchema()` stores schema; `getRequiredNumDataBlocks()` and `getRequiredNumParityBlocks()` return schema counts. `makeBlockGroup()` wraps data/parity arrays in `ECBlockGroup`. `anyRecoverable()` returns true when erased count is greater than zero and no more than parity count.

State and persistence: stores one schema reference; no persistence.

Dependencies and integration: created by `ErasureCodec.createBlockGrouper()` and used by EC managers to shape encoding/recovery work.

Risks and test signals: test recoverability boundaries, null/unset schema behavior, and data/parity array sizing outside this class. The recoverability rule is generic; codec-specific constraints such as XOR one-erasure assumptions may need upper-layer checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/grouper/BlockGrouper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawDecoder.java

Purpose: base class for native raw erasure decoders, providing lock-protected ByteBuffer decode plumbing and byte-array fallback conversion.

Important APIs and control flow: `doDecode(ByteBufferDecodingState)` takes a read lock, rejects use after native coder close (`nativeCoder == 0`), records input/output buffer positions as offset arrays, and calls subclass `performDecodeImpl()`. `doDecode(ByteArrayDecodingState)` logs a performance advisory, converts arrays to ByteBuffer state, delegates, then copies decoded output bytes back to arrays. `preferDirectBuffer()` returns true.

State and persistence: contains a `ReentrantReadWriteLock` and a private native pointer field used by JNI. No persistence; native lifecycle is coordinated by subclasses/raw coder base classes.

Dependencies and integration: extends `RawErasureDecoder`; used by native ISA-L decoders. Subclasses implement JNI bridge method `performDecodeImpl()`.

Risks and test signals: test decode after release, concurrent decode/release locking in subclasses, heap-array fallback correctness, and buffer position preservation/advancement by raw coder framework. Native pointer visibility is intentionally private for JNI use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawEncoder.java

Purpose: base class for native raw erasure encoders, providing lock-protected ByteBuffer encode plumbing and byte-array fallback conversion.

Important APIs and control flow: `doEncode(ByteBufferEncodingState)` takes a read lock, rejects closed native coder state, records input/output positions, derives `dataLen` from the first input's remaining bytes, and calls subclass `performEncodeImpl()`. `doEncode(ByteArrayEncodingState)` logs a performance advisory, converts arrays to ByteBuffers, delegates, then copies output bytes back. `preferDirectBuffer()` returns true.

State and persistence: contains a `ReentrantReadWriteLock` and private native pointer field for JNI. No persistence.

Dependencies and integration: extends `RawErasureEncoder`; native RS/XOR encoders subclass it and implement `performEncodeImpl()`.

Risks and test signals: test encode after close, direct-buffer preference propagation, heap-array conversion correctness, input/output offset calculation, and concurrent release behavior in concrete native encoders. Assumes all inputs have the same remaining length as input zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawEncoder.java -->
