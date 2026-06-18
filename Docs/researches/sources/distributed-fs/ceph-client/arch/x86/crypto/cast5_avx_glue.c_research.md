<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast5_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/cast5_avx_glue.c

Purpose: This file is the Linux Crypto API glue for the AVX CAST5 skcipher implementation. It registers high-priority ECB and CBC variants that use 16-way assembly routines for bulk work and generic CAST5 block helpers for leftovers or serial CBC encryption.

Important APIs/types/functions: The exported-to-assembly prototypes are `cast5_ecb_enc_16way`, `cast5_ecb_dec_16way`, and `cast5_cbc_dec_16way`. `cast5_setkey_skcipher()` adapts `cast5_setkey()` to `struct crypto_skcipher`. The request handlers are `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt`. `cast5_algs[]` registers `ecb(cast5)` as `ecb-cast5-avx` and `cbc(cast5)` as `cbc-cast5-avx` with priority 200.

Control flow: Module init first checks that the CPU and OS expose SSE/YMM xstate through `cpu_has_xfeatures(XFEATURE_MASK_SSE | XFEATURE_MASK_YMM)`. If available, skcipher registration exposes the algorithms. ECB encrypt/decrypt walks the request with `ECB_WALK_START`, processes 16-block chunks under `kernel_fpu_begin()` with AVX assembly, then drops to one-block `__cast5_encrypt` or `__cast5_decrypt` for the tail. CBC encryption is intentionally serial because each block depends on the previous ciphertext. CBC decryption processes independent ciphertext blocks 16 at a time and XORs the decrypted first block with the incoming IV through the shared helper.

State and persistence: Persistent state is limited to per-transform `struct cast5_ctx` key schedule storage and the registered algorithm table. Request state is local to `skcipher_walk`, including source/destination pointers, residual byte count, and CBC IV updates. No file-backed state exists.

Dependencies and integration points: It depends on `crypto/cast5.h`, `crypto/algapi.h`, `crypto/internal/skcipher.h` through `ecb_cbc_helpers.h`, x86 FPU save/restore APIs, and the matching AVX assembly object that provides the 16-way symbols. It integrates with the Crypto API module loader through `MODULE_ALIAS_CRYPTO("cast5")`.

Risks and test signals: The FPU section must begin only for full vector chunks and must be closed before generic scalar fallbacks. CBC in-place decryption depends on the helper preserving the previous ciphertext before overwrite. Tests should include Crypto API CAST5 ECB/CBC vectors, in-place and out-of-place requests, unaligned scatterlists, non-multiple request tails, CPU feature refusal on missing YMM state, and module unload after active transform teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast5_avx_glue.c -->
