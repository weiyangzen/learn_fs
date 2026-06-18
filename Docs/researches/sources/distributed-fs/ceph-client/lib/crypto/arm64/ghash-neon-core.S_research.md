# sources/distributed-fs/ceph-client/lib/crypto/arm64/ghash-neon-core.S

## Purpose
This ARM64 assembly file implements GHASH update using ASIMD polynomial multiply operations. It provides the p8 GHASH primitive used by both GHASH and some POLYVAL fallback paths.

## Important APIs, Types, And Functions
The exported symbol is `pmull_ghash_update_p8`. Macros include `__pmull_p8`, `__pmull2_p8`, `__pmull_pre_p8`, `__pmull_reduce_p8`, and specialized SHASH/SHASH2 helper forms. It prepares permutation vectors and shifted hash-key variants for efficient multiplication.

## Control Flow
The function loads the hash key and accumulator, precomputes low/high/cross multiplication helpers, then loops over input blocks. Each iteration reverses input bytes for GHASH format, xors the block into the accumulator, computes low/high/cross products using PMULL-style p8 operations, reduces the product modulo the GHASH polynomial, and stores the final accumulator after all blocks.

## State And Persistence
Only the caller's accumulator memory is updated. All other data is in vector registers or read-only constants synthesized at runtime.

## Dependencies And Integration Points
It depends on ARM64 assembler helpers and ASIMD/PMULL instruction availability as gated by `arm64/gf128hash.h`. It shares accumulator/key layout with common `struct polyval_elem`.

## Risks And Edge Cases
Byte order and polynomial reduction must match GHASH exactly. The macro-generated product uses many temporary vector registers; aliasing mistakes are hard to spot. Dispatch must avoid unsupported PMULL/p8 instructions.

## Test Signals
AES-GCM vectors, random GHASH comparison with generic C, endian/layout tests, and feature-gated arm64 runs with PMULL are relevant.
