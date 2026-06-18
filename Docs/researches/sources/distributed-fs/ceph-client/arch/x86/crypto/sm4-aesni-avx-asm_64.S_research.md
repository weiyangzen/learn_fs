<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx-asm_64.S

Purpose: This x86-64 assembly file implements AES-NI/AVX accelerated SM4 primitives for up to 8 parallel blocks, CTR encryption, and CBC decryption. It uses AES `aesenclast` plus affine transforms to implement the SM4 S-box efficiently.

Important APIs/types/functions: Public symbols are `sm4_aesni_avx_crypt4`, `sm4_aesni_avx_crypt8`, `sm4_aesni_avx_ctr_enc_blk8`, and `sm4_aesni_avx_cbc_dec_blk8`. Local `__sm4_crypt_blk8` performs the 32 SM4 rounds. Key macros include `transpose_4x4`, `transform_pre`, `transform_post`, `ROUND`, and `inc_le128`. Constant tables provide byte-swap masks, affine transform lookup masks, inverse shift rows, and rotate masks.

Control flow: `sm4_aesni_avx_crypt4` handles 1 to 4 blocks by loading available blocks, byte-swapping, transposing, iterating 32 rounds in groups of four round-key broadcasts, then storing only requested outputs. `sm4_aesni_avx_crypt8` delegates to the 4-block path for small counts, otherwise loads 5 to 8 blocks and calls `__sm4_crypt_blk8`. CTR builds eight counter blocks from the IV, stores the incremented IV, encrypts the counters, and XORs keystream with input. CBC decrypt decrypts eight ciphertext blocks, XORs with IV/previous ciphertext, updates IV with the last ciphertext block, and stores plaintext.

State and persistence: It mutates only destination buffers and the caller-provided IV for CTR/CBC helpers. Round keys are read from the `struct sm4_ctx` arrays passed by C glue. It clears vector state with `vzeroall` before returning from major public paths.

Dependencies and integration points: It includes linkage, CFI type metadata, and frame annotations. It is called by `sm4_aesni_avx_glue.c` under `kernel_fpu_begin()` after AVX, AES-NI, OSXSAVE, and YMM xstate checks.

Risks and test signals: Counter endian handling and carry propagation are critical for CTR. CBC must preserve ciphertext for IV update under in-place operation. S-box affine tables must match SM4 exactly. Tests should include SM4 ECB/CBC/CTR vectors, partial block-count calls from 1 to 8 full blocks, CTR carry near 2^64 low-counter wrap, in-place CBC decrypt, and CPU feature gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx-asm_64.S -->
