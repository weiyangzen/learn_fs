# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ssse3-asm.S

## Purpose
SSSE3 SHA-256 compression function for x86_64. It uses XMM instructions for endian conversion and message schedule expansion while scalar registers perform the SHA-256 round function.

## APIs, Control Flow, And Integration
Exports `sha256_transform_ssse3(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. `COPY_XMM_AND_BSWAP`, `FOUR_ROUNDS_AND_SCHED`, `DO_ROUND`, `rotate_Xs`, and `ROTATE_ARGS` implement input loading, schedule expansion, rounds, and alias rotation. The function saves registers, aligns stack, loads digest words and masks, processes each complete block with three schedule loops plus two final round loops, feeds state forward, and repeats to the end pointer.

## State, Dependencies, Risks, And Tests
Only the eight-word SHA-256 state persists. It depends on SSSE3 support and FPU bracketing in `sha256.h`. Risks are calling without SSSE3/FPU safety, complete-block precondition violations, and macro schedule regressions. Tests should include known-answer vectors, single and multi-block generic comparisons, and dispatch verification on SSSE3-only systems.
