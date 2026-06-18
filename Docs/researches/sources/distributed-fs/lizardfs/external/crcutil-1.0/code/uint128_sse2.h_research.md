# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/uint128_sse2.h

## Purpose

`uint128_sse2.h` defines `uint128_sse2`, a limited 128-bit unsigned value type implemented with SSE2 intrinsics. It supplies exactly the operations crcutil needs for 128-bit CRC arithmetic and table lookups.

## Important APIs and types

When `HAVE_SSE2` is true, the file specializes `Downcast<__m128i, uint64>`, defines class `uint128_sse2`, and specializes `Downcast<uint128_sse2, uint64/uint32/uint16/uint8>`, `CrcFromUint64<uint128_sse2>()`, and `Uint64FromCrc<uint128_sse2>()`. The class supports construction and assignment from `uint64` and `__m128i`, conversion to `__m128i`, `to_uint64()`, equality/inequality, a less-than comparison, bitwise `^`, `&`, `|`, compound bitwise operators, addition/subtraction by `uint64`, and logical shifts.

## Control flow, state, and persistence

The object stores one `__m128i x_` and has no heap state. Fast shift paths use byte-lane SSE shifts for 8, 16, 32, and 64 bits; other shifts fall back to bit-by-bit loops over union views. Downcast workarounds use inline assembly or memory stores for compiler versions known to generate bad or slow code.

## Dependencies and integration points

It includes `base_types.h`, `crc_casts.h`, and `platform.h`. It is used by `generic_crc.h` and `multiword_128_64_gcc_amd64_sse2.cc` to support 128-bit CRCs. Alignment is enforced with `GCC_ALIGN_ATTRIBUTE(16)`.

## Risks and test signals

The class is not a complete arbitrary-precision integer; it only implements operations needed by crcutil. The less-than implementation compares low 64 bits before high 64 bits, which is unusual for numeric ordering but appears only to support algorithmic heuristics. Union aliasing and aligned SSE stores can be compiler-sensitive. Test signals include conversion round trips, shift/add/subtract edge cases around 64-bit carries, bitwise operations, 128-bit CRC known vectors, and builds with and without SSE2.
