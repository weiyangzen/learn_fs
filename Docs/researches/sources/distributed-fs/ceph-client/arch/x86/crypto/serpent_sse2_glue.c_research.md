<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_sse2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_sse2_glue.c

Purpose: This file registers SSE2-accelerated Serpent ECB and CBC skcipher algorithms for x86. It supports 4-way operation on 32-bit and 8-way operation on 64-bit through `serpent-sse2.h`.

Important APIs/types/functions: `serpent_setkey_skcipher()` wraps `__serpent_setkey`. `serpent_decrypt_cbc_xway()` adapts the assembly decrypt routine for CBC by preserving previous ciphertext blocks and XORing all but the first block. `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt` are registered in `serpent_algs[]` under driver names `ecb-serpent-sse2` and `cbc-serpent-sse2` with priority 400.

Control flow: Init refuses registration unless the boot CPU advertises SSE2. ECB handlers use the x-way assembly wrapper for bulk and generic scalar helpers for tails. CBC encrypt is scalar. CBC decrypt calls `serpent_decrypt_cbc_xway` for full x-way groups and then scalar decrypt for remainders.

State and persistence: Runtime state consists of `struct serpent_ctx`, walk-local pointers and IV, and a small stack buffer in the CBC x-way helper for in-place decryption safety. Registered algorithms persist until module exit.

Dependencies and integration points: It depends on `serpent-sse2.h`, generic Serpent, `crypto/b128ops.h`, the shared ECB/CBC helper macros, and x86 SSE2 assembly. It provides a lower-priority fallback beneath AVX and AVX2 implementations.

Risks and test signals: The CBC helper has a custom in-place preservation path because the generic CBC macro only XORs the first block. Tests should cover both 32-bit and 64-bit parallel widths, exact x-way group sizes, in-place CBC decrypt, scalar tails, and priority fallback when AVX drivers are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_sse2_glue.c -->
