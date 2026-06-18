# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-spe-glue.c

Purpose: registers and drives SPE accelerated AES ECB/CBC/CTR/XTS skcipher implementations on e500-class cores.

Important APIs/types/functions: types `ppc_aes_ctx`, `ppc_xts_ctx`, `ppc_aes_ctx`, `ppc_xts_ctx`, `crypto_skcipher`, `ppc_aes_ctx`, `skcipher_walk`, `crypto_skcipher`, `ppc_aes_ctx`, `skcipher_walk`, and 12 more; functions `spe_begin`, `spe_end`, `ppc_aes_setkey_skcipher`, `ppc_xts_setkey`, `ppc_ecb_crypt`, `ppc_ecb_encrypt`, `ppc_ecb_decrypt`, `ppc_cbc_crypt`, `ppc_cbc_encrypt`, `ppc_cbc_decrypt`, `ppc_ctr_crypt`, `ppc_xts_crypt`, `ppc_xts_encrypt`, `ppc_xts_decrypt`, `ppc_aes_mod_init`, `ppc_aes_mod_fini`; macros `MAX_BYTES`. Source size is 444 lines / 11804 bytes.

Implementation notes: The module keeps SPE sections short with MAX_BYTES, expands encrypt/decrypt/tweak keys, walks skcipher requests for ECB/CBC/CTR/XTS, updates IVs and tweaks, and registers algorithms with crypto priorities and module init/exit hooks.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `crypto/aes.h`, `linux/module.h`, `linux/init.h`, `linux/types.h`, `linux/errno.h`, `linux/crypto.h`, `asm/byteorder.h`, `asm/switch_to.h`, `crypto/algapi.h`, `crypto/internal/skcipher.h`, `crypto/xts.h`, `crypto/gf128mul.h`, `crypto/scatterwalk.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
