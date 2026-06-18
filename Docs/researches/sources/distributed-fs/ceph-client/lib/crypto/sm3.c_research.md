# sources/distributed-fs/ceph-client/lib/crypto/sm3.c

## Purpose

This file implements the generic SM3 hash library with optional architecture block acceleration. It was read as a complete 290-line file.

## Important APIs, Types, and Functions

Exports include `sm3_init`, `sm3_update`, `sm3_final`, and `sm3`. Internal functions include `sm3_block_generic`, `sm3_blocks_generic`, and `__sm3_final`. The file defines SM3 IV constants, precomputed round constants, boolean functions, permutation macros, and message expansion macros.

## Control Flow

The generic block function performs 64 SM3 rounds with a rolling 16-word schedule and XOR feed-forward into the state. Update buffers partial 64-byte blocks and compresses full blocks. Finalization pads with `0x80`, appends a 64-bit big-endian bit count, compresses the final block, emits big-endian digest words, and zeroizes the context.

## State and Persistence Behavior

`struct sm3_ctx` stores block state, byte count, and a partial block buffer. Temporary message schedule words are zeroized by `sm3_blocks_generic`. No file-backed persistence exists.

## Dependencies and Integration Points

It depends on `crypto/sm3.h`, unaligned big-endian helpers, optional `$(SRCARCH)/sm3.h`, and exported GPL symbols. Architecture hooks can override `sm3_blocks` and provide module init.

## Risks and Edge Cases

Risks include padding boundary handling, bytecount overflow, round constant correctness, architecture hook equivalence, and message schedule carry-over errors.

## Test Signals

SM3 KUnit vectors, incremental update split tests, boundary-length messages, and generic-versus-accelerated comparisons validate behavior.
