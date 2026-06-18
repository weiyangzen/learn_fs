# sources/distributed-fs/ceph-client/lib/crypto/sparc/aes_asm.S

## Purpose

This SPARC64 assembly file implements AES key expansion, single-block encryption/decryption, key loading, and ECB/CBC/CTR block loops using SPARC crypto opcodes. It was read as a complete 1543-line file with symbol and body inspection.

## Important APIs, Types, and Functions

Exports include `aes_sparc64_key_expand`, `aes_sparc64_encrypt_128/192/256`, `aes_sparc64_decrypt_128/192/256`, key-load helpers for encryption and decryption keys, ECB encrypt/decrypt functions, CBC encrypt/decrypt functions, and CTR crypt functions for 128/192/256-bit keys. Macro families define repeated AES encrypt and decrypt rounds.

## Control Flow

The file uses macros to unroll AES rounds for each key length. Key expansion generates SPARC round-key material. Single-block functions load data, run key-length-specific opcode rounds, and store output. ECB/CBC/CTR routines load round keys into floating/vector registers, loop over blocks, perform mode-specific XOR/IV/counter handling, and return updated IV or counter data as required by their calling convention.

## State and Persistence Behavior

Persistent state is caller-owned key material, IVs, counters, and buffers. The assembly uses floating-point registers for round keys and data, so callers and wrappers must respect SPARC VIS/FPU state rules. No static mutable state is owned by the file.

## Dependencies and Integration Points

It depends on `<asm/opcodes.h>` macro definitions and SPARC linkage conventions. `sparc/aes.h` declares and exports these symbols and handles feature gating and alignment bounce buffers.

## Risks and Edge Cases

Risks include mode loop block-count semantics, IV and counter update correctness, register state preservation, alignment expectations, and key schedule layout drift with the C union fields.

## Test Signals

AES ECB/CBC/CTR known-answer tests, AES-CMAC and CBC-MAC tests, unaligned buffer tests through the C wrapper, and generic-versus-SPARC differential tests validate behavior.
