# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_128_64_gcc_amd64_sse2.cc

## Purpose

This file implements the GCC amd64 SSE2 specialization of `GenericCrc<uint128_sse2, uint128_sse2, uint64, 4>::CrcMultiword`. It accelerates 128-bit CRCs with 64-bit reads, four-way interleaving, and SSE2 registers for CRC state.

## Important APIs and functions

The specialization provides `CrcMultiword()` and the internal `CrcMultiwordGccAmd64Sse2(const uint8 *src, const uint8 *end, const uint128_sse2 &start)`. `CrcMultiword()` handles very small inputs byte-by-byte, aligns the source on a `uint64` boundary for larger inputs, canonicalizes the start value, and delegates to the assembly routine. `CRC_WORD_ASM()` is a macro that consumes one 64-bit word using the word table and SSE2 shifts/xors.

## Control flow, state, and persistence

No new persistent state is introduced; the implementation consumes `crc_word_`, `crc_word_interleaved_`, and `Base()` from the `GenericCrc` instance. The assembly routine subtracts sentinel lengths from `end`, runs a main loop over four 64-bit buffers and four SSE CRC registers, propagates high-half carryover for 128-bit CRC state, combines the four lanes, then finishes word and byte tails.

## Dependencies and integration points

It includes `generic_crc.h` and `uint128_sse2.h` and is compiled only for `defined(__GNUC__) && CRCUTIL_USE_ASM && HAVE_AMD64 && HAVE_SSE2`. It relies on `SSE2_MOVQ` from `platform.h` to work around Apple/GCC instruction spelling issues.

## Risks and test signals

The inline assembly has many register, pointer, and table-offset assumptions; it is high-risk under compiler upgrades or non-GNU assemblers. It assumes 16-byte-aligned SSE table entries and correct `uint128_sse2` conversions. Test signals are 128-bit CRC known-answer vectors, comparison against the generic non-asm path, small sizes 0..63, unaligned buffers, large buffers, and compilation under GCC versions around the documented workarounds.
