# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10-glue.c

Purpose: registers and drives ppc64le Power10 stitched AES-GCM/RFC4106 AEAD implementations.

Important APIs/types/functions: types `p10_aes_key`, `gcm_ctx`, `Hash_ctx`, `p10_aes_gcm_ctx`, `p10_aes_key`, `Hash_ctx`, `crypto_tfm`, `p10_aes_gcm_ctx`, `crypto_tfm`, `p10_aes_gcm_ctx`, and 8 more; functions `vsx_begin`, `vsx_end`, `set_subkey`, `set_aad`, `gcmp10_init`, `finish_tag`, `set_authsize`, `p10_aes_gcm_setkey`, `p10_aes_gcm_crypt`, `rfc4106_setkey`, `rfc4106_setauthsize`, `rfc4106_encrypt`, `rfc4106_decrypt`, `p10_aes_gcm_encrypt`, `p10_aes_gcm_decrypt`, `p10_init`, `p10_exit`; macros `PPC_ALIGN`, `GCM_IV_SIZE`, `RFC4106_NONCE_SIZE`. Source size is 433 lines / 10724 bytes.

Implementation notes: The glue validates auth sizes and keys, manages kernel VSX enable/disable, linearizes AAD when needed, initializes H tables and counters, walks AEAD scatterlists, invokes aes_p10_gcm_encrypt/decrypt, computes/verifies tags, and registers normal GCM plus RFC4106 variants.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `linux/unaligned.h`, `asm/simd.h`, `asm/switch_to.h`, `crypto/gcm.h`, `crypto/aes.h`, `crypto/algapi.h`, `crypto/b128ops.h`, `crypto/gf128mul.h`, `crypto/internal/simd.h`, `crypto/internal/aead.h`, `crypto/internal/hash.h`, `crypto/internal/skcipher.h`, `crypto/scatterwalk.h`, `linux/cpufeature.h`, and 3 more. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
