# sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx2.S

### Purpose
`aes-gcm-vaes-avx2.S` is the x86_64 VAES/VPCLMULQDQ/AVX2 backend for AES-GCM. It supplies the high-priority `gcm(aes)` and `rfc4106(gcm(aes))` data-plane helpers used by `aesni-intel_glue.c` when the CPU has VAES, VPCLMULQDQ, AVX2, PCLMULQDQ, and usable SSE/YMM xstate. The implementation targets CPUs with VAES but without preferred AVX512 use, using 256-bit vectors that carry two AES/GHASH blocks per vector.

### Important APIs, Types, And Functions
The exported assembly entry points are `aes_gcm_precompute_vaes_avx2()`, `aes_gcm_aad_update_vaes_avx2()`, `aes_gcm_enc_update_vaes_avx2()`, `aes_gcm_dec_update_vaes_avx2()`, `aes_gcm_enc_final_vaes_avx2()`, and `aes_gcm_dec_final_vaes_avx2()`. Their ABI is the one declared in `aesni-intel_glue.c` for `struct aes_gcm_key_vaes_avx2`. The code assumes `base.aes_key.len` at offset 0, AES round keys at 16, `h_powers` at 288, and `h_powers_xored` immediately after eight 128-bit powers. Core macros include `_ghash_mul_step`, `_ghash_mul`, `_ghash_mul_noreduce`, `_ghash_reduce`, `_ghash_square`, `_ghash_4x`, `_load_partial_block`, `_store_partial_block`, `_aes_gcm_update`, and `_aes_gcm_final`.

### Control Flow
Precomputation encrypts an all-zero block with the expanded AES key to derive H, byte-reflects it, multiplies by the required x factor, then builds `H^8` through `H^1` plus cached XORs of each 64-bit half for Karatsuba GHASH. AAD update handles zero and <=16-byte AAD quickly, uses a 128-byte four-vector GHASH loop for large input, falls back to 32-byte vectors, then handles 17..31 and 1..16 byte tails with shuffle masks and careful partial loads. Encryption/decryption update loads the GHASH accumulator and little-endian counter, generates CTR keystream blocks, XORs source to destination, and GHASHes ciphertext. The 128-byte loop interleaves VAES rounds with GHASH steps; encryption hashes the produced ciphertext, while decryption hashes source ciphertext. Tail handling covers <128 bytes with unreduced product accumulation and one final reduction, including bounded 1..16-byte load/store paths. Finalization GHASHes the length block, encrypts counter block one, stores the tag for encryption, or compares a truncated tag in constant time for decryption.

### State, Persistence, And Dependencies
Persistent per-key state is only the expanded AES key and GHASH precompute arrays in `struct aes_gcm_key_vaes_avx2`; per-request state is `ghash_acc`, the caller-owned little-endian counter, and scatterwalk buffers in the C glue. The assembly does not update `le_ctr` in memory; the glue updates it between data segments. It depends on VAES, VPCLMULQDQ, AVX2, YMM xstate, Linux `SYM_FUNC_*` linkage, and `kernel_fpu_begin()`/`kernel_fpu_end()` already being in effect. `vzeroupper` is issued after YMM use.

### Integration Points
`aesni-intel_glue.c` selects this backend through `FLAG_VAES_AVX2`, registers drivers such as `generic-gcm-vaes-avx2` and `rfc4106-gcm-vaes-avx2`, and aligns AEAD contexts to 32 bytes for this key layout. The glue buffers non-final AAD/data segments to multiples of 16 bytes because the assembly only accepts non-final full-block updates.

### Risks
The most fragile contracts are structure offsets, key-power ordering, tag-length masking, and partial-block bounds. A wrong `le_ctr` update in the caller would repeat keystream blocks because the assembly intentionally does not persist the incremented counter. The code only increments the low 32-bit GCM counter word, matching the standard but making overflow behavior a protocol-level concern. Any missing CPU/xstate gate would expose illegal instructions in kernel FPU sections.

### Test Signals
Useful tests include AES-GCM and RFC4106 known-answer vectors for 128/192/256-bit keys, AAD lengths 0..32 and >128, plaintext lengths 0..129 with every 1..16-byte tail, in-place and out-of-place requests, scatterlists that split AAD/data at non-block boundaries, truncated tags, bad tags returning `-EBADMSG`, and CPU feature selection between AESNI, AVX, VAES AVX2, and AVX512 implementations.
