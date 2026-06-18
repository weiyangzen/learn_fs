<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx_glue.c

Purpose: This file registers AVX-accelerated Serpent ECB and CBC skcipher algorithms and exports the 8-way AVX assembly symbols for other optimized modules.

Important APIs/types/functions: Exported symbols are `serpent_ecb_enc_8way_avx`, `serpent_ecb_dec_8way_avx`, and `serpent_cbc_dec_8way_avx`. `serpent_setkey_skcipher()` initializes `struct serpent_ctx`. `serpent_algs[]` registers `ecb-serpent-avx` and `cbc-serpent-avx` with priority 500.

Control flow: Module init verifies SSE and YMM xstate. ECB encrypt/decrypt handlers walk the skcipher request, use AVX 8-way routines for bulk, and fall back to `__serpent_encrypt`/`__serpent_decrypt` one block at a time. CBC encrypt is scalar, while CBC decrypt uses the 8-way assembly before scalar tail handling.

State and persistence: Per-transform key schedule state lives in `struct serpent_ctx`; algorithm registration persists while the module is loaded. No additional global mutable state is created.

Dependencies and integration points: It depends on generic Serpent, the shared helper macros, x86 FPU xstate support, and the AVX assembly file. Exported symbols are consumed by `serpent_avx2_glue.c`.

Risks and test signals: Because this module exports assembly entry points, ABI stability matters for AVX2 fallback users. Tests should include module dependency loading, Serpent ECB/CBC known-answer vectors, in-place CBC decrypt, requests smaller than eight blocks, and xstate-gated load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx_glue.c -->
