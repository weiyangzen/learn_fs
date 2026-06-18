<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_avx_glue.c

Purpose: This file registers AVX-accelerated Twofish ECB and CBC skcipher drivers. It uses 8-way AVX routines for bulk work, 3-way routines for medium tails, and single-block assembly for final tails or serial CBC encryption.

Important APIs/types/functions: Assembly symbols are `twofish_ecb_enc_8way`, `twofish_ecb_dec_8way`, and `twofish_cbc_dec_8way`. `twofish_enc_blk_3way()` wraps `__twofish_enc_blk_3way(..., false)`. Request handlers `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt` register in `twofish_algs[]` with priority 400.

Control flow: Init verifies SSE/YMM xstate before registration. ECB paths process 8-block AVX chunks, 3-block 3-way chunks, and one-block scalar chunks. CBC encryption remains scalar. CBC decrypt uses 8-way AVX, then 3-way CBC helper, then scalar fallback.

State and persistence: Per-transform state is `struct twofish_ctx`. The module exports only registered algorithms; request state and IV updates live in `skcipher_walk`.

Dependencies and integration points: It depends on base Twofish symbols from `twofish_glue.c`, 3-way symbols from `twofish_glue_3way.c`, the AVX assembly file, `twofish.h`, and `ecb_cbc_helpers.h`. It integrates as the highest-priority Twofish driver in this set.

Risks and test signals: The fallback chain crosses module boundaries, so link/load ordering matters. The helper starts the FPU only for 8-block chunks and ends it before 3-way/scalar fallbacks. Tests should cover request sizes 1, 3, 8, and combinations such as 11 or 12 blocks, in-place CBC decrypt, blacklisted CPU behavior of the 3-way provider, and comparison against generic Twofish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_avx_glue.c -->
