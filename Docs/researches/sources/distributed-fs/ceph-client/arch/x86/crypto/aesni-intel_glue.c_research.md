# sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_glue.c

### Purpose
`aesni-intel_glue.c` connects x86 AES-NI, AVX, VAES, XTS, CTR/XCTR, and GCM assembly implementations to the Linux kernel crypto API. It owns algorithm registration, key setup, request walking, SIMD/FPU section management, AEAD tag handling, RFC4106 nonce handling, and CPU feature gating.

### Important APIs, Types, And Functions
Important context types are `struct aesni_xts_ctx`, `struct aes_gcm_key`, `struct aes_gcm_key_aesni`, `struct aes_gcm_key_vaes_avx2`, and `struct aes_gcm_key_vaes_avx512`. Key helpers include `aes_align_addr()`, `aes_ctx()`, `aes_xts_ctx()`, `aes_set_key_common()`, `aesni_skcipher_setkey()`, and `xts_setkey_aesni()`. Request paths include `ecb_encrypt/decrypt()`, `cbc_encrypt/decrypt()`, `cts_cbc_encrypt/decrypt()`, `ctr_crypt_aesni()`, generic `xts_crypt()`, `xts_crypt_slowpath()`, `ctr_crypt()`, `xctr_crypt()`, `gcm_setkey()`, `gcm_process_assoc()`, and `gcm_crypt()`. Registration is handled through `aesni_skciphers[]`, `DEFINE_AVX_SKCIPHER_ALGS`, `DEFINE_GCM_ALGS`, `register_avx_algs()`, `aesni_init()`, and `aesni_exit()`.

### Control Flow
Initialization first checks for AES-NI, registers baseline skciphers and AESNI GCM, then conditionally registers AVX, VAES AVX2, and VAES AVX512 algorithms as CPU features and xstate permit. Setkey expands AES keys via assembly when SIMD is usable, otherwise falls back to portable AES expansion. XTS setkey validates the doubled key and fills crypt/tweak contexts. ECB/CBC/CTS/CTR wrappers walk scatterlists and call assembly inside FPU sections. XTS encrypt/decrypt encrypts the IV, uses a fast path for single contiguous scatterlist elements, and falls back to a slow path that keeps CTS-required blocks together. GCM setkey handles RFC4106 salt extraction, asserts assembly offsets, expands AES, and precomputes GHASH powers either in assembly or with portable GF(2^128) math. `gcm_crypt()` initializes the counter, hashes AAD, encrypts/decrypts data, finalizes the tag, writes tags for encryption, and verifies tags for decryption.

### State, Persistence, And Dependencies
Per-transform state lives in aligned crypto contexts: AES round keys, XTS tweak/data keys, RFC4106 nonce, and GCM GHASH precompute tables. Per-request state is transient in `skcipher_walk`, `scatter_walk`, `ghash_acc`, IV buffers, and local counters. Dependencies include Linux crypto internal APIs, scatterwalk, simd helpers, x86 CPU feature checks, xfeature checks, static assertions, GF(2^128) helpers, AES library fallbacks, module registration, and the assembly symbols in the neighboring `.S` files.

### Integration Points
The file registers driver names such as `ecb-aes-aesni`, `cbc-aes-aesni`, `xts-aes-aesni`, `xts-aes-vaes-avx2`, `ctr-aes-vaes-avx512`, `generic-gcm-vaes-avx2`, and `rfc4106-gcm-vaes-avx512`. It is the single policy layer choosing priorities: AESNI baseline at 400/401, AVX at 500, VAES AVX2 at 600, and VAES AVX512 at 800 unless YMM is preferred. It also bridges AEAD API semantics, scatterlist layout, tag placement, and RFC4106 associated-data conventions to low-level assembly contracts.

### Risks
Registration error unwinding is delicate because partially registered arrays must be unregistered exactly once. SIMD usability matters in setkey and request paths; fallback key precompute must produce byte-for-byte-compatible GHASH tables. The GCM assembly offset `static_assert`s are critical because the assembly uses hard-coded offsets. XTS slowpath must keep the last full block and partial block in one assembly call for CTS. CTR overflow handling is split in C for AVX paths because some assembly only handles the low 64-bit counter. Authsize and RFC4106 associated-data validation are security-sensitive.

### Test Signals
Crypto selftests should cover every registered driver and key size, algorithm fallback when SIMD is unavailable during setkey, CPU-feature-gated registration, XTS contiguous fast path and scatterwalk slow path, CTR low-64-bit overflow splitting, XCTR counter progression, GCM/RFC4106 AAD and tag handling, invalid auth sizes, invalid RFC4106 AAD lengths, module load/unload, and comparison of all optimized backends against generic software implementations.
