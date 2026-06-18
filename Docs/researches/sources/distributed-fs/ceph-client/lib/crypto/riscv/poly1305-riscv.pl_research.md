# sources/distributed-fs/ceph-client/lib/crypto/riscv/poly1305-riscv.pl

## Purpose

This Perl generator emits RISC-V assembly for the Poly1305 one-time authenticator. It is derived from OpenSSL/Cryptogams and generates optimized `poly1305_init`, `poly1305_blocks`, and `poly1305_emit` entry points for kernel use. The source was read as a complete 847-line generator.

## Important APIs, Types, and Functions

Generated symbols are `poly1305_init`, `poly1305_blocks`, and `poly1305_emit`. The generator maps ABI registers, selects 64-bit or 32-bit code by its flavour argument, handles CHERI capability substitutions, and emits conditional code for fast versus manually assembled misaligned accesses. The generated state layout stores accumulator limbs, clamped `r`, and precomputed scaled `r` values in the caller-provided Poly1305 block state.

## Control Flow

The script builds assembly text in `$code`, chooses a 64-bit or 32-bit body, then post-processes lines for CHERI or normal RISC-V mnemonics before writing the output file. Runtime flow in the emitted code is split into initialization with optional key clamping, block processing over complete 16-byte blocks, and final emission that reduces the accumulator, conditionally subtracts the Poly1305 modulus, adds the nonce, and stores the 16-byte tag.

## State and Persistence Behavior

No persistent storage is owned by the generator. Emitted code mutates the caller's Poly1305 state in memory and uses stack saves for callee-saved registers during block processing. Secret intermediate key and accumulator values live in registers or the supplied state; final security depends on callers zeroizing state where appropriate.

## Dependencies and Integration Points

The generated assembly is declared by `riscv/poly1305.h` and integrated by the generic Poly1305 library when RISC-V architecture support is selected. It depends on RISC-V integer multiply instructions, Linux build-time assembly preprocessing, and optional CHERI and `__riscv_misaligned_fast` feature macros.

## Risks and Edge Cases

Risks concentrate around ABI drift between generated symbols and C prototypes, misaligned input handling, CHERI post-processing substitutions, endian assumptions, and arithmetic carry/reduction correctness. The block routine intentionally truncates `len` to complete 16-byte blocks, so callers must handle partial buffering correctly outside this code.

## Test Signals

Useful tests are Poly1305 KUnit test vectors, ChaCha20-Poly1305 AEAD vectors, unaligned-key and unaligned-message cases, 32-bit and 64-bit RISC-V build coverage, CHERI build coverage where supported, and comparison against the generic C Poly1305 implementation.
