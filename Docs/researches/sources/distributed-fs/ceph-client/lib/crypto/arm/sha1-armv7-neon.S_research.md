# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv7-neon.S

## Purpose
This ARMv7 NEON assembly file accelerates SHA-1 block compression using vectorized message schedule precalculation while scalar ARM registers carry the five working variables.

## Important APIs, Types, And Functions
The exported routine is `sha1_transform_neon(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. Macro families `W_PRECALC_*`, `_R`, and `R` generate schedule and round code. Constants `.LK_VEC` hold the four SHA-1 round constants as vectors.

## Control Flow
The function rejects zero blocks, saves registers, aligns a stack work area, loads constants and chaining variables, and precalculates schedule words for the first block. `.Loop` interleaves rounds 0-79 with NEON schedule preparation for the next block, adding final working variables into the state at the end of each block. `.Lend` handles the final block without preloading a successor, and `.Ldo_nothing` returns for empty input.

## State And Persistence
The SHA-1 state buffer is updated in place. Temporary schedule data is on the stack and in NEON registers. No persistent globals are written.

## Dependencies And Integration Points
It depends on ARMv7 NEON and Linux linkage. `arm/sha1.h` invokes it from inside `scoped_ksimd()` when NEON is available and SHA-1 crypto extensions are not preferred.

## Risks And Edge Cases
The interleaving between current rounds and next-block schedule is subtle; off-by-one mistakes affect only multi-block streams. Stack alignment and VFP/NEON register preservation must match kernel ABI. It assumes full block input and correct caller-side finalization.

## Test Signals
SHA-1 selftests over one-block and multi-block messages, randomized comparison with scalar `sha1_block_data_order`, NEON register preservation tests, and preemption/SIMD context stress are appropriate signals.
