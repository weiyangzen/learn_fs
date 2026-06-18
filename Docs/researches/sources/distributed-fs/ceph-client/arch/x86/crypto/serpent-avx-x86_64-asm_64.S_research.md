<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements 8-way AVX Serpent block encryption, block decryption, and CBC decryption. It processes two four-block groups in parallel with XMM registers and bit-sliced Serpent S-box macros.

Important APIs/types/functions: Public symbols are `serpent_ecb_enc_8way_avx`, `serpent_ecb_dec_8way_avx`, and `serpent_cbc_dec_8way_avx`; they are typed for CFI and exported by the glue file. Local cores `__serpent_enc_blk8_avx` and `__serpent_dec_blk8_avx` perform the 32-round cipher. Macro families `S0_1` through `S7_2`, `SI0_1` through `SI7_2`, `K2`, `LK2`, `KL2`, `S`, `SP`, `transpose_4x4`, `read_blocks`, and `write_blocks` express Serpent's S-box, linear transform, key mixing, and bit-sliced packing.

Control flow: The ECB wrappers load eight blocks, call the encrypt or decrypt core, then store reordered output registers. The encrypt core initializes an all-ones mask, transposes input blocks into bit-sliced lanes, applies key 0, runs 32 Serpent S-box/linear-transform rounds with keys 1 through 31, applies final key 32, and transposes back. Decryption reads blocks, applies key 32, walks inverse S-boxes and inverse linear transforms down to key 0, then writes plaintext. CBC decrypt decrypts eight ciphertext blocks and uses `store_cbc_8way` to XOR with the prior ciphertext chain.

State and persistence: The file owns no global state. It reads `struct serpent_ctx` round keys through the context pointer and uses volatile XMM registers. Public wrappers rely on the caller having enabled kernel FPU/vector usage.

Dependencies and integration points: It includes `linux/linkage.h`, `linux/cfi_types.h`, `asm/frame.h`, and `glue_helper-asm-avx.S`. It is used by `serpent_avx_glue.c` and by AVX2 glue as an 8-block fallback. The C header `serpent-avx.h` declares the ABI.

Risks and test signals: Bit-sliced Serpent is extremely register-order-sensitive: wrong transposition, inverse S-box ordering, or final store ordering changes every block. CBC chaining depends on ciphertext still being readable. Tests should include Serpent known-answer vectors, 8-block ECB/CBC bulk paths, AVX2 fallback users, in-place decrypt, objtool/CFI symbol validation, and mixed-size requests that leave scalar tails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx-x86_64-asm_64.S -->
