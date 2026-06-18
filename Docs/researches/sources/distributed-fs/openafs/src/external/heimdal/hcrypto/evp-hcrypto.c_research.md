## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.c

Purpose: built-in hcrypto EVP provider. It exposes static `EVP_CIPHER` and `EVP_MD` descriptors backed by Heimdal's AES, DES/3DES, RC2, RC4, Camellia, SHA, MD2, MD4, and MD5 implementations.

Important APIs/functions: AES helpers `aes_init()` and `aes_do_cipher()` support AES CBC and CFB8 descriptors for 128/192/256-bit keys. Digest provider functions return `hc_evp_md` descriptors for SHA256, SHA384, SHA512, SHA1, MD5, MD4, and MD2. DES helpers wrap DES-CBC and 3DES-CBC. RC2 helpers use variable effective key length based on EVP context key length. Camellia helpers wrap CBC descriptors for 128/192/256-bit keys. RC4 helpers expose stream-cipher descriptors for default and 40-bit keys.

Control flow: each exported `EVP_hcrypto_*` returns the address of a static descriptor. During EVP initialization, descriptor `init` callbacks expand keys into context-owned cipher data. During updates, descriptor `do_cipher` callbacks call the primitive mode function using `ctx->iv` and `ctx->encrypt`. Digest descriptors provide init/update/final function pointers and context sizes directly from hash implementations.

State and persistence: no provider global mutable state. EVP context-owned `cipher_data` persists expanded key schedules (`AES_KEY`, `DES_key_schedule`, `struct des_ede3_cbc`, `struct rc2_cbc`, `CAMELLIA_KEY`, `RC4_KEY`). `ctx->iv` is mutated by block modes and CFB8. RC4 key stream state mutates inside `RC4_KEY`.

Dependencies: `evp.h`, `evp-hcrypto.h`, `krb5-types.h`, `des.h`, `camellia.h`, `aes.h`, `rc2.h`, `rc4.h`, `sha.h`, `md2.h`, `md4.h`, and `md5.h`.

Integration points: core provider for hcrypto EVP when platform-specific providers are unavailable or not selected. Depends on primitive wrappers in this subset (`aes.c`, `camellia.c`, `des.c`) and other hcrypto primitives outside this subset.

Risks: initialization callbacks ignore return codes from primitive key setup, so invalid key lengths or setup failures are not propagated. DES-CBC uses `DES_set_key_unchecked()` and does not set parity/weak-key checks; 3DES sets odd parity but also uses unchecked schedules. Legacy algorithms MD2/MD4/MD5/DES/RC2/RC4 are exposed for compatibility and should be policy-gated by callers. The AES CFB8 descriptor block-size choices differ from CommonCrypto's AES-256 CFB8 descriptor, so provider parity should be tested. No cleanup callbacks zeroize context key schedules when EVP frees cipher data.

Test signals: EVP known-answer vectors for every descriptor, encrypt/decrypt round trips with IV mutation checks, variable-length RC2/RC4 key tests, invalid key length behavior, provider equivalence tests against CommonCrypto where available, digest known-answer vectors, and memory cleanup/zeroization review for sensitive contexts.
