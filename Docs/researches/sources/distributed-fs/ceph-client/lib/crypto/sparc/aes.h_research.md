# sources/distributed-fs/ceph-client/lib/crypto/sparc/aes.h

## Purpose

This SPARC64 architecture header connects generic AES library hooks to SPARC crypto opcodes and assembly routines. It was read as a complete 149-line file.

## Important APIs, Types, and Functions

It defines `have_aes_opcodes`, exports many `aes_sparc64_*` assembly symbols, declares single-block encrypt/decrypt functions for 128/192/256-bit keys, and implements `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, and `aes_mod_init_arch`.

## Control Flow

Key preparation uses `aes_sparc64_key_expand` when AES opcodes are present, copying unaligned input keys into a temporary aligned buffer when needed. Encryption and decryption dispatch by key length to SPARC assembly and use bounce buffers for unaligned input or output. Without opcodes, all operations fall back to generic AES key expansion and block encrypt/decrypt. Init checks hardware capabilities and ASR26 crypto feature bits.

## State and Persistence Behavior

The static key persists after init. Prepared AES keys store SPARC round keys when accelerated; inverse key storage is unused for SPARC because assembly uses the same round-key array for decryption.

## Dependencies and Integration Points

It depends on SPARC opcode, FPU, PSTATE, ELF hwcap, and generic AES helpers. It integrates with `sparc/aes_asm.S` and shared AES library code.

## Risks and Edge Cases

Risks include FPU/register state assumptions in assembly, alignment bounce-buffer correctness, round-key layout compatibility, and feature detection through hardware capability bits.

## Test Signals

AES known-answer tests, ECB/CBC/CTR mode tests, AES-CMAC KUnit coverage, unaligned buffer tests, and generic fallback comparison validate behavior.
