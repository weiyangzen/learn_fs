# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx2-x86_64.S

Purpose: AVX2 ChaCha block XOR functions for x86_64, processing 2, 4, or 8 blocks per call.

Important APIs/types/functions: exports `chacha_2block_xor_avx2()`, `chacha_4block_xor_avx2()`, and `chacha_8block_xor_avx2()`. Constant tables provide rotate shuffle masks and counter increments.

Control flow: each function loads/broadcasts the input `struct chacha_state`, adds per-lane block counters, runs `nrounds` as repeated double rounds, adds the original state, XORs keystream with source, and stores up to the requested byte length. The 2-block path operates on duplicated state rows requiring word shuffles after column/diagonal phases. The 4/8-block paths operate on corresponding words across blocks and transpose before output. Partial tails use stack scratch space and `rep movsb` to avoid reading/writing past requested bytes.

State and persistence: no global state; writes caller output only. Uses YMM registers and stack scratch; calls `vzeroupper`.

Dependencies: AVX/AVX2 instructions, x86_64 ABI, caller-side FPU bracketing and CPU feature dispatch in `chacha.h`.

Integration points: selected by `chacha_dosimd()` when AVX2 is enabled and input length benefits from multi-block SIMD.

Risks: counter lane setup and caller-side `state->x[12]` advancement must agree. Tail handling is security-sensitive because out-of-bounds reads can leak or fault. ChaCha allows variable `nrounds`; loops assume even round counts.

Test signals: ChaCha/XChaCha known-answer tests, partial-length encryption tests, and guard-buffer tests are needed to catch tail and counter mistakes.
