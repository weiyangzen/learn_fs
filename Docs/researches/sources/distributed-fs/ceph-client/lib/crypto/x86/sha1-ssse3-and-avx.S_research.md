# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ssse3-and-avx.S

## Purpose
Shared macro implementation for SSSE3 and AVX SHA-1 compression functions. It vectorizes message scheduling and uses scalar integer registers for SHA-1 round arithmetic.

## APIs, Control Flow, And Integration
Exports `sha1_transform_ssse3` and `sha1_transform_avx`. `SHA1_VECTOR_ASM` emits each function with stack workspace setup and cleanup. `SHA1_PIPELINED_MAIN_BODY` loads `A..E`, precomputes schedule entries into a circular `WK` buffer, runs 80 rounds with `RR` and `F1..F4`, advances block pointers, uses a dummy pointer to avoid end-of-buffer overread during lookahead, updates state, and loops. `W_PRECALC_SSSE3` and `W_PRECALC_AVX` swap instruction forms while preserving the algorithm.

## State, Dependencies, Risks, And Tests
The five SHA-1 chaining words are updated in place; the schedule workspace is zeroed before return. Dispatch and FPU safety are provided by `sha1.h`. Risks include lookahead pointer mistakes, stack cleanup errors, feature dispatch mismatch, and SHA-1 collision weakness. Tests should cover one-block and two-block edges, SSSE3-only and AVX dispatch, and generic known-answer comparisons.
