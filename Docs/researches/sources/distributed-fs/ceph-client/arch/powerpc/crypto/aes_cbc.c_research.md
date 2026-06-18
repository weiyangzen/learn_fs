# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_cbc.c

Purpose: registers the Power8 VSX AES-CBC skcipher with fallback handling.

Important APIs/types/functions: types `p8_aes_cbc_ctx`, `crypto_skcipher`, `p8_aes_key`, `p8_aes_key`, `p8_aes_cbc_ctx`, `crypto_skcipher`, `p8_aes_cbc_ctx`, `p8_aes_cbc_ctx`, `crypto_skcipher`, `skcipher_walk`, and 2 more; functions `p8_aes_cbc_init`, `p8_aes_cbc_exit`, `p8_aes_cbc_setkey`, `p8_aes_cbc_crypt`, `p8_aes_cbc_encrypt`, `p8_aes_cbc_decrypt`. Source size is 137 lines / 3580 bytes.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `asm/simd.h`, `asm/switch_to.h`, `crypto/aes.h`, `crypto/internal/simd.h`, `crypto/internal/skcipher.h`, `linux/err.h`, `linux/kernel.h`, `linux/module.h`, `linux/uaccess.h`, `aesp8-ppc.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
