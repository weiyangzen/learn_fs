# sources/distributed-fs/ceph-client/lib/decompress_unlz4.c

## Purpose
Provides the LZ4 wrapper used to decompress LZ4-compressed kernel, initramfs, and initrd images.

## APIs, Types, and Functions
The main decompressor is `unlz4()`; preboot builds expose `__decompress()`. Constants include `LZ4_DEFAULT_UNCOMPRESSED_CHUNK_SIZE` and `ARCHIVE_MAGICNUMBER`. It uses either statically included `lz4_decompress.c` or the linked kernel LZ4 API.

## Control Flow
`unlz4()` validates input/output mode, allocates buffers when callbacks are used, optionally reads the first chunk size with `fill`, and handles an optional archive magic word. It then loops over little-endian chunk sizes, skips repeated magic words, treats zero as EOF for non-stream input, bounds streaming chunk sizes by `LZ4_compressBound()`, and decompresses each chunk with `LZ4_decompress_safe()` or preboot `LZ4_decompress_fast()` using the output length footer. It flushes each decompressed chunk or advances the caller output pointer, updates `posp`, and frees temporary buffers.

## State and Persistence
State is per-call: input/output buffer pointers, chunk sizes, remaining input size, and output cursor. There is no global state or persistence after return.

## Dependencies and Integration Points
Depends on Linux LZ4 APIs, unaligned little-endian reads, preboot allocation helpers, and the generic decompressor callback contract. It is selected by `decompress.c` for LZ4 magic and used by boot/initramfs decompression.

## Risks and Test Signals
Risks include incorrect handling of chunk-size framing, preboot footer assumptions, short `fill` or `flush`, malformed zero/magic chunks, and output-size mismatches. Test signals include LZ4-compressed boot artifacts, multi-chunk streams, truncated chunk headers, oversized chunk rejection, and streaming callback tests.
