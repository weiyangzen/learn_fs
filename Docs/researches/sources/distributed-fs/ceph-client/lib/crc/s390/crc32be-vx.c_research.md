# sources/distributed-fs/ceph-client/lib/crc/s390/crc32be-vx.c

## Purpose
This file implements the big-endian/non-reflected CRC32 vector algorithm for s390 using vector Galois-field multiply instructions.

## Important APIs, Types, and Functions
It defines a static `constants_CRC_32_BE` table and the callable function `u32 crc32_be_vgfm_16(u32 crc, unsigned char const *buf, size_t size)`.

## Control Flow
The function loads constants into vector registers, seeds V0 with the initial CRC in the leftmost word, loads the first 64-byte chunk, then repeatedly folds 64-byte blocks using `fpu_vgfmag()`. It folds V1-V4 into one 128-bit value, consumes remaining 16-byte chunks, reduces 128 bits to 96 then 64 bits, and applies Barrett reduction to return a 32-bit CRC.

## State and Persistence
All state is in vector registers during a caller-managed FPU section. The constant table is immutable static data.

## Dependencies and Integration Points
It depends on `asm/fpu.h` vector helper intrinsics and is called by the wrapper generated in s390 `crc32.h`.

## Risks and Test Signals
Risks include vector register convention mistakes, constants loaded in the wrong order, missing caller alignment/size assumptions, and final-word extraction errors. CRC32 BE KUnit vectors, large-buffer folding tests, and s390 VX build coverage validate it.
