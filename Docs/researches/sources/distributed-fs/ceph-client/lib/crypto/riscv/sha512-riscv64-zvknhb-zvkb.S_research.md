# sources/distributed-fs/ceph-client/lib/crypto/riscv/sha512-riscv64-zvknhb-zvkb.S

## Purpose

This RV64 vector crypto assembly file implements the SHA-512 and SHA-384 compression transform for systems with `Zvknhb`, `Zvkb`, and VLEN at least 128. It was read as a complete 203-line file.

## Important APIs, Types, and Functions

It exports `sha512_transform_zvknhb_zvkb(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. Macros `sha512_4rounds` and `sha512_16rounds` use SHA-2 vector crypto instructions over e64 LMUL=2 vectors. The `K512` rodata table stores 80 64-bit round constants.

## Control Flow

The transform prepares a mask and gather indices, loads state into vector order, and processes each 1024-bit message block. It endian-swaps the four vector chunks, executes five groups of 16 rounds, adds previous state vectors, advances the block pointer, and stores the updated state when all blocks are consumed.

## State and Persistence Behavior

The function mutates only the caller's SHA-512 block state. Constants are immutable. Vector registers are transient and must be protected by the caller's kernel vector state management.

## Dependencies and Integration Points

The assembly is selected by `riscv/sha512.h`, which probes `ZVKNHB`, `ZVKB`, and vector length before dispatching. It integrates with the streaming, finalization, and HMAC code in `sha512.c`.

## Risks and Edge Cases

The code is sensitive to e64 vector grouping, gather/scatter byte offsets, endian reversal, and exact nblocks loop semantics. Incorrect feature gating can fault on unsupported CPUs.

## Test Signals

SHA-384/SHA-512 KUnit vectors, FIPS HMAC-SHA512 self-test when enabled, long multi-block hashes, and generic-versus-accelerated comparison on vector RISC-V validate behavior.
