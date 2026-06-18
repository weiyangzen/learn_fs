# subset-b-000860 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx2.S -->
## sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx2.S

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx512.S -->
## sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx512.S

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-vaes-avx512.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-xts-avx-x86_64.S -->
## sources/distributed-fs/ceph-client/arch/x86/crypto/aes-xts-avx-x86_64.S

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-xts-avx-x86_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_asm.S -->
## sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_asm.S

### Purpose
`aesni-intel_asm.S` is the baseline Intel AES-NI assembly implementation for AES key expansion and common block modes. It supports 32-bit and 64-bit x86, with x86_64-only CTR support, and supplies the low-level primitives called by `aesni-intel_glue.c` for `ecb(aes)`, `cbc(aes)`, `cts(cbc(aes))`, `ctr(aes)`, and baseline `xts(aes)`.

### Important APIs, Types, And Functions
Exported functions include `aesni_set_key()`, `aesni_enc()`, `aesni_ecb_enc()`, `aesni_ecb_dec()`, `aesni_cbc_enc()`, `aesni_cbc_dec()`, `aesni_cts_cbc_enc()`, `aesni_cts_cbc_dec()`, `aesni_ctr_enc()` on x86_64, `aesni_xts_enc()`, and `aesni_xts_dec()`. Internal helpers include `_key_expansion_128`, `_key_expansion_192a/b`, `_key_expansion_256a/b`, `_aesni_enc1`, `_aesni_enc4`, `_aesni_dec1`, `_aesni_dec4`, `_aesni_inc_init`, `_aesni_inc`, and `_aesni_gf128mul_x_ble`. The key layout stores encryption round keys at the start of `crypto_aes_ctx`, decryption round keys at a 240-byte offset, and key length at offset 480.

### Control Flow
`aesni_set_key()` expands 128/192/256-bit AES keys with `aeskeygenassist`, writes encryption round keys, then builds the inverse decryption key schedule with `aesimc` and endpoint swapping. ECB encrypt/decrypt loops process four blocks at a time when possible and one block for remainders. CBC encryption chains one block at a time through the IV, while CBC decryption parallelizes four-block decrypts and XORs with the previous ciphertext or IV. CTS-CBC helpers use a shuffle table to permute the final partial block. CTR initializes a byte-swap mask and little-endian counter, encrypts counters one or four blocks at a time, XORs with input, increments IV, and stores the updated IV. XTS encrypt/decrypt computes tweaks by multiplying by x in GF(2^128), processes four blocks where possible, and handles ciphertext stealing for partial final blocks.

### State, Persistence, And Dependencies
Persistent state is the expanded key schedule in `crypto_aes_ctx` and caller-provided IV/tweak buffers that are updated by CBC, CTR, and XTS. The assembly relies on the glue to provide valid key lengths, block-aligned lengths except for modes that explicitly handle CTS or CTR tail in C, and active kernel FPU sections. It depends on AES-NI instructions, PCL-style XMM operations, Linux frame/linkage macros, and for x86_64 CTR the ABI register mapping used by the glue.

### Integration Points
This file is the foundation for `aesni_skciphers[]` in `aesni-intel_glue.c`. The glue wraps these routines in `skcipher_walk_virt()`, handles partial CTR tails that are smaller than one AES block, validates XTS keys, aligns contexts, and registers algorithms only when `X86_FEATURE_AES` is present. The baseline XTS functions are lower priority than the newer AVX/VAES XTS functions.

### Risks
Key schedule offsets are shared implicitly with newer assembly files and the C glue. Mode functions assume the caller passes lengths they can legally process; for example ECB/CBC process only complete blocks, while glue returns leftovers to the walk. IV update behavior is part of the API and can break multi-segment requests if changed. CTS and XTS partial-block paths are shuffle-table-heavy and must preserve in-place semantics. The file uses legacy SSE encodings, so callers mixing AVX code must respect upper-register state rules in surrounding paths.

### Test Signals
Use AES ECB/CBC/CTS/CTR/XTS known-answer vectors for all key sizes, multi-block and single-block requests, CBC and CTR IV continuation over scatterwalk segments, CTS lengths 16..31 and larger, XTS partial-sector cases, in-place buffers, and comparison against generic AES software. Key expansion should be checked indirectly through both encryption and decryption vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_glue.c -->
## sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_glue.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx-asm_64.S -->
## sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx-asm_64.S

### Purpose
`aria-aesni-avx-asm_64.S` implements 16-way parallel ARIA block cipher helpers for x86_64 using AVX and AES-NI, with optional GFNI variants. It is not an AES mode implementation; it uses AES instructions and affine transformations to accelerate ARIA S-boxes and provides ECB-style 16-block encrypt/decrypt helpers plus CTR keystream encryption helpers for ARIA glue code elsewhere in the kernel.

### Important APIs, Types, And Functions
Exported functions are `aria_aesni_avx_encrypt_16way()`, `aria_aesni_avx_decrypt_16way()`, `aria_aesni_avx_ctr_crypt_16way()`, `aria_aesni_avx_gfni_encrypt_16way()`, `aria_aesni_avx_gfni_decrypt_16way()`, and `aria_aesni_avx_gfni_ctr_crypt_16way()`. Internal functions are `__aria_aesni_avx_crypt_16way()`, `__aria_aesni_avx_ctr_gen_keystream_16way()`, and `__aria_aesni_avx_gfni_crypt_16way()`. The assembly relies on ARIA context offsets from `asm-offsets.h`, including `ARIA_CTX_rounds`, `ARIA_CTX_enc_key`, and `ARIA_CTX_dec_key`. Major macros handle byte slicing, de-byte-slicing, round-key addition, ARIA FO/FE/FF rounds, S-box implementations using AES-NI or GFNI, diffusion layers, CTR increment, and output writes.

### Control Flow
Encrypt and decrypt wrappers load 16 input blocks into XMM registers, select encryption or decryption round keys, byte-slice the blocks, run the shared 16-way crypt core, de-byte-slice, and write 16 blocks. The shared core performs alternating ARIA FO and FE rounds, checking `ARIA_CTX_rounds` to choose the 12-round, 14-round, or 16-round final sequence for 128/192/256-bit keys. AES-NI S-box macros isolate AES SubBytes via `vaesenclast`/`vaesdeclast` and apply affine tables; GFNI variants replace these table-filtered affine steps with `vgf2p8affine*` instructions. CTR generation loads the big-endian 128-bit IV, byte-swaps to little endian for increments, constructs 16 counter blocks, writes back the IV advanced by 16, encrypts the counters, XORs them with source, and writes output.

### State, Persistence, And Dependencies
Persistent state is the ARIA context supplied by the caller, including round count and expanded round keys. CTR mode mutates the caller-provided IV to the next counter after 16 blocks. Temporary byte-sliced state is held in XMM registers and, during the core, in scratch memory based on the destination pointer. Dependencies include x86_64, AVX VEX-encoded XMM operations, AES-NI for the base path, GFNI for the GFNI path, Linux typed linkage, frame macros, and generated ARIA structure offsets.

### Integration Points
This file is called by ARIA x86 glue code that batches full 16-block chunks and handles mode-level request walking and tail processing. It complements scalar or smaller parallel ARIA implementations by providing high throughput for large ECB/CTR-style workloads. The CTR helper's keystream buffer parameter lets the function build counter blocks, encrypt them through the same 16-way core, and avoid exposing byteslicing details to the caller.

### Risks
The round-count branches must match ARIA key schedule semantics exactly; using the wrong `ARIA_CTX_rounds` value corrupts all output. The byte-slice/de-byte-slice register ordering is subtle and must match `write_output()` ordering. CTR IV update is observable state and must stay consistent across batched calls. GFNI and non-GFNI paths must remain equivalent despite different S-box implementations. The scratch-memory use through the destination pointer assumes the caller provides writable output space for the full 16-block batch.

### Test Signals
Tests should compare AESNI-AVX and GFNI outputs against generic ARIA for 128/192/256-bit keys, both encryption and decryption, 16-block ECB batches, CTR batches with IV continuation across multiple calls, in-place CTR if supported by glue, CPU feature dispatch between GFNI and non-GFNI paths, and randomized multi-block differential tests around round-count boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx-asm_64.S -->
