<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx2_glue.c

Purpose: This file registers AVX2/AES-NI SM4 skcipher drivers for ECB, CBC, and CTR. It reuses common AVX helper functions for ECB and scalar fallback while supplying 16-block AVX2 CBC decrypt and CTR functions.

Important APIs/types/functions: Assembly functions are `sm4_aesni_avx2_ctr_enc_blk16` and `sm4_aesni_avx2_cbc_dec_blk16`. `sm4_skcipher_setkey()` calls `sm4_expandkey()`. Local handlers `cbc_decrypt()` and `ctr_crypt()` call `sm4_avx_cbc_decrypt()` and `sm4_avx_ctr_crypt()` with `SM4_CRYPT16_BLOCK_SIZE`. `sm4_aesni_avx2_skciphers[]` registers `ecb-sm4-aesni-avx2`, `cbc-sm4-aesni-avx2`, and `ctr-sm4-aesni-avx2` with priority 500.

Control flow: Init checks AVX, AVX2, AES-NI, OSXSAVE, and SSE/YMM xstate before registering. ECB encrypt/decrypt use shared AVX helpers, which process up to 8 blocks at a time rather than the AVX2 assembly file. CBC decrypt and CTR use 16-block AVX2 function pointers for large chunks and common helper fallback for smaller chunks/tails.

State and persistence: Per-transform state is `struct sm4_ctx` containing expanded encryption and decryption round keys. Request state includes `skcipher_walk` and IV updates for CBC/CTR. Registered algorithms persist until module exit.

Dependencies and integration points: It depends on `sm4-avx.h`, generic SM4 key expansion, x86 FPU APIs, and the AVX2 assembly file. It integrates as the higher-priority SM4 implementation above the AVX driver.

Risks and test signals: Since ECB is reused from the AVX glue, priority selection may not imply wider ECB execution. Function-pointer block size must match 16-block assembly. Tests should cover SM4 ECB/CBC/CTR vectors, AVX2 module loading without the AVX common helpers failing to resolve, 16-block bulk paths, scalar tails, and IV continuity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx2_glue.c -->
