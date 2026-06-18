# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/generic_crc.h

## Purpose

`generic_crc.h` defines `GenericCrc`, a table-driven template for arbitrary CRC polynomials and widths. It supports byte-at-a-time, word-at-a-time, block-striped, and interleaved multiword CRC algorithms, and it declares architecture-specific specializations used for faster 64-bit and 128-bit paths.

## Important APIs, types, and macros

`GenericCrc<_Crc, _TableEntry, _Word, kStride>` exports `Crc`, `TableEntry`, and `Word`. Public construction and `Init(generating_polynomial, degree, canonical)` initialize `GfUtil` and the byte/word lookup tables. `CrcDefault()` selects `CrcMultiword()` on i386/amd64 and `CrcByteUnrolled()` elsewhere. `Base()` exposes the underlying `GfUtil<Crc>`.

Important protected algorithms are `CrcByte()`, `CrcByteUnrolled()`, `CrcByteWord()`, `CrcWord()`, `CrcBlockword()`, and `CrcMultiword()`. Macros `CRC_BYTE`, `CRC_WORD`, `ALIGN_ON_WORD_BOUNDARY`, and table-entry helpers implement tight loops with type-generic downcasts.

## Control flow, state, and persistence

Instance state consists of `crc_word_interleaved_`, `crc_word_`, and `base_`, aligned to 16 bytes. Initialization precomputes tables by multiplying byte values by powers of x in GF(2), using a power-of-two fill optimization. Runtime computation canonicalizes the start value, optionally aligns input, chooses a loop shape based on byte count and `kStride`, processes full words or stripes, then handles byte tails before de-canonicalizing the result.

## Dependencies and integration points

It depends on `base_types.h`, `crc_casts.h`, `gf_util.h`, `platform.h`, and `uint128_sse2.h`. `rolling_crc.h` is a friend consumer of `crc_word_`. Specialized implementations are declared for GCC amd64, GCC amd64 SSE2, GCC i386 MMX, and selected MSVC i386 MMX paths.

## Risks and test signals

The code relies on reinterpret-casting byte pointers to `Word *` after alignment logic, so strict-aliasing and alignment assumptions matter. `kStride` outside 2..8 falls back, but tuned paths expect 4 in specializations. The template is dense with macros and compile-time conditionals, making small edits high risk. Test signals include known CRC vectors for multiple widths/polynomials, randomized split/concatenate comparisons through `GfUtil`, unaligned buffer tests, small-tail sizes, and build coverage with `CRCUTIL_USE_ASM` on and off.
