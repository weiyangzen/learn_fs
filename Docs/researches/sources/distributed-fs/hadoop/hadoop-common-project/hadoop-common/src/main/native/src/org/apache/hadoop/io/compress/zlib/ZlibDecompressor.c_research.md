<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.c

## Purpose
`ZlibDecompressor.c` implements Hadoop's native zlib decompressor JNI backend. It dynamically loads inflate symbols, manages `z_stream` handles, supports dictionaries, and inflates direct-buffer input into direct-buffer output.

## Important APIs, Types, and Functions
JNI exports are `initIDs()`, `init()`, `setDictionary()`, `inflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `getRemaining()`, `reset()`, and `end()`. It resolves `inflateInit2_`, `inflate`, `inflateSetDictionary`, `inflateReset`, and `inflateEnd`, and shares the Windows zlib loader from the compressor file.

## Control Flow
`initIDs()` loads zlib and caches field IDs. `init()` allocates a zeroed stream and initializes inflate with Java window bits. `setDictionary()` pins a byte array and calls `inflateSetDictionary`. `inflateBytesDirect()` obtains Java buffer fields and direct addresses, recalibrates zlib input/output pointers, calls `inflate` with `Z_PARTIAL_FLUSH`, maps `Z_STREAM_END`, `Z_OK`, `Z_NEED_DICT`, `Z_BUF_ERROR`, `Z_DATA_ERROR`, and `Z_MEM_ERROR` to Java state or exceptions, and updates compressed input offsets/remaining bytes.

## State and Persistence
The native `z_stream` is held as a Java long until reset or end. Java fields hold `needDict`, `finished`, input offsets, and remaining input. Static function pointers and field IDs are process-wide.

## Dependencies and Integration Points
It depends on zlib, JNI direct buffers, Hadoop native macros, and Java `ZlibDecompressor`.

## Risks and Edge Cases
The code allocates `z_stream` then calls `memset` before checking whether allocation succeeded, which is a null-dereference risk on allocation failure. Direct-buffer failures return zero silently. Dictionary and data errors depend on zlib messages that may be null. Java must coordinate `needDict` and remaining input state correctly.

## Test Signals
Tests should include valid inflate, raw/gzip modes via window bits, dictionary-needed flows, corrupted data, reset reuse, small output buffers, missing zlib symbols, and allocation-failure hardening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.c -->
