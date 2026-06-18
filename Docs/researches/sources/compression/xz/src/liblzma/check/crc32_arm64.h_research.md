# sources/compression/xz/src/liblzma/check/crc32_arm64.h

Purpose: ARM64 hardware-accelerated CRC32 implementation and runtime feature detection helper.

Important APIs/types/functions: includes ARM ACLE intrinsics except under MSVC; defines `crc_attr_target` for GCC/Clang `+crc`; implements static `crc32_arch_optimized(const uint8_t *buf, size_t size, uint32_t crc)` using `__crc32b/h/w/d`; when both generic and optimized variants are built, defines `is_arch_extension_supported()`.

Control flow: CRC calculation complements the incoming CRC, handles short inputs byte-wise, aligns to 8 bytes, processes 64-bit chunks, then handles 4/2/1-byte tails and complements the result. Runtime detection uses Linux `getauxval`, ELF aux info, Windows `IsProcessorFeaturePresent`, or Apple `sysctlbyname`, depending on available macros.

State and persistence: no persistent state; dispatch state lives in `crc32_fast.c` when both variants are compiled.

Dependencies/integration: included by `crc32_fast.c` under `CRC32_ARM64`; relies on aligned little-endian read helpers from common CRC code. Runtime detection availability is coordinated with `crc_common.h` and build-system checks.

Risks: hardware intrinsics must only execute on CPUs with CRC extension unless compiled for a target where it is guaranteed. Alignment math subtracts `align` from `size` after assuming `size >= 8`; this is safe only because the short-input path exits first. Missing runtime detection is a compile-time error when both variants are requested.

Test signals: `tests/test_check.c` validates CRC results; ARM64 optimized builds and runtime dispatch tests are needed to cover hardware paths.
