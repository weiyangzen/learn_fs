# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4_intrin.h

## Purpose

`crc32c_sse4_intrin.h` provides the `_mm_crc32_u8`, `_mm_crc32_u32`, and `_mm_crc32_u64` interfaces used by `crc32c_sse4.h`. It smooths over compiler differences by including native intrinsics when available, defining GCC builtin wrappers for GCC 4.5 or newer, or providing inline assembly for older GCC.

## Important APIs and functions

When MSVC or `__SSE4_2__` is available, the header includes `<nmmintrin.h>`. For GCC 4.5+ without `CRCUTIL_FORCE_ASM_CRC32C`, it defines always-inline wrappers around `__builtin_ia32_crc32qi`, `__builtin_ia32_crc32di`, or `__builtin_ia32_crc32si`. For older GCC, it defines namespace `crcutil` inline assembly functions emitting `crc32q`, `crc32l`, and `crc32b`.

## Control flow, state, and persistence

There is no runtime state. All behavior is compile-time selected by `CRCUTIL_USE_MM_CRC32`, `HAVE_I386`, `HAVE_AMD64`, `_MSC_VER`, `__SSE4_2__`, GCC version, and `CRCUTIL_FORCE_ASM_CRC32C`.

## Dependencies and integration points

The file depends on `platform.h` for architecture/compiler macros and `base_types.h` for crcutil integer aliases. It is consumed by `crc32c_sse4.h`. Build flags such as `-mcrc32`, `-msse4.2`, or MSVC target settings determine whether builtin or header-provided intrinsics compile.

## Risks and test signals

The GCC builtin path explicitly warns that compiling without `-msse4` or `-mcrc32` while enabling `CRCUTIL_USE_MM_CRC32` can fail because GCC hides the builtins. The inline assembly path is x86-only and compiler-constraint-sensitive. This header does not perform runtime CPU detection; it only makes instructions available. Test signals are compilation under MSVC, GCC old/new, i386, and amd64 configurations, plus execution guarded by `Crc32cSSE4::IsSSE42Available()`.
