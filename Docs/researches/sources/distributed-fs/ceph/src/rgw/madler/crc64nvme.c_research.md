# sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.c

## Purpose
This C file implements CRC-64/NVME with generated tables and the same update/combine structure as the 32-bit madler CRC files. It uses reflected polynomial `0x9a6c9329ac4bc9b5`.

## Important APIs, types, and functions
- `crc64nvme_bit()` is the bitwise reference update.
- `crc64nvme_rem()` handles a partial final byte.
- `crc64nvme_byte()` is table-driven per byte.
- `crc64nvme_word()` is slicing-by-8 over 64-bit words.
- `crc64nvme_comb()` combines CRCs for message concatenation using `multmodp()` and `x8nmodp()`.

## Control flow
The bit/rem paths complement the CRC, consume reflected bits by shifting right, and xor the NVME polynomial on set low bits. The byte path indexes the first table row. The word path processes leading bytes until 8-byte alignment, folds aligned 64-bit words through table rows 7..0, and then handles the tail. The combine path computes the x-power multiplier for `len2` bytes and xors with `crc2`.

## State and persistence behavior
The file uses static constant tables only. All CRC values are caller-owned values; there is no allocation, mutation of global state, or persistence.

## Dependencies and integration points
It includes `crc64nvme.h` for fixed-width integer declarations. It integrates with code paths that need NVMe-style 64-bit data integrity checks, including object/checksum handling in RGW where this variant is configured.

## Risks and edge cases
- `_word` assumes little-endian integer layout.
- The partial-bit mask uses `1U << bits`; callers must keep `bits` in range despite the 64-bit CRC width.
- Standard CRC-64 variants are often confused; the NVME polynomial must be tested independently from ECMA or ISO variants.
- Very large `len2` combine cases depend on `uintmax_t` width and table exponent cycling.

## Test signals
Use CRC-64/NVME golden vectors, compare bit/byte/word routines for varied alignment and lengths, verify `crc64nvme_comb()` against concatenated buffers, test zero-length and NULL behavior, and include large `len2` combination tests.
