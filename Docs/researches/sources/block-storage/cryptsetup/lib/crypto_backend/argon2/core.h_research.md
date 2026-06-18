# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.h

## Purpose
Internal Argon2 core definitions and function declarations.

## Key Content
Defines block sizes, prehash sizes, the 1 KiB `block` structure, `argon2_instance_t`, `argon2_position_t`, thread data structure, and declarations for allocator, wiping, validation, initialization, segment filling, memory filling, indexing, and finalization functions.

## Dependencies and Coupling
Included by all Argon2 implementation units. The `fill_segment()` declaration is implemented by exactly one of `ref.c` or `opt.c`.

## Invariants and Risks
The block layout and constants must match the Argon2 specification. `argon2_instance_t` stores derived lane and segment lengths; callers must initialize them consistently before filling memory.
