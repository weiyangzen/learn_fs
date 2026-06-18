# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv4-large.S

## Purpose
This file implements a scalar ARM SHA-1 block compression routine for ARMv4-compatible systems. It is the non-NEON fallback for ARM32 SHA-1 acceleration.

## Important APIs, Types, And Functions
The exported symbol is `sha1_block_data_order(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. Important labels include `.Lloop`, `.L_00_15`, `.L_20_39_or_60_79`, `.L_40_59`, `.L_done`, and constants `.LK_00_19` through `.LK_60_79`.

## Control Flow
The routine loads five SHA-1 chaining words, loops over 64-byte blocks, expands the message schedule in registers/stack, runs the 80 rounds grouped by SHA-1 boolean function and constant, then adds working variables back into state. It handles endian conversion while loading message words and exits when all blocks are consumed.

## State And Persistence
Only the caller's `sha1_block_state` is updated persistently. Stack/register state is transient. No static writable data is used.

## Dependencies And Integration Points
It uses Linux ARM linkage macros and is declared by `arm/sha1.h`. The header selects it when NEON/crypto extensions are unavailable or SIMD cannot be used.

## Risks And Edge Cases
The routine is performance-sensitive and has high register pressure. Endian loading and exact 80-round sequencing are the main correctness risks. It assumes full 64-byte blocks and leaves padding/finalization to higher-level SHA-1 code.

## Test Signals
SHA-1 known-answer tests, generic-vs-assembly differential tests over many block counts, ARMv4/ARMv5 build compatibility, and tests with `CONFIG_KERNEL_MODE_NEON` disabled exercise this path.
