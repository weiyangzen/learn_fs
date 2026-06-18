# sources/distributed-fs/ceph-client/arch/x86/crypto/cast5-avx-x86_64-asm_64.S

Purpose: Implements 16-block parallel CAST5 ECB encryption/decryption and CBC decryption using x86_64 AVX/SSE registers. It is the assembly backend used by `cast5_avx_glue.c`.

Important APIs/functions: public symbols are `cast5_ecb_enc_16way`, `cast5_ecb_dec_16way`, and `cast5_cbc_dec_16way`; internal helpers are `__cast5_enc_blk16` and `__cast5_dec_blk16`. The file references external S-box tables `cast_s1` through `cast_s4` and expects `struct cast5_ctx` layout fields `Km`, `Kr`, and round count.

Control flow: ECB entry points load 16 64-bit blocks into XMM pairs, call the encrypt or decrypt helper, then write swapped left/right halves. Round macros broadcast masking subkeys, derive rotation counts, perform CAST5 F1/F2/F3 S-box lookups through scalar GPRs for two lanes at a time, and XOR results into Feistel halves. Decryption reverses key order and checks the context round count for reduced-round keys. CBC decrypt decrypts 16 blocks, then XORs each plaintext with the prior ciphertext block before writing.

State and persistence: key schedule and round count live in `struct cast5_ctx`; S-boxes are read-only external data. The assembly mutates only output buffers and registers. CBC decrypt reads source ciphertext as chaining state.

Dependencies and integration points: depends on `cast5_avx_glue.c` for CPU xfeature gating, crypto registration, and scalar fallback. Requires Linux linkage/frame macros, AVX/SSE register state, and generic CAST5 symbols/tables.

Risks: the implementation mixes vector lanes with scalar S-box table loads, so register allocation and callee-saved preservation are delicate. CBC decrypt assumes source remains intact while output is produced. Round count handling must match CAST5 reduced-round behavior for short keys.

Test signals: CAST5 ECB/CBC vectors with minimum and maximum key sizes, reduced-round keys, exactly 16-block decrypt, in-place CBC decrypt, non-16-block fallback through glue, and CPU xfeature rejection should cover the integration.
