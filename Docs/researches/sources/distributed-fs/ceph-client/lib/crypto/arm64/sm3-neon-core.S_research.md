# sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-neon-core.S

## Purpose
ARM64 ASIMD/NEON implementation of SM3 compression for CPUs without dedicated SM3 Crypto Extensions.

## Important APIs, Types, And Functions
Exports `sm3_neon_transform(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. Defines register aliases for scalar state, vector schedule registers, stack schedule area, Boolean functions `FF/GG`, round macros `R`, `R1`, `R2`, and extensive load/schedule macros.

## Control Flow
The function saves callee-saved registers, allocates an aligned stack schedule buffer, preloads and byte-swaps the first block, then loops through 64 SM3 rounds while overlapping schedule precomputation with compression. Between blocks it XORs the compressed state into the chaining variables and preloads the next block. On exit it clears vector temporaries and the stack message expansion area, restores registers, and returns.

## State, Persistence, And Dependencies
State is the caller's SM3 block state. Temporary message expansion lives on the stack and is explicitly cleared. It requires ASIMD but not SM3 CE instructions.

## Integration Points
Selected by `sm3.h` when ASIMD is present but SM3 CE is absent, or as a fallback below the CE path inside the SIMD section.

## Risks
The hand-scheduled macro body is large and sensitive to stack alignment, register preservation, and zeroization. Stack clearing is a useful hardening signal; regressions could leave message data in kernel stack memory.

## Test Signals
SM3 vectors across 1 and many blocks, generic-vs-NEON comparisons, register clobber tests, stack sanitizer runs, and feature-gated selection tests are strong signals.
