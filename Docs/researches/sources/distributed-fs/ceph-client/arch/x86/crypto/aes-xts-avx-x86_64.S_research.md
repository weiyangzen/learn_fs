# sources/distributed-fs/ceph-client/arch/x86/crypto/aes-xts-avx-x86_64.S

### Purpose
`aes-xts-avx-x86_64.S` implements modern x86_64 AES-XTS encrypt/decrypt helpers for AES-NI+AVX, VAES+AVX2, and VAES+AVX512. It is optimized for disk-sector-sized inputs while still supporting arbitrary crypto API lengths, continuation calls, in-place operation, and ciphertext stealing.

### Important APIs, Types, And Functions
The exported entry points are `aes_xts_encrypt_iv()`, `aes_xts_encrypt_aesni_avx()`, `aes_xts_decrypt_aesni_avx()`, `aes_xts_encrypt_vaes_avx2()`, `aes_xts_decrypt_vaes_avx2()`, `aes_xts_encrypt_vaes_avx512()`, and `aes_xts_decrypt_vaes_avx512()`. They match the `xts_encrypt_iv_func` and `xts_crypt_func` typedefs in `aesni-intel_glue.c`. The key ABI is `struct crypto_aes_ctx`, including AES round keys and key length at offset 480. The central macro `_aes_xts_crypt` is instantiated with `VL=16`, `VL=32`, and `VL=64`. Supporting macros compute XTS tweaks, broadcast round keys, choose encryption or decryption round keys, perform tweaked AES, and handle CTS shuffles/masks.

### Control Flow
`aes_xts_encrypt_iv()` AES-encrypts the sector IV with the tweak key to produce the first tweak. Each XTS crypt function loads key length, chooses encryption or decryption round keys, computes the first four tweak vectors, then processes `4 * VL` bytes per main-loop iteration. For each block/vector, plaintext or ciphertext is XORed with the tweak and round-zero key, AES rounds are executed, the last round folds in the tweak, and output is stored. Tweak generation is interleaved with AES rounds; VL=16 uses repeated multiply-by-x, while VAES vector paths use VPCLMULQDQ to advance multiple tweaks at once. Remainders are processed vector-at-a-time, then block-at-a-time. If the final length is partial, the CTS path swaps the partial bytes with the last full block, taking special care that decryption uses the final two tweaks in reverse order.

### State, Persistence, And Dependencies
The only persistent mutable state is the caller-provided `tweak` buffer, which is overwritten with the next tweak when the processed length is block-aligned so the glue can continue across scatterwalk segments. No key state is changed. Dependencies include AES-NI and AVX for all variants, VAES/VPCLMULQDQ/AVX2 for the 256-bit variant, AVX512BW/AVX512VL/BMI2 for the 512-bit variant, CFI typed symbols, and kernel FPU ownership by callers.

### Integration Points
`aesni-intel_glue.c` registers this file's functions as higher-priority `xts(aes)` drivers through the `DEFINE_AVX_SKCIPHER_ALGS` macro. The glue's `xts_crypt()` first encrypts the IV, then uses a single-scatterlist fast path when possible or a slow path that keeps the final full block together with the partial block for CTS. Baseline AES-NI XTS in `aesni-intel_asm.S` remains available at lower priority.

### Risks
The CTS paths are the highest-risk control flow because encryption and decryption intentionally differ in when the last full block is processed and which tweak applies. The function assumes `len >= 16`, and the glue enforces this. Offset 480 for key length and the encryption/decryption key schedule layout must remain compatible with `crypto_aes_ctx`. AVX512 masking and non-AVX512 shuffle-table CTS paths must preserve in-place correctness by loading partial source bytes before overwriting destination bytes.

### Test Signals
Run XTS known-answer tests for AES-128/192/256 data keys, sector sizes 16, 17..31, 32, 64, 512, and 4096 bytes, in-place and out-of-place buffers, scatterlists split before the final partial block, repeated continuation calls that verify updated tweak state, and backend comparisons among AESNI, AESNI-AVX, VAES-AVX2, and VAES-AVX512.
