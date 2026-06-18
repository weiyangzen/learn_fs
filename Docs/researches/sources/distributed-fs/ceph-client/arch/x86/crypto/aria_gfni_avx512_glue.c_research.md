# sources/distributed-fs/ceph-client/arch/x86/crypto/aria_gfni_avx512_glue.c

Purpose: Registers the AVX512/GFNI ARIA skcipher backend and composes it with lower-width GFNI AVX and AVX2 routines for tail processing.

Important APIs/types/functions: declares 64-way assembly functions, uses `struct aria_avx_ops aria_ops`, and defines `struct aria_avx512_request_ctx` with a 64-block keystream buffer. Main callbacks are `aria_avx512_ecb_encrypt`, `aria_avx512_ecb_decrypt`, `aria_avx512_ctr_encrypt`, `aria_avx512_set_key`, and `aria_avx512_init_tfm`.

Control flow: ECB processing attempts 64-way, then 32-way, then 16-way, then scalar blocks. CTR mirrors that ordering inside skcipher walks, wrapping each vector call with FPU begin/end. Module init requires AVX, AVX2, AVX512F, AVX512VL, GFNI, OSXSAVE, and SSE/YMM/AVX512 xfeatures; then it wires 16-way and 32-way GFNI functions plus 64-way AVX512 functions and registers priority-600 algorithms.

State and persistence: no persistent state beyond registered algorithms and the initialized static dispatch table. Key schedule lives in `struct aria_ctx`; request scratch contains the large keystream buffer; IV state is updated in place.

Dependencies and integration points: depends on `aria-avx.h` declarations for lower-width GFNI functions, the AVX512 assembly symbols in `aria-gfni-avx512-asm_64.S`, skcipher helpers, and x86 FPU/xfeature checks. It supersedes AVX2 when available through crypto API priority.

Risks: the request context is 1024 bytes, so the `CRYPTO_ALG_SKCIPHER_REQSIZE_LARGE` flag is necessary. Correct operation depends on both CPU instruction bits and OS-managed ZMM state. Tail dispatch to lower-width functions assumes those modules/symbols are linked in the same build configuration.

Test signals: boot and module-load tests should confirm registration only on full AVX512/GFNI systems. Crypto tests should cover 64-, 32-, 16-, scalar-, and partial-tail paths, IV carry behavior, and priority selection over AVX2.
