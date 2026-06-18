# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-opt.h

## Purpose
SIMD-optimized BlaMka/BLAKE2 round macros for Argon2 block filling.

## Key Content
Provides SSE2/SSSE3, AVX2, and AVX512F implementations of the BlaMka multiply-add round, rotation helpers, diagonalization/undiagonalization, and `BLAKE2_ROUND*` macros. AVX2 and AVX512 paths use vector shuffles/permutations and packed 64-bit arithmetic to process Argon2 block columns/rows efficiently.

## Dependencies and Coupling
Included by `opt.c`. Requires x86 intrinsic headers and compiler feature macros matching the selected build flags.

## Invariants and Risks
This is compile-time CPU-targeted code. Binaries built with unsupported instruction sets will not run on older CPUs unless the build system constrains deployment appropriately.
