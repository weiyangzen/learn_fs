# sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx512.S

### Purpose
`aes-gcm-vaes-avx512.S` is the x86_64 VAES/VPCLMULQDQ/AVX512 AES-GCM backend. It is optimized for CPUs with useful ZMM support, processing four AES blocks per 512-bit vector and up to 256 bytes per main loop iteration. It backs the highest-priority `gcm(aes)` and RFC4106 GCM registrations unless the CPU advertises `X86_FEATURE_PREFER_YMM`, in which case the glue drops its priority.

### Important APIs, Types, And Functions
The exported functions are `aes_gcm_precompute_vaes_avx512()`, `aes_gcm_aad_update_vaes_avx512()`, `aes_gcm_enc_update_vaes_avx512()`, `aes_gcm_dec_update_vaes_avx512()`, `aes_gcm_enc_final_vaes_avx512()`, and `aes_gcm_dec_final_vaes_avx512()`. They operate on `struct aes_gcm_key_vaes_avx512`, expecting key length at offset 0, AES round keys at 16, `h_powers` at 320, and three zero padding blocks after the sixteen powers. Important macros are `_ghash_mul_step`, `_ghash_mul_noreduce`, `_ghash_reduce`, `_horizontal_xor`, `_ghash_4x`, `_ctr_begin_4x`, `_aesenclast_and_xor_4x`, `_aes_gcm_update`, and `_aes_gcm_final`.

### Control Flow
Precompute derives the raw GHASH key by AES-encrypting zero, byte-reflects it, applies the required x adjustment, stores zero padding blocks, and fills `H^16` through `H^1` in 64-byte groups. AAD update has a fast masked-load path for 1..16 bytes, a 256-byte loop that hashes four ZMM vectors at a time, a 64-byte loop, and a final masked tail path that selects the right key powers based on rounded-up block count. Update functions load the current GHASH accumulator and broadcast the GCM counter into ZMM lanes using the `[0,1,2,3]` counter pattern. The main loop interleaves VAES rounds and GHASH over 256-byte chunks; encryption pipelines by hashing the previous ciphertext group while generating the next group. Remaining data under 256 bytes is handled by a compact 64-byte-at-a-time loop using AVX512 masks and zero padding. Final functions fold in the length block, encrypt counter block one, and either store the computed tag or compare a masked tag in constant time.

### State, Persistence, And Dependencies
The durable state is the expanded AES key and sixteen precomputed GHASH powers in the AEAD context. The three padding blocks are part of the assembly contract and allow masked tail loads of key powers. Per-call state lives in vector registers and caller-provided `ghash_acc`. Dependencies include VAES, VPCLMULQDQ, AVX512BW, AVX512VL, BMI2 `bzhi`, AVX512 xstate, and Linux kernel SIMD section discipline. The file uses `vzeroupper` after YMM/ZMM usage.

### Integration Points
The C glue selects this implementation through `FLAG_VAES_AVX512`, aligns contexts to 64 bytes, registers `generic-gcm-vaes-avx512` and `rfc4106-gcm-vaes-avx512`, and verifies CPU/xfeature availability before registration. It shares the same AEAD control path, RFC4106 nonce handling, tag-size validation, and scatterwalk buffering as the AVX2 and AESNI backends.

### Risks
The AVX512 path has a larger CPU-state footprint and can downclock some CPUs, so registration priority is part of correctness from a performance-policy perspective. Mask construction with `bzhi`, padding block zeroization, and offset static assertions in the glue are essential for tails. Any mismatch in `h_powers` order breaks GHASH silently. As with AVX2, the assembly does not persist updated counters, and the low 32-bit GCM counter is the only incremented word.

### Test Signals
Test with the same AES-GCM/RFC4106 vectors as other backends, plus lengths around 16, 64, 256, and non-multiple tails. Compare output byte-for-byte against generic GCM and the AVX2 backend. Exercise bad tags with all accepted auth sizes, in-place scatterlists, split AAD/data segments, AVX512 priority lowering on `PREFER_YMM`, and boot gating when AVX512 xfeatures are unavailable.
