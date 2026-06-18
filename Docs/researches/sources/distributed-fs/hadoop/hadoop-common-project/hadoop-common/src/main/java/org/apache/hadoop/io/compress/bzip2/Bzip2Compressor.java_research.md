
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.java

## Purpose
`Bzip2Compressor` is the native/JNI-backed `Compressor` implementation for bzip2.

## Important APIs and Types
It implements `Compressor`. Constructors configure block size, work factor, and direct buffer size. Important methods include `reinit`, `setInput`, `needsInput`, `finish`, `finished`, `compress`, byte counters, `reset`, `end`, static `initSymbols`, and native `getLibraryName`.

## Control Flow
Input bytes are copied from the user buffer into a direct uncompressed buffer. `compress()` first drains any remaining compressed direct-buffer output, then rewinds the output buffer, calls native `deflateBytesDirect()`, and exposes produced bytes to the caller. `finish()` sets a flag consumed by native code. `reset()` and `reinit()` tear down and recreate the native stream.

## State and Persistence
State includes a native stream pointer, block size, work factor, direct buffers, user buffer offsets/lengths, flags for retained uncompressed buffer data, and finish/finished flags. State is synchronized per instance and process-local only.

## Dependencies and Integration
Loaded through `Bzip2Factory` after `NativeCodeLoader` and native symbol initialization. Used by `BZip2Codec` native stream paths and `CodecPool`.

## Risks
Native resource lifecycle depends on `end(stream)` being called during reset/reinit/end. `checkStream()` throws `NullPointerException` after `end()`, which can surface if closed compressors are reused incorrectly. Direct buffer sizes and native counters must remain consistent with Java buffer bookkeeping.

## Test Signals
`TestBzip2CompressorDecompressor` exercises native bzip2 round trips and a multithreaded smoke test when native bzip2 is available. CodecPool tests cover generic pooling mechanics.
