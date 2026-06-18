# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha256_asm.S

## Purpose

This SPARC64 assembly file implements SHA-256 block compression with SPARC crypto/VIS opcodes. It was read as a complete 78-line file.

## Important APIs, Types, and Functions

It exports `sha256_sparc64_transform(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. It uses `VISEntryHalf`, `VISExitHalf`, and the `SHA256` opcode macro.

## Control Flow

The transform loads eight 32-bit state words into floating registers, chooses aligned or unaligned input flow, processes each 64-byte block with the `SHA256` macro, advances the input pointer, decrements block count, then stores the updated state.

## State and Persistence Behavior

The caller's SHA-256 state is updated in place. Message words and intermediate state live in floating registers during the VIS-protected region.

## Dependencies and Integration Points

It depends on SPARC linkage, opcode, and VIS macros, is declared by `sparc/sha256.h`, and is called from generic SHA-256/SHA-224 streaming and HMAC code.

## Risks and Edge Cases

Risks include unaligned input reconstruction, VIS state preservation, and exact state word ordering.

## Test Signals

SHA-224/SHA-256 KUnit vectors, unaligned inputs, multi-block messages, and fallback comparison validate behavior.
