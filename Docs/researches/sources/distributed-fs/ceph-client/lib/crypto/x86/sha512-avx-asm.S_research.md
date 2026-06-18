# sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx-asm.S

## Purpose
AVX SHA-512 complete-block compression routine. It schedules two 64-bit message words at a time in XMM/AVX registers while scalar 64-bit GPRs execute the 80 SHA-512 rounds.

## APIs, Control Flow, And Integration
Exports `sha512_transform_avx(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. `SHA512_Round` performs one scalar round using `WK_2`; `SHA512_2Sched_2Round_avx` computes two schedule words and two rounds together. The function saves GPRs, allocates an aligned schedule frame, loads the eight state words for each 128-byte block, byte-swaps initial words, leads scheduling by one pair, runs rounds 0..79, feeds forward into the digest, advances input, and loops over `nblocks`.

## State, Dependencies, Risks, And Tests
The eight-word SHA-512 state is updated in place; `W_t` and `WK_2` are stack-local. It depends on caller-side AVX/xstate/FPU dispatch and generic SHA-512 state layout. Risks include zero/partial block caller bugs, large stack schedule alignment, AVX use without FPU bracketing, and macro alias mistakes. Tests should include SHA-512 known-answer vectors, one-block and multi-block generic comparisons, AVX dispatch checks, and build/objtool validation.
