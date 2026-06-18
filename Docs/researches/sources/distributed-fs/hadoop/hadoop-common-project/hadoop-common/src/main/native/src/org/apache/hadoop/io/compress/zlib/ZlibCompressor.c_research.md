<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibCompressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibCompressor.c

## Purpose
`ZlibCompressor.c` implements Hadoop's native zlib compressor JNI backend. It dynamically loads zlib, creates `z_stream` instances, supports dictionaries, compresses direct buffers, and reports stream counters/library identity.

## Important APIs, Types, and Functions
JNI exports include `initIDs()`, `init()`, `setDictionary()`, `deflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `reset()`, `end()`, and `getLibraryName()`. It resolves `deflateInit2_`, `deflate`, `deflateSetDictionary`, `deflateReset`, and `deflateEnd`. On Windows, `LoadZlibTryHadoopNativeDir()` tries the native Hadoop DLL directory before falling back to system paths.

## Control Flow
`initIDs()` opens zlib and caches symbol pointers plus Java field IDs. `init()` allocates and zeroes `z_stream`, then calls `deflateInit2_` using Java compression level, strategy, and window bits. `setDictionary()` pins a Java byte array and passes the requested slice to zlib. `deflateBytesDirect()` pulls Java object fields, obtains direct buffer addresses, sets zlib input/output pointers, calls `deflate` with `Z_NO_FLUSH` or `Z_FINISH`, updates Java input offset/remaining fields, and marks the Java object finished when `Z_STREAM_END` occurs.

## State and Persistence
`z_stream` is lifecycle state stored in a Java `long`. Static field IDs and function pointers persist process-wide. Stream counters and zlib internal state persist until `reset()` or `end()`.

## Dependencies and Integration Points
It depends on zlib, JNI direct buffers, Hadoop platform config, `winutils` on Windows, and Java `ZlibCompressor`.

## Risks and Edge Cases
Direct-buffer failures return zero rather than throwing. Library handles are not closed. Dictionary calls use critical array sections and must remain short. Java must avoid using a stream after `end()`. Window bits and strategy validation is delegated to zlib and mapped to broad Java exceptions.

## Test Signals
Tests should cover compression round trips, gzip/raw/window-bit variants, dictionaries, finish and reset, counters, short output buffers, missing zlib library, Windows load fallback, and invalid level/strategy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibCompressor.c -->
