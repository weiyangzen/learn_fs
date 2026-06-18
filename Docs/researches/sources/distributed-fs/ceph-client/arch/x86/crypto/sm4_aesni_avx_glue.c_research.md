<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx_glue.c

Purpose: This file implements common SM4 AVX/AES-NI skcipher glue and exports reusable request handlers for AVX2. It registers ECB, CBC, and CTR SM4 algorithms and provides generic walking logic for vector and scalar tails.

Important APIs/types/functions: Assembly functions are `sm4_aesni_avx_crypt4`, `sm4_aesni_avx_crypt8`, `sm4_aesni_avx_ctr_enc_blk8`, and `sm4_aesni_avx_cbc_dec_blk8`. Exported helpers are `sm4_avx_ecb_encrypt`, `sm4_avx_ecb_decrypt`, `sm4_cbc_encrypt`, `sm4_avx_cbc_decrypt`, and `sm4_avx_ctr_crypt`. `sm4_aesni_avx_skciphers[]` registers `ecb(sm4)`, `cbc(sm4)`, and `ctr(sm4)` with priority 400.

Control flow: `ecb_do_crypt()` walks segments, opens the kernel FPU, processes 8-block chunks via assembly, then uses the 1-to-4-block assembly helper for residual full blocks. CBC encryption is serial with `sm4_crypt_block`. CBC decrypt accepts a caller-supplied vector block size/function, processes bulk chunks, then handles up to 8 remaining blocks with a stack keystream buffer and reverse XOR to preserve CBC dependencies. CTR similarly accepts a vector function, processes bulk chunks, handles up to 8 full-block counters in software, and finally processes a short final tail only when it is the last walk segment.

State and persistence: Per-transform state is `struct sm4_ctx` with expanded round keys. CBC and CTR mutate `walk.iv` as part of the Crypto API contract. The exported helper symbols are persistent module interfaces for the AVX2 module.

Dependencies and integration points: It depends on `asm/fpu/api.h`, `crypto/internal/skcipher.h`, `crypto/sm4.h`, and `sm4-avx.h`. It integrates with the Crypto API and module autoloading through aliases `sm4` and `sm4-aesni-avx`.

Risks and test signals: FPU begin/end scopes wrap all vector code and stack keystream use. CTR tail handling must only consume partial bytes on the final segment. CBC decrypt pointer arithmetic walks backwards through a temporary keystream buffer and is sensitive to `nblocks` bounds. Tests should include SM4 official ECB/CBC/CTR vectors, partial CTR tails, segmented scatterlists, IV carry and persistence, in-place CBC decrypt, and missing AVX/AES/YMM feature load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx_glue.c -->
