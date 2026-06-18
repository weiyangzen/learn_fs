# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha.h

Purpose: x86_64 dispatch layer for ChaCha encryption and HChaCha derivation across generic, SSSE3, AVX2, and AVX-512VL implementations.

Important APIs/types/functions: declares all assembly entry points; defines static keys `chacha_use_simd`, `chacha_use_avx2`, `chacha_use_avx512vl`, helper `chacha_advance()`, dispatcher `chacha_dosimd()`, hooks `hchacha_block_arch()`, `chacha_crypt_arch()`, and `chacha_mod_init_arch()`.

Control flow: init enables SSSE3 baseline, then AVX2 if AVX/AVX2 and YMM xfeatures are available, then AVX512VL if AVX512VL/BW are present. `chacha_crypt_arch()` uses generic for no SIMD or <=1 block, otherwise chunks work to at most 4 KiB per FPU section. `chacha_dosimd()` prefers AVX512VL, then AVX2, then SSSE3, selecting 8/4/2/1-block functions based on remaining byte count and advancing `state->x[12]` by rounded block count.

State and persistence: persistent static keys after init; mutable caller state counter is updated after SIMD calls. No file I/O or persistence.

Dependencies: CPU feature detection, OS xfeature checks, static keys, `kernel_fpu_begin/end`, generic ChaCha/HChaCha functions.

Integration points: architecture hooks for the ChaCha library used by stream cipher and XChaCha consumers.

Risks: counter overflow is not checked here. Incorrect `chacha_advance()` or branch thresholds would desynchronize keystream counters. FPU bracketing and 4 KiB chunking are required for kernel scheduling safety.

Test signals: known-answer vectors across lengths 0..multi-block, state counter advancement tests, and CPU-feature matrix testing.
