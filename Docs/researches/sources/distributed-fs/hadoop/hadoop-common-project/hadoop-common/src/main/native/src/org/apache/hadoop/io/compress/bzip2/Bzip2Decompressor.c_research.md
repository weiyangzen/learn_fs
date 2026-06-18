<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.c

## Purpose
`Bzip2Decompressor.c` is the JNI decompressor backend for Hadoop's bzip2 codec. It loads libbz2 dynamically, manages `bz_stream` handles, and inflates compressed direct-buffer data into Java direct buffers.

## Important APIs, Types, and Functions
JNI exports include `initIDs()`, `init()`, `inflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `getRemaining()`, and `end()`. It resolves `BZ2_bzDecompressInit`, `BZ2_bzDecompress`, and `BZ2_bzDecompressEnd`, and caches fields for stream handle, compressed input buffer, offsets/lengths, uncompressed output buffer, output buffer size, and finished flag.

## Control Flow
`initIDs()` selects the bzip2 library name, loads it, resolves symbols, and caches field IDs. `init()` allocates and initializes a `bz_stream` with the Java conserve-memory flag. `inflateBytesDirect()` reads Java field state, obtains direct buffer addresses, sets `next_in`, `avail_in`, `next_out`, and `avail_out`, calls `BZ2_bzDecompress`, updates consumed input and remaining length, returns produced output bytes, and marks `finished` on stream end.

## State and Persistence
The native `bz_stream` persists through the Java decompressor lifecycle. Counters and remaining input live in the stream and Java object fields. No data is persisted outside memory.

## Dependencies and Integration Points
It depends on libbz2, JNI direct buffers, Hadoop's dynamic-symbol and exception macros, and Java `Bzip2Decompressor`.

## Risks and Edge Cases
Malformed data maps to `IOException` with a null message. Direct-buffer lookup failure returns zero without explaining the failure. Java offset/length validation is assumed. `getRemaining()` reports `avail_in`, so correctness depends on `inflateBytesDirect()` consistently updating Java-side compressed buffer fields.

## Test Signals
Tests should cover valid decompression, truncated and invalid magic data, conserve-memory mode, EOF marking, remaining-byte reporting, small output buffers, and teardown on both success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.c -->
