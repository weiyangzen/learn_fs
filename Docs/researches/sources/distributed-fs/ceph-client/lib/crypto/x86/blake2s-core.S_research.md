# sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s-core.S

Purpose: x86_64 SIMD compression functions for BLAKE2s, with SSSE3 and AVX-512 implementations.

Important APIs/types/functions: exports `blake2s_compress_ssse3(struct blake2s_ctx *, const u8 *, size_t, u32)` and `blake2s_compress_avx512(...)`. Both use only `h[8]`, `t[2]`, and `f[2]` from the context. Static tables include IV constants, rotate shuffle masks, and sigma message schedules.

Control flow: each main loop processes one 64-byte block. It loads hash state, increments the 64-bit byte counter by `inc`, builds the BLAKE2s working vector from state/IV/counter/final flags, runs 10 rounds of G mixing with scheduled message words, then XORs the compressed state back into `h`. SSSE3 uses byte shuffles and shift/or rotates; AVX-512 uses vector rotates/permutation and ternary XOR.

State and persistence: mutates only the caller's BLAKE2s context (`h` and `t`); `f` is read. No global state. AVX code calls `vzeroupper` before return.

Dependencies: x86_64 SIMD instruction sets, `linux/linkage.h`, caller-side FPU bracketing, and context layout compatibility with the generic BLAKE2s code.

Integration points: selected by `x86/blake2s.h` via static CPU feature branches.

Risks: context layout comments are a hard ABI. Counter increment and final flag handling must match generic compression. Long SIMD execution must be chunked by callers to avoid excessive preemption-off time.

Test signals: BLAKE2s self-tests and WireGuard/crypto users should catch digest mismatches; performance depends on CPU feature selection.
