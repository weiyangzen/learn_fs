# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_intrinsic_i386_mmx.cc

## Purpose

This file implements a 32-bit x86 MMX specialization using MMX intrinsic functions instead of large inline assembly blocks. It targets the same `GenericCrc<uint64, uint64, uint64, 4>` multiword path and is available for i386/MMX builds with `CRCUTIL_USE_ASM`.

## Important APIs and functions

It specializes `CrcMultiword()` for non-MSVC builds and defines `CrcMultiwordI386Mmx()`. The `CRC_WORD_MMX(this, crc, buf)` macro uses `_mm_xor_si64`, `_mm_cvtsi64_si32`, `_mm_srli_si64`, and table loads to fold one 64-bit word into a CRC lane. `MM64()` and `MM64_TABLE()` cast table memory to `__m64` pointers.

## Control flow, state, and persistence

The function canonicalizes input, aligns the source, and processes data in two phases. For large enough aligned input, it runs a four-lane loop over 32-byte chunks using `crc_word_interleaved_`, then combines the lanes through `CRC_WORD_MMX`. It then processes remaining full 64-bit words one at a time and finishes byte tails with `CRC_BYTE`. `_mm_empty()` is called after MMX phases.

## Dependencies and integration points

It includes `generic_crc.h` and relies on MMX intrinsics being available through compiler headers included indirectly by platform/compiler configuration. It shares the same table layout as the assembly implementations and is conditionally adapted for MSVC warning behavior, although MSVC's primary inline-assembly specialization lives in `multiword_64_64_cl_i386_mmx.cc`.

## Risks and test signals

Intrinsic code is more portable than raw assembly but still relies on MMX state, pointer casts to `__m64`, and compiler support. The macro parameter named `this` is unusual but valid in macro substitution; edits should be cautious. Test signals include output equivalence with generic CRC, large and small input sweeps, i386/MMX compile coverage, and checks that `_mm_empty()` runs before subsequent floating-point code.
