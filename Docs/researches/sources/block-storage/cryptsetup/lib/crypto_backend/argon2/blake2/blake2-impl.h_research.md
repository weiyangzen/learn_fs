# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2-impl.h

## Purpose
Portable low-level helpers for BLAKE2 and Argon2 encoding of little-endian words and rotates.

## Key Content
Detects native little-endian targets, defines inline `load32`, `load64`, `store32`, `store64`, `load48`, `store48`, `rotr32`, and `rotr64`. Uses memcpy-based loads/stores on little-endian systems to avoid alignment violations and bytewise fallback otherwise.

## Dependencies and Coupling
Included by BLAKE2b and Argon2 block-fill code. Its endian helpers are foundational for stable cross-platform hash output.

## Invariants and Risks
Correctness depends on exact little-endian serialization. Rotate helpers assume valid nonzero rotation constants as used by BLAKE2/BlaMka code.
