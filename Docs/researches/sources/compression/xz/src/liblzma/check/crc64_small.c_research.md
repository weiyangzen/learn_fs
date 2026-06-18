# sources/compression/xz/src/liblzma/check/crc64_small.c

Purpose: size-optimized CRC64 implementation that computes a single 256-entry ECMA-182 lookup table at runtime and updates CRC one byte at a time.

Important APIs/types/functions: static `uint64_t crc64_table[256]`, static `crc64_init()`, and exported `LZMA_API(uint64_t) lzma_crc64(const uint8_t *buf, size_t size, uint64_t crc)`.

Control flow: initialization folds each byte through eight steps using reversed ECMA polynomial `0xC96C5795D7870F42`. With constructor support the table is prepared before calls; otherwise `lzma_crc64()` uses a function-local `mythread_once(crc64_init)`. The update path complements the input CRC, indexes the table with the low byte XOR input byte, shifts right by eight, and returns the complemented result.

State and persistence: the table is private process-global mutable state during initialization and read-only afterward. There is no persistence beyond process memory.

Dependencies/integration: includes `check.h`; uses thread-once primitives from common headers. Selected by small-build configuration instead of the larger fast CRC64 table path.

Risks: byte-at-a-time performance can be significant for large streams using CRC64, the default XZ check. Any initialization race would corrupt checks, so constructor or `mythread_once` availability matters. Unlike CRC32 small, the table is private and not shared with LZ code.

Test signals: known CRC64 vectors and XZ Block round trips using CRC64. Repeated first-call tests under concurrency are useful for no-constructor builds.
