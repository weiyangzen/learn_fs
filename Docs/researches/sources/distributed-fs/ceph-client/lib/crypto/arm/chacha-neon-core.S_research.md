# sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-neon-core.S

## Purpose
This ARM NEON assembly file implements ChaCha block XOR, four-block XOR, and HChaCha using vectorized NEON operations.

## Important APIs, Types, and Functions
It defines `ENTRY(chacha_block_xor_neon)`, `ENTRY(hchacha_block_neon)`, and `ENTRY(chacha_4block_xor_neon)`. It includes permutation/rotate constants and a `.Lpermute` table for partial-block stores.

## Control Flow
The one-block path loads the ChaCha state, runs 12 or 20 rounds, adds the original state, XORs one 64-byte block, and stores. HChaCha runs the permutation and stores words x0-x3 and x12-x15. The four-block path transposes four states across NEON registers, adds counters 0-3, runs double rounds, re-interleaves output keystream, XORs up to 256 bytes, and uses table-based partial handling for the final incomplete block.

## State and Persistence
All state is register and stack-local; the wrapper updates the caller-owned block counter after calls. No global mutable state is created.

## Dependencies and Integration Points
It depends on ARM NEON, Linux linkage, and is selected by `arm/chacha.h` when NEON is usable. It complements the scalar ARM ChaCha implementation.

## Risks and Test Signals
Risks include partial-block overlap stores, counter lane addition, 12- versus 20-round selection, state transposition bugs, and SIMD context misuse if called outside wrappers. ChaCha/XChaCha known-answer tests, partial lengths 1-255, and in-place XOR tests validate it.
