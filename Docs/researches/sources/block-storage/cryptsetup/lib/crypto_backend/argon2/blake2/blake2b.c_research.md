# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2b.c

## Purpose
Portable BLAKE2b implementation for bundled Argon2.

## Key Content
Implements parameterized initialization, keyed initialization, update, finalization, one-shot hashing, compression with 12 rounds, state invalidation, counter/final-block management, and Argon2’s `blake2b_long()` variable-output construction.

## Dependencies and Coupling
Uses `blake2.h`, `blake2-impl.h`, and `clear_internal_memory()` from Argon2 core. Argon2 core uses BLAKE2b for initial hashing, first block expansion, and final tag generation.

## Invariants and Risks
State reuse after finalization is rejected. Temporary buffers and state fields are wiped. `blake2b_long()` prefixes output length in little-endian form as required by Argon2.
