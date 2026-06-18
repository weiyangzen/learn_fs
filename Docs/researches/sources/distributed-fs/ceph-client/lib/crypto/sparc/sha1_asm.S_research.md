# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1_asm.S

## Purpose

This SPARC64 assembly file implements SHA-1 block compression with SPARC crypto/VIS opcodes. It was read as a complete 72-line file.

## Important APIs, Types, and Functions

It exports `sha1_sparc64_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. It uses `VISEntryHalf`, `VISExitHalf`, and the `SHA1` opcode macro.

## Control Flow

The function loads the five SHA-1 state words into floating registers, checks data alignment, and loops over 64-byte blocks. Aligned input is loaded directly with doubleword loads. Unaligned input uses `alignaddr` and `faligndata` to assemble block words before invoking `SHA1`. After all blocks, it stores the updated state and returns.

## State and Persistence Behavior

The assembly mutates only the caller's SHA-1 state. Floating registers carry transient state and message data within VIS entry/exit protection.

## Dependencies and Integration Points

It depends on SPARC linkage, opcode, and VIS assembly macros. It is declared by `sparc/sha1.h` and called from generic SHA-1 streaming code.

## Risks and Edge Cases

Risks include unaligned load reconstruction, block count loop correctness, VIS state preservation, and state word layout compatibility.

## Test Signals

SHA-1 KUnit vectors, unaligned input tests, multi-block inputs, and generic-versus-SPARC comparison validate behavior.
