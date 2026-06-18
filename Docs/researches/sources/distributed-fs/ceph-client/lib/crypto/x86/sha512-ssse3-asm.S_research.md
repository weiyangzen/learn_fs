# sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-ssse3-asm.S

## Purpose
Implements the x86-64 SSSE3 SHA-512 compression transform. It is the lower SIMD tier used when SSSE3 is present but AVX/YMM acceleration is unavailable or not selected.

## APIs, Types, and Functions
The exported assembly symbol is `sha512_transform_ssse3`, with C ABI `void sha512_transform_ssse3(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. The file defines symbolic register aliases for `digest`, `msg`, `msglen`, the eight SHA-512 working variables, and temporary registers. It uses a stack message schedule `W_t`, a two-word `WK_2` transfer area, `SHA512_Round`, `SHA512_2Sched_2Round_sse`, and `RotateState`. Ro data includes `XMM_QWORD_BSWAP` and the standard `K512` table.

## Control Flow
After saving GPRs and aligning the stack, the function loops over message blocks. For each block it loads the digest words, byte-swaps the first sixteen 64-bit message words with `pshufb`, stores them in the stack schedule, and interleaves two scalar SHA-512 rounds with vectorized two-word message-schedule expansion. It runs 80 rounds, adds the resulting working variables back into the digest, advances `msg` by 128 bytes, decrements `msglen`, and repeats until all blocks are processed.

## State and Persistence
The caller's digest state is the only durable mutation. Stack storage holds the 80-word schedule and two-word round-transfer buffer. The static constants are mergeable read-only sections. The function does not allocate memory, take locks, or store process-wide state.

## Dependencies and Integration Points
It depends on SSSE3 `pshufb`, SSE2 integer-vector operations, x86-64 ABI preservation rules, and kernel linkage macros. `sha512.h` declares the symbol, protects the call with kernel FPU save/restore, and switches to this transform through `static_call_update()` when `X86_FEATURE_SSSE3` is the best available acceleration tier.

## Risks and Test Signals
Important risks include incorrect endian shuffling, schedule expansion errors, stack-frame alignment mistakes, missed register restores, and use without a valid FPU context. Tests should compare against generic SHA-512 for single and multi-block inputs, exercise CPU feature selection on SSSE3-only systems, run crypto selftests under preemption and interrupt pressure, and use objtool/build coverage to catch unwinder or frame violations.
