# sources/distributed-fs/ceph-client/lib/crypto/riscv/sha256-riscv64-zvknha_or_zvknhb-zvkb.S

## Purpose

This RISC-V vector crypto assembly file implements the SHA-256 compression function for RV64 systems with VLEN at least 128, `Zvknha` or `Zvknhb`, and `Zvkb`. It was read as a complete 225-line assembly file.

## Important APIs, Types, and Functions

It exports `sha256_transform_zvknha_or_zvknhb_zvkb(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. Internal macros `sha256_4rounds` and `sha256_16rounds` drive `vsha2cl.vv`, `vsha2ch.vv`, and `vsha2ms.vv`. The constant table `K256` provides the 64 SHA-256 round constants.

## Control Flow

The function preloads round constants, builds a vector mask for message schedule updates, gathers state words into the vector layout required by the SHA instructions, then loops over blocks. For each block it endian-swaps four vectors of message words, performs 64 rounds in four groups of 16, adds the previous state, and repeats until `nblocks` reaches zero. Final state is scattered back to the C state layout.

## State and Persistence Behavior

The only persistent mutation is the caller-owned SHA-256 block state. Constants live in read-only data. Vector registers hold transient message schedule and state words inside a `kernel_vector_begin()` and `kernel_vector_end()` region supplied by the C wrapper.

## Dependencies and Integration Points

The file is called from `riscv/sha256.h`, which probes vector crypto features and falls back to `sha256_blocks_generic` if unavailable or SIMD use is disallowed. It includes Linux linkage macros and relies on RISC-V vector crypto assembler support.

## Risks and Edge Cases

Risks include vector length assumptions, state gather/scatter index correctness, endian conversion, exact feature gating, and calling the function without saving vector state. It assumes `nblocks` is nonzero when called by the streaming layer.

## Test Signals

SHA-224/SHA-256 KUnit vectors, long multi-block hashes, unaligned input coverage through the generic streaming layer, and comparison against generic C output on vector-capable RISC-V are the primary signals.
