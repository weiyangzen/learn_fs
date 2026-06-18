# sources/distributed-fs/ceph-client/lib/crc/s390/crc32le-vx.c

## Purpose
This file implements reflected/little-endian CRC32 and CRC32C vector algorithms for s390 VX.

## Important APIs, Types, and Functions
It defines `constants_CRC_32_LE`, `constants_CRC_32C_LE`, a shared `crc32_le_vgfm_generic()`, and wrappers `crc32_le_vgfm_16()` and `crc32c_le_vgfm_16()`.

## Control Flow
The generic function loads the selected constants, byte-permutes input vectors to the expected order, seeds the rightmost word with the CRC, folds 64-byte chunks into four accumulators, reduces to 128 then 64 bits, applies final 32-bit folding with R5, and performs Barrett reduction. Wrappers pass the IEEE or Castagnoli constant table.

## State and Persistence
Mutable state is entirely vector-register local. The two constant tables are immutable.

## Dependencies and Integration Points
It depends on the s390 FPU/vector helper layer. It is invoked from the s390 arch CRC32 wrapper after vector-state entry.

## Risks and Test Signals
Risks include byte-permutation errors for reflected CRCs, using the wrong constant table, and size assumptions inherited from the caller. CRC32 LE, CRC32C, alignment, and large-buffer KUnit tests on s390 VX are key.
