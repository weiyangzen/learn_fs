# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha512_asm.S

## Purpose

This SPARC64 assembly file implements SHA-512 block compression with SPARC crypto/VIS opcodes. It was read as a complete 102-line file.

## Important APIs, Types, and Functions

It exports `sha512_sparc64_transform(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. It uses `VISEntry`, `VISExit`, and the `SHA512` opcode macro.

## Control Flow

The function loads eight 64-bit state words, checks input alignment, and loops over 128-byte blocks. Aligned input is loaded directly; unaligned input is aligned with `alignaddr` and `faligndata`. Each block is compressed by `SHA512`, the pointer advances by 128 bytes, and final state words are stored back.

## State and Persistence Behavior

The caller's SHA-512 block state is updated in place. Floating registers carry state and schedule inputs during the VIS-protected region.

## Dependencies and Integration Points

It depends on SPARC linkage, opcode, and VIS macros. It is declared by `sparc/sha512.h` and used by generic SHA-384/SHA-512 code.

## Risks and Edge Cases

Risks include unaligned block reconstruction, 128-byte stride correctness, VIS state management, and state endian/order compatibility.

## Test Signals

SHA-384/SHA-512 KUnit vectors, unaligned input cases, long inputs, and generic comparison validate behavior.
