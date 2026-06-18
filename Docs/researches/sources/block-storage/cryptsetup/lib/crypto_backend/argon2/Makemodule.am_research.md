# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/Makemodule.am

## Purpose
Autotools build module for cryptsetup’s bundled Argon2 static library.

## Key Content
Defines `libargon2.la` with C89, pthread, and `-O3` flags. Includes BLAKE2b, Argon2 API/core/encoding/thread sources and headers. Selects either optimized SIMD Argon2 (`blamka-round-opt.h`, `opt.c`) or portable reference Argon2 (`blamka-round-ref.h`, `ref.c`) based on `CRYPTO_INTERNAL_SSE_ARGON2`.

## Dependencies and Coupling
Used only when cryptsetup builds internal Argon2. Include paths point to `argon2` and `argon2/blake2`.

## Invariants and Risks
Autotools and Meson Argon2 source lists must remain aligned. SIMD selection is compile-time, not runtime.
