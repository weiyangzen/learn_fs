<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx2_glue.c

Purpose: This file registers the highest-priority AVX2 Serpent ECB and CBC skcipher implementations. It layers a 16-block AVX2 path over the existing 8-block AVX and scalar fallbacks.

Important APIs/types/functions: It declares `serpent_ecb_enc_16way`, `serpent_ecb_dec_16way`, and `serpent_cbc_dec_16way`. `serpent_setkey_skcipher()` calls `__serpent_setkey()`. `serpent_algs[]` registers `ecb-serpent-avx2` and `cbc-serpent-avx2` with priority 600 and aliases `serpent`/`serpent-asm`.

Control flow: Init checks `X86_FEATURE_AVX2`, `X86_FEATURE_OSXSAVE`, and SSE/YMM xstate. ECB handlers process 16-block AVX2 chunks, then 8-block AVX chunks, then one-block generic Serpent. CBC encryption remains scalar; CBC decryption uses 16-way, then 8-way, then scalar paths. The shared helper starts the FPU section when at least eight blocks are available, so both vector widths run under FPU ownership.

State and persistence: Persistent module state is the registered skcipher table. Per-transform state is `struct serpent_ctx`. Request-local state is in `skcipher_walk` and CBC IV.

Dependencies and integration points: It depends on `serpent-avx.h` for the 8-way fallback ABI, `ecb_cbc_helpers.h`, generic Serpent key setup/block routines, and the AVX2 assembly file. It integrates with Crypto API priority selection above AVX and SSE2 drivers.

Risks and test signals: The AVX2 driver has a stronger CPU feature contract than the AVX fallback it calls. If the AVX module symbols are not linked/exported as expected, registration or calls fail. Tests should cover driver priority selection, AVX2 feature refusal, 16+8+tail decomposition, CBC in-place decrypt, and generic equivalence vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx2_glue.c -->
