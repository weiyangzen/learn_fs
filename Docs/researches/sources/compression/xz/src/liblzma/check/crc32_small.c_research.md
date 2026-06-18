# sources/compression/xz/src/liblzma/check/crc32_small.c

Purpose: implements the size-optimized CRC32 backend used when liblzma is built with the small CRC path. It generates a single 256-entry IEEE CRC32 table at startup and exposes the public `lzma_crc32()` API.

Important APIs/types/functions: defines exported `uint32_t lzma_crc32_table[1][256]`, static `crc32_init()`, optional `lzma_crc32_init()`, and `LZMA_API(uint32_t) lzma_crc32(const uint8_t *buf, size_t size, uint32_t crc)`. The table is not static because the LZ encoder hash code can reuse it in small builds.

Control flow: initialization iterates all byte values and folds each through eight polynomial steps using reversed IEEE polynomial `0xEDB88320`. With constructor support this runs before use; otherwise `lzma_crc32()` calls `lzma_crc32_init()`, which wraps `crc32_init()` in `mythread_once()`. The CRC routine complements the incoming CRC, consumes bytes one at a time through table index `*buf ^ (crc & 0xFF)`, shifts right, and returns the complemented final value.

State and persistence: process-global table state is initialized once and then read-only in practice. There is no external persistence; thread safety depends on constructor ordering or `mythread_once`.

Dependencies/integration: includes `check.h` for the public check API and `crc_common.h` for table declarations/thread initialization. `block_header_encoder.c`, `block_header_decoder.c`, stream flags, index tests, and several container decoders depend on `lzma_crc32()`.

Risks: incorrect or skipped table initialization corrupts every CRC32 consumer, including XZ headers and lzip checks. The byte-at-a-time path is slower than fast slicing/arch implementations, so build configuration strongly affects performance. The non-static table is an internal ABI dependency for LZ hash code.

Test signals: CRC32 is exercised indirectly by stream flags, block header, index, lzip, and microlzma tests; focused regression should compare known vectors and repeated lazy initialization under threads.
