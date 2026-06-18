# sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s.h

Purpose: x86_64 BLAKE2s compression dispatch layer selecting generic, SSSE3, or AVX-512 compression.

Important APIs/types/functions: declares `blake2s_compress_ssse3()` and `blake2s_compress_avx512()`, defines `blake2s_compress()` and `blake2s_mod_init_arch()`, and owns static keys `blake2s_use_ssse3` and `blake2s_use_avx512`.

Control flow: `blake2s_compress()` falls back to generic when SSSE3 is unavailable or `may_use_simd()` is false. Otherwise it processes at most one 4 KiB page worth of blocks per FPU section, choosing AVX-512 if its static key is enabled, else SSSE3. Module init enables SSSE3 on `X86_FEATURE_SSSE3`; AVX-512 requires AVX, AVX2, AVX512F, AVX512VL, and OS xfeature support for SSE/YMM/AVX512 state.

State and persistence: persistent state is static branch configuration after init. Per-call state is the BLAKE2s context and input pointer. FPU/SIMD state is bracketed.

Dependencies: CPU feature checks, `may_use_simd()`, `kernel_fpu_begin/end`, page size constants, generic BLAKE2s compressor, and context definitions from the including source.

Integration points: architecture hook for the BLAKE2s library, often used in fast hashing/MAC contexts.

Risks: using SIMD when preemption or FPU use is not allowed would be unsafe. AVX-512 xfeature detection must match actual instruction use. The 4 KiB chunking assumes compression can resume cleanly by advancing context counter and data pointer.

Test signals: BLAKE2s known-answer tests plus CPU-feature-specific boot/runtime testing.
