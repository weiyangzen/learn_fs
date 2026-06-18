<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx2-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx2-asm_64.S

Purpose: This assembly file implements the AVX2 16-way Serpent fast path for x86-64. It doubles the AVX 8-way structure by using YMM registers and AVX2 load/store helpers.

Important APIs/types/functions: Public functions are `serpent_ecb_enc_16way`, `serpent_ecb_dec_16way`, and `serpent_cbc_dec_16way`. Local cores `__serpent_enc_blk16` and `__serpent_dec_blk16` run the bit-sliced cipher. Macro families mirror the AVX file but use YMM registers: S-boxes `S0` through `S7`, inverse S-boxes `SI0` through `SI7`, key helpers `K2`, `LK2`, `KL2`, and block transposition helpers. `load_16way`, `store_16way`, and `store_cbc_16way` come from `glue_helper-asm-avx2.S`.

Control flow: ECB wrappers clear upper vector state with `vzeroupper`, load sixteen blocks, call the encrypt/decrypt core, store the results, clear upper state again, and return. The encrypt core transposes sixteen blocks into bit-sliced YMM lanes, applies all Serpent rounds in order, and transposes back. The decrypt core performs the inverse sequence from round key 32 down to 0. CBC decrypt decrypts sixteen blocks and uses the AVX2 CBC store helper to XOR with the input chain.

State and persistence: No persistent state is stored. The code reads Serpent round keys from the caller's context and mutates destination buffers. It uses YMM registers and therefore requires correct XSAVE/YMM ownership from the caller.

Dependencies and integration points: It includes `linux/linkage.h`, `asm/frame.h`, and `glue_helper-asm-avx2.S`. It is registered through `serpent_avx2_glue.c`, which also depends on the AVX 8-way functions for fallback.

Risks and test signals: AVX2 lane ordering, `vzeroupper`, and CBC chain construction are key integration risks. The glue's FPU threshold uses the 8-way constant, so the assembly must be safe when called only for 16-block chunks. Tests should cover exact 16-block requests, 16+8+tail decomposition, CBC in-place decryption, CPU gating for AVX2/OSXSAVE/YMM, and known-answer comparisons against generic Serpent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx2-asm_64.S -->
