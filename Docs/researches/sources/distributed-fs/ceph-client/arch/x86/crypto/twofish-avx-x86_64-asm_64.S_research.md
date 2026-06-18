<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-avx-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-avx-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements 8-way AVX Twofish ECB encryption, ECB decryption, and CBC decryption. It bit-packs two groups of four blocks into XMM registers and performs table-based Twofish G-functions in parallel.

Important APIs/types/functions: Public symbols are `twofish_ecb_enc_8way`, `twofish_ecb_dec_8way`, and `twofish_cbc_dec_8way`. Local cores are `__twofish_enc_blk8` and `__twofish_dec_blk8`. Macros include `lookup_32bit`, `G`, `round_head_2`, `encround_tail`, `decround_tail`, `encrypt_cycle`, `decrypt_cycle`, `inpack_blocks`, `outunpack_blocks`, and register preload helpers. Context offsets `s0` through `s3`, `w`, and `k` match `struct twofish_ctx`.

Control flow: Public wrappers load eight blocks, call the local encrypt/decrypt core, and store ECB or CBC output. The encrypt core applies input whitening, transposes blocks, runs eight Twofish round cycles, applies output whitening, and returns encrypted registers in a reordered layout. Decryption starts from output whitening keys, runs inverse cycles, then applies input whitening. CBC decrypt uses `store_cbc_8way` after decrypting to combine with IV/previous ciphertext.

State and persistence: The assembly reads only the caller's expanded Twofish context and writes destination memory. It preserves the callee-saved general registers it uses and has no globals.

Dependencies and integration points: It includes `glue_helper-asm-avx.S` and is called by `twofish_avx_glue.c` under FPU ownership. It also depends on `twofish.h` declarations and the generic Twofish key schedule layout.

Risks and test signals: Table offsets and block transposition must match the generic Twofish representation. CBC output order must align with the helper macro's chain assumptions. Tests should include Twofish known-answer vectors, 8-block ECB/CBC paths, in-place CBC decrypt, mixed 8/3/1 fallback decomposition, and xstate-gated module loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-avx-x86_64-asm_64.S -->
