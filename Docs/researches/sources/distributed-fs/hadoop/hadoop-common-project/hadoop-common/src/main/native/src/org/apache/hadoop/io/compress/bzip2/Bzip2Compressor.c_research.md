<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.c

## Purpose
`Bzip2Compressor.c` is the JNI compressor backend for Hadoop's bzip2 codec. It dynamically loads libbz2, caches Java field IDs, owns a native `bz_stream`, and compresses from Java direct input buffers into direct output buffers.

## Important APIs, Types, and Functions
JNI exports are `initIDs()`, `init()`, `deflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `end()`, and `getLibraryName()`. Cached symbol pointers include `BZ2_bzCompressInit`, `BZ2_bzCompress`, and `BZ2_bzCompressEnd`. Cached fields include `stream`, direct buffer references, offsets/lengths, `finish`, `finished`, and `directBufferSize`.

## Control Flow
`initIDs()` maps `"system-native"` to `HADOOP_BZIP2_LIBRARY` or uses a caller-supplied name, opens the library with `dlopen`, resolves symbols, and stores field IDs. `init()` allocates and zeroes `bz_stream`, initializes it with Java block size and work factor, and maps bzip2 errors to Java exceptions. `deflateBytesDirect()` retrieves the stream and Java direct buffer addresses, recalibrates `next_in`, `avail_in`, `next_out`, and `avail_out`, calls `BZ2_bzCompress` with `BZ_RUN` or `BZ_FINISH`, updates Java offsets and remaining length, and marks `finished` on `BZ_STREAM_END`.

## State and Persistence
The native stream persists until Java calls `end()`. Library function pointers and Java field IDs are process-static. Byte counters live in `bz_stream` and are exposed as 64-bit values composed from high/low bzip2 counters.

## Dependencies and Integration Points
It depends on libbz2, Hadoop dynamic-symbol macros, direct NIO buffers, Java `Bzip2Compressor`, and the shared bzip2 header's pointer conversion macros.

## Risks and Edge Cases
Direct-buffer address failure returns zero without throwing, relying on Java-side control flow. Library handles are not closed. Java must guarantee valid offsets and buffer sizes. `end()` frees even after successful `BZ2_bzCompressEnd`; double-closing the same handle would be unsafe.

## Test Signals
Round-trip compression/decompression, finish handling, partial-buffer progress, invalid block/work-factor errors, byte counters beyond 4 GiB, custom library name loading, and native close behavior are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.c -->
