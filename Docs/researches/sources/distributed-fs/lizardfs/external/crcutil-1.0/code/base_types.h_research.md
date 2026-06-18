# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/base_types.h

## Purpose

`base_types.h` defines crcutil's fixed-width integer aliases and a compile-time helper used to align those aliases with `size_t` and `ptrdiff_t` when their sizes match. This lets template specializations written for `size_t` also serve `uint32` or `uint64` configurations on the matching platform width.

## Important APIs and types

`ChooseFirstIfSame<A, B>::Type` selects `A` when `sizeof(A) == sizeof(B)`, otherwise `B`. It contains a nested `ChooseFirstIfTrue` template with a boolean specialization. The file defines `uint8`, `int8`, `uint16`, `int16`, `uint32`, `int32`, `uint64`, and `int64` in namespace `crcutil`. On MSVC, 64-bit types use `unsigned __int64` and `__int64`; on GCC they use `unsigned long long` and `long long`. `HAVE_UINT64` is defined to 1 for MSVC and GCC and 0 for unknown compilers, where `uint64` falls back to `uint32`.

## Control flow, state, and persistence

There is no runtime state. The only state is compile-time type selection and macro definition. Downstream templates depend on the selected aliases to determine table entry size, word size, CRC width, and specialization availability.

## Dependencies and integration points

The file includes `std_headers.h` for `size_t` and `ptrdiff_t`. It feeds nearly every other crcutil header, including `crc_casts.h`, `generic_crc.h`, `gf_util.h`, `platform.h`, `crc32c_sse4_intrin.h`, and `uint128_sse2.h`.

## Risks and test signals

The fallback non-GCC/non-MSVC path aliases 64-bit types to 32-bit types while leaving TODOs about correctness, so unsupported compilers can silently lose 64-bit CRC behavior. The selection trick also assumes that matching sizes imply desirable alias reuse, which is performance-driven but can be surprising for ABI inspection. Test signals include compiling the library on 32-bit and 64-bit targets and running CRC unit vectors that exercise 32-bit, 64-bit, and 128-bit template instantiations.
