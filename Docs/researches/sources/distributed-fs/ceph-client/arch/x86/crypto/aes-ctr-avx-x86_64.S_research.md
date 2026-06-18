# sources/distributed-fs/ceph-client/arch/x86/crypto/aes-ctr-avx-x86_64.S

## Purpose
x86_64 assembly implementations of AES-CTR and AES-XCTR for AES-NI+AVX, VAES+AVX2, and VAES+AVX512BW/VL+BMI2 CPUs. It supplies high-throughput length-preserving stream encryption/decryption for AES glue.

## Important APIs, Types, And Functions
Exports `aes_ctr64_crypt_aesni_avx()`, `aes_xctr_crypt_aesni_avx()`, `aes_ctr64_crypt_vaes_avx2()`, `aes_xctr_crypt_vaes_avx2()`, `aes_ctr64_crypt_vaes_avx512()`, and `aes_xctr_crypt_vaes_avx512()`. The `_aes_ctr_crypt` macro generates all functions for vector lengths 16, 32, and 64 bytes. Helper macros abstract vector moves, XORs, broadcast, partial-block load/store, counter preparation, AES rounds, and tail XOR.

## Control Flow And State
The functions load AES key length and round keys from `struct crypto_aes_ctx`, broadcast the initial counter or XCTR IV, generate counter vectors, AES-encrypt them, XOR keystream with source, and store destination. Main loops process eight vectors at a time. Tail paths generate enough keystream for the remaining bytes, handle full vectors first, then use masked AVX512 stores or scalar overlapping partial loads/stores for sub-vector tails. CTR uses big-endian block counters but leaves carry handling and counter writeback to the caller; XCTR uses little-endian counter semantics starting from the provided scalar counter.

## Dependencies And Integration
Built into the AES-NI module on 64-bit. Requires callers to select functions based on CPU features, manage kernel FPU/SIMD state, split CTR at low-64-bit carry boundaries, and update multi-part counters externally.

## Risks And Test Signals
Risks include counter endian mistakes, missing carry splitting in callers, incorrect AES round-key pointer math for AES-128/192/256, AVX/SSE transition issues, partial-block overwrite, and CFI prototype mismatch. Signals include AES CTR/XCTR known-answer tests, non-multiple lengths 1-15 and around vector boundaries, in-place operation, AES key sizes, AVX2/AVX512 CPU feature dispatch, and SIMD state validation.
