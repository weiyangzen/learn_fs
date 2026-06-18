# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibCompressor.java

Purpose: native Hadoop zlib `Compressor` backed by JNI, with configurable compression level, strategy, and zlib/gzip/raw headers.

Important APIs and control flow: enum types map Java configuration to zlib integer parameters. Static initialization calls `NativeCodeLoader` and JNI `initIDs()`. Constructors call native `init()` and allocate direct buffers. `setInput()` copies user bytes into `uncompressedDirectBuf`; `needsInput()` considers pending compressed output, unconsumed direct input (`keepUncompressedBuf`), saved user data, and direct-buffer capacity. `compress()` drains pending output, calls native `deflateBytesDirect()`, updates direct-input tracking based on bytes consumed by JNI, and returns caller-sized output. `reinit()` resets, destroys the old native stream, reloads level/strategy, and creates a new native stream.

State and persistence: state includes native `stream` pointer, direct buffers, offsets/lengths, `keepUncompressedBuf`, saved user input, and finish flags. `end()` releases native stream; `checkStream()` throws after close. No persistence.

Dependencies and integration: implements Hadoop `Compressor`, uses Hadoop native libraries and `ZlibFactory` configuration keys. `ZlibFactory` selects this class only when both native compressor/decompressor loaded.

Risks and test signals: test JNI availability fallback, reinit after data, dictionaries, all `CompressionHeader` modes, output buffer smaller than native output, `finish()` drain behavior, and `end()` idempotence. Native pointer lifecycle and direct-buffer position accounting are the main risk.
