# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1.h

## Purpose
x86_64 SHA-1 dispatch header. It exposes `sha1_blocks()` while selecting generic, SSSE3, AVX, AVX2, or SHA-NI compression through static calls.

## APIs, Control Flow, And Integration
`DEFINE_STATIC_CALL(sha1_blocks_x86, sha1_blocks_generic)` starts with the generic target. `DEFINE_X86_SHA1_FN` creates FPU-safe wrappers for SSSE3, AVX, and SHA-NI assembly. `sha1_blocks_avx2()` uses AVX2 only when `nblocks >= 4`, otherwise AVX, to avoid small-message overhead. `sha1_mod_init_arch()` selects SHA-NI first, then AVX2 with BMI1/BMI2, then AVX, then SSSE3. Runtime calls go through `static_call(sha1_blocks_x86)`.

## State, Dependencies, Risks, And Tests
The static-call target persists after init; per-call mutation is limited to the SHA-1 state. Dependencies include kernel FPU APIs, static calls, CPU/xfeature helpers, generic SHA-1, and the assembly files. Risks are feature checks diverging from instruction use, FPU-unusable contexts, and SHA-1's legacy weakness. Tests should verify backend selection, known-answer vectors under each backend, AVX2 threshold behavior, and generic fallback when `irq_fpu_usable()` is false.
