# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx-asm.S

## Purpose
AVX1 SHA-256 complete-block compression routine. It schedules one block at a time with XMM/AVX instructions and performs round arithmetic in scalar registers.

## APIs, Control Flow, And Integration
Exports `sha256_transform_avx(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. `COPY_XMM_AND_BSWAP` loads and endian-swaps input words. `FOUR_ROUNDS_AND_SCHED` computes four rounds while extending the schedule; `DO_ROUND` consumes later `K+W` words. The function saves registers, aligns stack, computes an end pointer, loads digest words and masks, loops over blocks through scheduled rounds 0..47 and direct rounds 48..63, feeds state forward into memory, and advances by 64 bytes.

## State, Dependencies, Risks, And Tests
The eight-word SHA-256 state is updated in place; input is read-only and temporary schedule transfer lives on the stack. `sha256.h` dispatches here with AVX/xstate/FPU availability when higher-priority backends are absent. Risks are feature mismatch, schedule/register alias bugs, and complete-block precondition violations. Tests should include known-answer vectors, multi-block generic comparisons, and dispatch checks on AVX-only systems.
