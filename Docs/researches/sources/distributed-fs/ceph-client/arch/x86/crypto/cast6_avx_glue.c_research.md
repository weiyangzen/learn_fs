<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/cast6_avx_glue.c

Purpose: This file registers AVX-accelerated CAST6 ECB and CBC skcipher algorithms. It connects Crypto API requests to the 8-way x86-64 AVX assembly implementation while retaining scalar generic CAST6 helpers for serial CBC encryption and residual blocks.

Important APIs/types/functions: Assembly entry points are `cast6_ecb_enc_8way`, `cast6_ecb_dec_8way`, and `cast6_cbc_dec_8way`. `cast6_setkey_skcipher()` wraps `cast6_setkey()`. Request handlers `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt` are registered in `cast6_algs[]` for `ecb(cast6)` and `cbc(cast6)` with driver names `ecb-cast6-avx` and `cbc-cast6-avx`.

Control flow: `cast6_init()` refuses registration unless SSE and YMM xstate are available. For ECB, the helper macro opens an skcipher walk, enters the kernel FPU for chunks of at least eight blocks, invokes the 8-way assembly routine, then exits the FPU before one-block scalar fallback. CBC encrypt walks one block at a time because chaining prevents parallel encryption. CBC decrypt uses 8-way assembly for bulk decryption and then scalar `__cast6_decrypt` for the tail.

State and persistence: Per-transform state is `struct cast6_ctx` stored in the Crypto API context. The CBC IV is updated in the walk object after each processed group. Registered algorithm state persists only while the module is loaded.

Dependencies and integration points: It depends on the generic CAST6 implementation, the shared `ecb_cbc_helpers.h` macro framework, x86 FPU/xstate support, and the assembly file in the same directory. It integrates with module autoloading through `MODULE_ALIAS_CRYPTO("cast6")`.

Risks and test signals: The vector path assumes callers never reach it without `kernel_fpu_begin()`. The helper threshold must match the 8-block assembly contract. Tests should cover CAST6 ECB/CBC known-answer vectors, request sizes below/at/above eight blocks, in-place CBC decrypt, fallback behavior for remainders, feature-gated module load failure, and comparison against the generic `cast6` driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6_avx_glue.c -->
