# sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx2_glue.c

Purpose: Registers the AVX2/AES-NI ARIA skcipher implementations for ECB and CTR and dispatches bulk work to 32-way assembly, optionally choosing GFNI variants at module init.

Important APIs/types/functions: declares and exports 32-way AVX2 and 32-way GFNI assembly functions. Uses `static struct aria_avx_ops aria_ops` as the selected dispatch table and `struct aria_avx2_request_ctx` for CTR scratch keystream storage. Main callbacks are `aria_avx2_ecb_encrypt`, `aria_avx2_ecb_decrypt`, `aria_avx2_ctr_encrypt`, `aria_avx2_set_key`, and `aria_avx2_init_tfm`.

Control flow: ECB walkers process 32-block chunks, then 16-block chunks, then scalar single blocks. CTR walks virtual skcipher segments, processes 32-block and 16-block full batches inside `kernel_fpu_begin/end`, then scalar ARIA blocks, and finally a partial tail only when the current walk segment covers the request end. Module init checks AVX, AVX2, AES, OSXSAVE, and YMM xfeatures, selects GFNI or AES-NI function pointers, and registers two skcipher algorithms at priority 500.

State and persistence: key material is stored in each `struct aria_ctx`. The request context holds only temporary keystream bytes. CTR mutates `walk.iv` as the counter advances. Module-global state is limited to `aria_ops` and registered algorithm metadata.

Dependencies and integration points: depends on `crypto/aria.h`, `ecb_cbc_helpers.h`, `aria-avx.h`, x86 CPU feature helpers, skcipher walk APIs, FPU ownership helpers, and lower-level AVX 16-way symbols for tails. It integrates with the Linux crypto API as `ecb-aria-avx2` and `ctr-aria-avx2`.

Risks: `ECB_WALK_START` is passed the 16-way threshold while 32-way blocks are attempted first; changes to helper semantics could affect fast-path batching. The CTR partial-tail condition must avoid generating a partial keystream before a later walk segment. Missing `CRYPTO_ALG_SKCIPHER_REQSIZE_LARGE` would be risky because the request context stores a 512-byte keystream.

Test signals: crypto manager selftests should select this driver on AVX2 hardware and verify ECB/CTR vectors, tail lengths below 16 blocks, requests spanning walk segments, in-place operation, GFNI and non-GFNI dispatch, and module unload registration cleanup.
