<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6-avx-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/cast6-avx-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements 8-way AVX CAST6 block transforms for ECB encryption, ECB decryption, and CBC decryption. It performs CAST6 rounds over two groups of four 128-bit blocks using XMM registers, table lookups, byte shuffles, and shared AVX load/store helpers.

Important APIs/types/functions: Public symbols are `cast6_ecb_enc_8way`, `cast6_ecb_dec_8way`, and `cast6_cbc_dec_8way`. Local worker symbols `__cast6_enc_blk8` and `__cast6_dec_blk8` run the vectorized round function on already-loaded registers. Important macros include `F1_2`, `F2_2`, `F3_2`, `Q`, `QBAR`, `get_round_keys`, `preload_rkr`, `transpose_4x4`, `inpack_blocks`, and `outunpack_blocks`. The code uses CAST S-box symbols `cast_s1` through `cast_s4` and key schedule offsets `km` and `kr`.

Control flow: The public ECB entry loads eight source blocks with `load_8way`, calls the encryption or decryption core, and stores eight output blocks. The encryption core byte-swaps and transposes blocks into SIMD lanes, preloads masking/rotation metadata, runs the twelve CAST6 quad-round groups in the encryption order, then transposes and byte-swaps output back. Decryption executes the same structural pipeline with reversed key order and inverse Q/QBAR sequence. CBC decryption preserves the source pointer, decrypts eight blocks, then `store_cbc_8way` XORs plaintext with the previous ciphertext chain and updates the output.

State and persistence: The routine is stateless apart from the caller-owned CAST6 context. It consumes the expanded key schedule at fixed offsets and uses volatile vector and general registers, saving the callee-saved registers it uses (`r15`, `rbx`, and for CBC `r12`). No persistent global state is modified.

Dependencies and integration points: It includes `linux/linkage.h`, `asm/frame.h`, and `glue_helper-asm-avx.S`. It is called by `cast6_avx_glue.c` under `kernel_fpu_begin()` after SSE/YMM xstate has been validated. Correct integration depends on the CAST6 generic key schedule layout and the shared `cast_s*` S-box tables.

Risks and test signals: Table lookup indexing and byte-lane transposition must exactly match the CAST6 big-endian block format. Any mismatch in key schedule offsets, Q/QBAR order, or CBC store order causes silent ciphertext divergence. Tests should use CAST6 known-answer vectors, ECB/CBC decrypt/encrypt round trips for exactly 8 blocks and mixed tails, in-place CBC decrypt, objtool/unwind validation, and CPU feature gating through the glue module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6-avx-x86_64-asm_64.S -->
