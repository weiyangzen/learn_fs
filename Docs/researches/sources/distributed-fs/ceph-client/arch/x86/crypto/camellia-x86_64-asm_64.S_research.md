# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-x86_64-asm_64.S

Purpose: Provides scalar and 2-way x86_64 assembly Camellia block operations used by the baseline Camellia asm module and by wider AES-NI modules for tails.

Important APIs/functions: exports `__camellia_enc_blk`, `camellia_dec_blk`, `__camellia_enc_blk_2way`, and `camellia_dec_blk_2way`. Macros reference the eight Camellia S-box tables exported from `camellia_glue.c`, define key table offsets, implement F-function rounds, FL/FLINV layers, endian packing, optional XOR output for CBC encryption helpers, and two-block parallel variants.

Control flow: scalar encryption loads one 16-byte block, pre-whitens, runs three or four groups of six rounds depending on key length, applies FL layers, and writes or XORs output. Scalar decryption starts from the selected terminal whitening key, conditionally includes the higher-key round group, then reverses round order. Two-way routines perform the same logic over two blocks interleaved in registers.

State and persistence: all key state is read from `struct camellia_ctx`. Output is written directly or XORed with existing destination when the caller requests the XOR variant. No persistent mutable state is kept by the assembly.

Dependencies and integration points: depends on S-box globals from `camellia_glue.c`, `camellia_ctx` layout from `camellia.h`, and Linux CFI/linkage macros. It is used by `camellia_glue.c`, `camellia_aesni_avx_glue.c`, and `camellia_aesni_avx2_glue.c`.

Risks: because the S-box tables live in C, link visibility and symbol names are part of the ABI. The boolean XOR mode in encryption must remain aligned with `camellia_enc_blk_xor` wrappers. Manual preservation of callee-saved registers and endian rotations are correctness-sensitive.

Test signals: scalar and 2-way paths are exercised by short ECB/CBC requests below vector batch sizes, CBC encryption, CBC decryption tails, all key lengths, and in-place requests.
