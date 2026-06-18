# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/opt.c

## Purpose
SIMD implementation of Argon2 `fill_segment()`.

## Key Content
Defines vectorized `fill_block()` variants for AVX512F, AVX2, and SSE-class targets, plus address-block generation and the same segment traversal logic as the reference implementation. It maintains a vector `state` initialized from the previous block, selects reference blocks based on data-independent or data-dependent addressing, and writes mixed blocks with overwrite or XOR behavior depending on Argon2 version/pass.

## Dependencies and Coupling
Includes `argon2.h`, `core.h`, BLAKE2 headers, and `blamka-round-opt.h`. Selected only when the build enables internal SSE Argon2.

## Invariants and Risks
Compile flags must match the intrinsic path. The optimized path must remain bit-for-bit compatible with `ref.c`; changes to indexing or XOR rules must be mirrored.
