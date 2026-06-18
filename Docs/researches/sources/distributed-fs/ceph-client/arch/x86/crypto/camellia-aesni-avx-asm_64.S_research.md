# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx-asm_64.S

Purpose: Implements 16-block parallel Camellia ECB encryption/decryption and CBC decryption using AVX plus AES-NI-assisted S-box transforms.

Important APIs/functions: public symbols are `camellia_ecb_enc_16way`, `camellia_ecb_dec_16way`, and `camellia_cbc_dec_16way`. Internal helpers `__camellia_enc_blk16` and `__camellia_dec_blk16` perform the core round schedule. Macro groups implement AES-assisted S-box transforms, byteslicing, FL/FLINV layers, key-dependent round loops, and output packing.

Control flow: entry points load 16 blocks, pre-whiten with `key_table`, byteslice into XMM registers, run Camellia round groups and FL layers, branch on `key_length` to include the extra 256/192-bit-key round group, unpack, and write output. CBC decryption uses stack temporary storage to protect in-place operation, then XORs decrypted blocks with previous ciphertext blocks before final output.

State and persistence: persistent state is the `struct camellia_ctx` key table generated in C. This assembly mutates output and stack/destination scratch only. It does not retain state after return.

Dependencies and integration points: called by `camellia_aesni_avx_glue.c` and exported for reuse by AVX2 glue as a 16-way tail. Depends on `camellia_ctx` layout (`key_table`, `key_length`), Linux frame/linkage macros, AVX, AES-NI, and SSE/YMM state management by the caller.

Risks: the transformed S-box tables and lane order are hard to audit and must match scalar Camellia exactly. CBC decrypt has in-place overlap concerns and manually arranged XOR order. Any key table layout change must update both C and assembly.

Test signals: Camellia known-answer tests for 128/192/256-bit keys, ECB and CBC decrypt, exactly 16-block requests, 16+tail requests through glue, and in-place CBC decrypt should exercise this file.
