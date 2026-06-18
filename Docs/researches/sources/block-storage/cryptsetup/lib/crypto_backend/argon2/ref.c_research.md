# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/ref.c

## Purpose
Portable reference implementation of Argon2 `fill_segment()`.

## Key Content
Implements scalar `fill_block()` using copy/xor, BlaMka no-message rounds over columns then rows, address-block generation for data-independent modes, and segment filling for Argon2d/i/id. It handles first-slice startup offsets, reference lane/index calculation, and version-specific overwrite vs XOR behavior.

## Dependencies and Coupling
Includes `argon2.h`, `core.h`, `blamka-round-ref.h`, `blake2-impl.h`, and `blake2.h`. Selected when optimized internal Argon2 is disabled.

## Invariants and Risks
This is the correctness reference for the SIMD path. `fill_segment()` returns silently if the instance pointer is null, matching upstream style rather than reporting an error.
