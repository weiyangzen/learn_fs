# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx2-asm.S

## Purpose
AVX2/BMI2 SHA-256 compression routine. It schedules two blocks at a time in YMM registers and uses BMI2 `rorx` for scalar rotates.

## APIs, Control Flow, And Integration
Exports `sha256_transform_rorx(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. `FOUR_ROUNDS_AND_SCHED` interleaves four rounds with schedule expansion across two blocks; `DO_4ROUNDS` consumes precomputed schedule data. The function aligns stack to 32 bytes, computes the last-block pointer, handles single-block input specially, processes pairs by storing two blocks of `K+W` schedule material, feeds forward after each block, then routes odd final blocks through `.Ldo_last_block`. It ends with `vzeroupper`.

## State, Dependencies, Risks, And Tests
State is updated in place after each block; stack stores schedule, context, and pointers. It depends on `sha256.h` selecting it only with AVX2, BMI2, xstate, and usable FPU. Risks include odd-tail pointer errors, stack layout drift, missing AVX cleanup, and dispatch mismatch. Tests should cover 1, 2, 3, and larger block counts, known-answer vectors, random generic comparisons, and AVX2/BMI2 feature dispatch.
