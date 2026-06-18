# sources/distributed-fs/ceph-client/arch/x86/crypto/aria-gfni-avx512-asm_64.S

Purpose: Provides the 64-block parallel ARIA backend for x86_64 AVX512/GFNI. It is the highest-priority ARIA implementation in this subset and implements ECB-style encrypt/decrypt plus CTR bulk processing over ZMM registers.

Important APIs/functions: public symbols are `aria_gfni_avx512_encrypt_64way`, `aria_gfni_avx512_decrypt_64way`, and `aria_gfni_avx512_ctr_crypt_64way`. Internal helpers include `__aria_gfni_avx512_crypt_64way` and `__aria_gfni_avx512_ctr_gen_keystream_64way`. Macros implement byteslicing, ARIA add-round-key, GFNI S-box transforms, diffusion layers, and final round operations.

Control flow: entry points load key schedule pointers for encryption or decryption, prepare 64 input blocks as sixteen ZMM lanes, run ARIA rounds with branches for 12, 14, or 16 rounds, then debyteslice and write output. CTR builds 64 sequential counter blocks, using a fast add path unless the low 64-bit counter may overflow; the carry path uses AVX512 mask registers to propagate high-word increments. The encrypted counters are XORed with source blocks before output.

State and persistence: persistent key state lives in `struct aria_ctx`, supplied by the glue. This file updates caller memory only: output blocks, scratch keystream blocks, and the 128-bit IV. No global data is mutable; lookup/bitmatrix constants are read-only.

Dependencies and integration points: requires AVX512F, AVX512VL, GFNI, OSXSAVE-enabled ZMM state, Linux frame/linkage macros, and generated `ARIA_CTX_*` offsets. `aria_gfni_avx512_glue.c` registers these routines and reuses lower-width GFNI AVX/AVX2 routines for tails.

Risks: the AVX512 counter-generation path has subtle carry and byte-swap logic. Mask-register behavior, ZMM temporary use, and output lane order must remain synchronized with the write macros. Incorrect OS xfeature gating would corrupt task FPU state.

Test signals: compare against generic ARIA for all key sizes and both ECB/CTR; exercise in-place CTR, exactly 64-block requests, 64+tail requests, and IV values near `0xffffffffffffffff` in the low half. Boot/module tests on CPUs with AVX512 but missing GFNI should reject registration.
