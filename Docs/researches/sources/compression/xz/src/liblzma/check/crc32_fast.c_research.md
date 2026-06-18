# sources/compression/xz/src/liblzma/check/crc32_fast.c

Purpose: fast CRC32 implementation with optional architecture-specific acceleration and runtime dispatch.

Important APIs/types/functions: includes `check.h` and `crc_common.h`; optionally includes x86 CLMUL, ARM64, or LoongArch optimized headers. Defines generic `lzma_crc32_generic()` unless provided by x86 assembly, dispatch type `crc32_func_type`, resolver `crc32_resolve()`, constructor/first-call dispatch state, and public `LZMA_API(uint32_t) lzma_crc32()`.

Control flow: generic path complements and endian-adjusts CRC, aligns input, processes slice-by-eight table chunks, processes remaining bytes, reverses endian adjustment on big-endian, and returns complemented CRC. When both generic and optimized implementations exist, a constructor or first call selects the optimized function if `is_arch_extension_supported()` succeeds.

State and persistence: dispatch builds keep static function pointer `crc32_func`, initialized by constructor or first call. The first-call path intentionally lacks locking because concurrent resolvers assign the same target.

Dependencies/integration: public `lzma_crc32()` is used by stream flags, block headers, Index, lzip, tests, and LZ hash initialization. Depends on generated endian CRC tables or x86 assembly and architecture headers selected by configure.

Risks: dispatch without locking is pragmatically safe but not strictly standards-clean. Table endian assumptions must match `WORDS_BIGENDIAN`. Optimized and generic implementations must produce identical results for chunked and unaligned inputs.

Test signals: `tests/test_check.c` validates known string, unaligned input, byte-at-a-time chunking, and random data; many container/header tests indirectly rely on CRC32 correctness.
