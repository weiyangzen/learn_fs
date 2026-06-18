# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-avx2-asm.S

## Purpose
AVX2/BMI optimized SHA-1 compression routine for complete blocks. It uses YMM registers to precompute two blocks of SHA-1 message schedule while scalar/BMI instructions run the 80 rounds.

## APIs, Control Flow, And Integration
Exports `sha1_transform_avx2(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. `SHA1_VECTOR_ASM` emits the prologue, callee-saved saves, stack alignment, `vzeroupper`, and epilogue. `SHA1_PIPELINED_MAIN_BODY` maintains double-buffered schedule storage, processes one or two blocks per loop, updates the five state words after each block, and swaps precalc/work buffers. `PRECALC_*`, `RR`, and `ROUND_F*` implement message expansion and two-round issue using `rorx` and `andn`.

## State, Dependencies, Risks, And Tests
The five-word SHA-1 state is updated in place; temporary schedule data is stack-local. `sha1.h` dispatches here only with AVX2, BMI1, BMI2, xstate, and usable FPU. Risks are dispatch mismatch, stack-alignment mistakes, odd block-count behavior, and SHA-1's algorithmic collision weakness. Tests should include known-answer vectors, random odd/even block counts, threshold behavior around four blocks, and generic comparisons.
