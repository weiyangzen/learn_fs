# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/platform.h

## Purpose

`platform.h` centralizes compiler, CPU, SIMD, prefetch, alignment, and utility macro detection for crcutil. It supplies defaults for optional acceleration features and hides compiler-specific spellings from the CRC algorithm headers.

## Important macros and configuration

Defaults include `CRCUTIL_USE_ASM=1`, architecture macros `HAVE_I386` and `HAVE_AMD64`, feature macros `HAVE_MMX`, `HAVE_SSE`, and `HAVE_SSE2`, `CRCUTIL_PREFETCH_WIDTH=0`, `CRCUTIL_MIN_ALIGN_SIZE`, and `CRCUTIL_USE_MM_CRC32`. Utility macros include `PREFETCH(src)`, `TO_STRING`, `SHIFT_RIGHT_SAFE`, `SHIFT_LEFT_SAFE`, `GCC_VERSION_AVAILABLE`, `GCC_ALIGN_ATTRIBUTE`, `GCC_OMIT_FRAME_POINTER`, `SSE2_MOVQ`, and `__forceinline`.

## Control flow, state, and persistence

There is no runtime state. All behavior is compile-time conditional. The header includes SIMD headers when compiler macros indicate support, emits compile-time errors for inconsistent SSE/MMX combinations, and defines safe-shift wrappers to avoid warnings for shifts equal to or wider than the type width.

## Dependencies and integration points

It includes `std_headers.h` first, partly to apply MSVC warning suppression before standard/compiler headers. Nearly every crcutil source depends on this file for architecture gates, alignment attributes, forced inline, prefetch, and shift behavior. Build flags such as `-msse2`, `-mcrc32`, and compiler target architecture directly influence this header's decisions.

## Risks and test signals

Feature detection is compile-time, not runtime, except for separate CPU checks in `Crc32cSSE4`. Compiling with SIMD flags can enable code generation that will fault on older CPUs unless callers dispatch correctly. Some defaults are old-toolchain-oriented and may not match modern cross-compilation expectations. Test signals are matrix builds across x86, non-x86, GCC, Clang-compatible GCC macros, and MSVC, plus runtime tests on CPUs with different SSE/SSE4 capabilities.
