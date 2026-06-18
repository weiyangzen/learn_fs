# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2.h

## Purpose
Vendored BLAKE2b interface and state definitions used by Argon2.

## Key Content
Defines BLAKE2b constants, packed parameter block, streaming state, compile-time size checks, streaming API declarations, simple one-shot API, and Argon2-specific `blake2b_long()`.

## Dependencies and Coupling
Includes `argon2.h` for visibility macros. Implemented by `blake2b.c` and used by `core.c`, `ref.c`, and `opt.c`.

## Invariants and Risks
The packed parameter block must remain exactly 64 bytes. `blake2b_long()` is required by Argon2 for variable-length block expansion and final output generation.
