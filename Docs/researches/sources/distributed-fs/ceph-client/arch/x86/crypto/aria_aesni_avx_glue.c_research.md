# sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx_glue.c

Purpose: Registers the 16-way AVX/AES-NI ARIA skcipher backend for ECB and CTR, with optional GFNI routines when available.

Important APIs/types/functions: declares and exports 16-way AES-NI and GFNI assembly symbols. Uses `struct aria_avx_ops` for runtime-selected pointers and `struct aria_avx_request_ctx` for one 16-block CTR keystream buffer. Provides `aria_avx_ecb_encrypt`, `aria_avx_ecb_decrypt`, `aria_avx_ctr_encrypt`, `aria_avx_set_key`, and `aria_avx_init_tfm`.

Control flow: module init validates AVX, AES, OSXSAVE, and SSE/YMM xfeatures; then it selects GFNI 16-way routines or regular AES-NI routines and registers `ecb(aria)` plus `ctr(aria)` at priority 400. ECB uses helper macros to process 16-block chunks and scalar tails. CTR walks request segments, runs 16-block chunks in FPU context, then scalar full blocks, then a final partial tail.

State and persistence: per-transform state is `struct aria_ctx`; per-request state is the keystream scratch array. The CTR IV is the only mutable protocol state and is incremented as blocks are consumed. The static dispatch table is set once at module init.

Dependencies and integration points: depends on generic ARIA `aria_set_key`, `aria_encrypt`, `aria_decrypt`, crypto walk helpers, x86 feature probing, and the assembly file `aria-aesni-avx-asm_64.S` for the actual 16-way operations. It is a lower-priority fallback beneath AVX2/AVX512 drivers.

Risks: the assembly routines require FPU ownership, so all vector calls must remain wrapped. Partial CTR handling must only happen on the final segment or the IV/ciphertext stream can diverge. Exported 16-way symbols are also used by AVX2 and AVX512 glue for tail processing, so ABI drift affects multiple modules.

Test signals: validate driver priority selection, generic fallback for short buffers, in-place CTR, sub-block CTR lengths, CPU feature rejection on missing YMM state, and GFNI selection when `X86_FEATURE_GFNI` is present.
