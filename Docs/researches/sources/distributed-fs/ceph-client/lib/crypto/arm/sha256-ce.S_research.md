# sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-ce.S

## Purpose
This ARM32 assembly file implements SHA-256 compression using ARMv8 SHA-2 crypto extension instructions.

## Important APIs, Types, And Functions
The exported symbol is `sha256_ce_transform(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. It uses `.Lsha256_rcon` for round constants and vector registers for state/message schedule.

## Control Flow
The routine loads initial state and constants, loops over input blocks, uses SHA-256 extension instructions to run rounds and update the schedule, accumulates results back into chaining variables, and writes state after all blocks.

## State And Persistence
Only the caller's SHA-256 state is updated. Temporary vectors and pointers are transient.

## Dependencies And Integration Points
It requires crypto-extension-capable ARM hardware, Linux linkage, and guarded SIMD entry. `arm/sha256.h` selects it when NEON is available and `HWCAP2_SHA2` is set.

## Risks And Edge Cases
Illegal instruction risk exists if dispatch is wrong. Lane ordering and endian loads must match SHA-256 big-endian block semantics. Finalization and partial block padding are not handled here.

## Test Signals
SHA-256 known-answer tests on CPUs with SHA2 extensions, comparison against scalar and NEON outputs, and fallback tests when `HWCAP2_SHA2` is absent are key signals.
