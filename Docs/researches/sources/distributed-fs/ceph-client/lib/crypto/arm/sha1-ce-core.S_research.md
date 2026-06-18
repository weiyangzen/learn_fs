# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-ce-core.S

## Purpose
This ARM32 assembly file implements SHA-1 compression using ARMv8 SHA-1 crypto extension instructions exposed to ARM state.

## Important APIs, Types, And Functions
It exports `sha1_ce_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. It uses vector registers for the state, message schedule, and round constants stored at `.Lsha1_rcon`.

## Control Flow
The routine loads the current SHA-1 state and constants, loops over input blocks, uses SHA-1 extension instructions to perform rounds and schedule updates, accumulates results into the state, advances the input pointer, and stores the final chaining state.

## State And Persistence
Only the caller-provided state is updated. All message schedule and working state are transient registers.

## Dependencies And Integration Points
It requires ARM crypto extension support, NEON/SIMD context, and Linux linkage macros. `arm/sha1.h` chooses it when both NEON and `HWCAP2_SHA1` are enabled.

## Risks And Edge Cases
The fast path must be used only on CPUs with SHA-1 instructions; illegal instruction faults are otherwise possible. Byte ordering and state vector lane layout must match generic SHA-1. Padding remains outside this routine.

## Test Signals
Run SHA-1 vectors on ARMv8-capable ARM32 hardware, compare with NEON and scalar outputs, and verify fallback when `HWCAP2_SHA1` is absent.
