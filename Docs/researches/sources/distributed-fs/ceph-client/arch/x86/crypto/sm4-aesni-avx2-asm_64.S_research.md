<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx2-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx2-asm_64.S

Purpose: This file implements AVX2/AES-NI SM4 16-block CTR and CBC-decrypt primitives. It widens the AVX algorithm to YMM registers while still using AES round hardware to realize the SM4 S-box.

Important APIs/types/functions: Public symbols are `sm4_aesni_avx2_ctr_enc_blk16` and `sm4_aesni_avx2_cbc_dec_blk16`. Local `__sm4_crypt_blk16` encrypts sixteen counter or ciphertext blocks. Macros include `transpose_4x4`, `transform_pre`, `transform_post`, `ROUND`, and `inc_le128`; the code also uses XMM subregister aliases for AES-NI operations on YMM lanes.

Control flow: The core byte-swaps and transposes sixteen blocks, iterates 32 SM4 rounds with round-key broadcasts, then transposes and byte-swaps back. CTR constructs sixteen counter blocks from the IV, handles low 64-bit counter overflow with a slower carry path when needed, stores IV+16, encrypts counters, XORs with source, and stores output. CBC decrypt loads sixteen ciphertext blocks, decrypts them, XORs with IV and previous ciphertext blocks, writes the last ciphertext as the new IV, and stores plaintext.

State and persistence: The only persistent mutation visible to callers is IV advancement/update for CTR/CBC and output buffer writes. Round keys remain caller-owned. The routine uses `vzeroupper`/`vzeroall` around AVX2 work to manage vector state transitions.

Dependencies and integration points: It includes linkage, CFI types, and frame annotations. It is registered by `sm4_aesni_avx2_glue.c`, which shares common ECB/CBC/CTR glue from the AVX module for smaller chunks and scalar tails.

Risks and test signals: The 16-counter construction must preserve big-endian counter semantics and handle carry correctly. CBC lane order across 32-byte YMM vectors is a subtle source of errors. Tests should cover 16-block CTR/CBC vectors, IV wrap boundary, in-place CBC, AVX2 feature gating, and decomposition of long requests into 16-block plus smaller fallback chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx2-asm_64.S -->
