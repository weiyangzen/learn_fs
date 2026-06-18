# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-ref.h

## Purpose
Portable scalar BlaMka round macros for Argon2 reference block filling.

## Key Content
Defines `fBlaMka()` and the no-message BLAKE2-style `G` and `BLAKE2_ROUND_NOMSG` macros over 64-bit words. The multiply-add variant is from the Lyra PHC team and is the core compression primitive used in Argon2 memory block mixing.

## Dependencies and Coupling
Included by `ref.c`. Uses rotate helpers from `blake2-impl.h`.

## Invariants and Risks
This path is slower than SIMD but portable. Macro arguments are evaluated as mutable lvalues and must be real block word variables.
