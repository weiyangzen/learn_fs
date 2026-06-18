# sources/compression/xz/src/liblzma/check/crc32_loongarch.h

Purpose: LoongArch hardware-accelerated CRC32 implementation.

Important APIs/types/functions: includes `<larchintrin.h>` and defines static `crc32_arch_optimized(const uint8_t *buf, size_t size, uint32_t crc_unsigned)` using LoongArch CRC intrinsics `__crc_w_b_w`, `__crc_w_h_w`, `__crc_w_w_w`, and `__crc_w_d_w`.

Control flow: complements the incoming CRC into a signed 32-bit state, handles short inputs byte-wise, aligns the buffer to 8 bytes, processes 64-bit chunks, handles 4/2/1-byte tails, and returns the complemented state as `uint32_t`.

State and persistence: no state beyond local CRC and pointers. Unlike ARM64, this header has no runtime detection helper in this file; build selection must ensure the target supports the intrinsics.

Dependencies/integration: included by `crc32_fast.c` when `CRC32_LOONGARCH` is defined; relies on common aligned little-endian read helpers and build-system CPU feature checks.

Risks: compiling or running on unsupported LoongArch toolchains/CPUs will fail or fault. Casts to signed integer widths reflect intrinsic signatures and must preserve CRC bit patterns.

Test signals: `tests/test_check.c` provides correctness coverage when built on LoongArch; cross-builds verify header availability and intrinsic compatibility.
