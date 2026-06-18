# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_mbedtls.c

Implements the mbedTLS backend.

Key points:
- Global state includes mbedTLS entropy and CTR-DRBG contexts initialized in `crypt_backend_init()` and freed in `crypt_backend_destroy()`.
- Hash support is limited to SHA-1, SHA-224/256/384/512, and RIPEMD-160 through `crypt_get_hash()`.
- Hash and HMAC wrap `mbedtls_md_context_t`; finalization copies through `crypt_backend_memcpy()`, zeroes temporary digest buffers, and resets contexts.
- RNG rejects FIPS mode with `-ENOTSUP`; otherwise uses CTR-DRBG and toggles prediction resistance based on randomness quality.
- Cipher support is table-driven for AES, ARIA, Camellia and modes ECB/CBC/CFB/OFB/CTR/XTS.
- CBC padding is disabled. ECB is processed in block-sized chunks because mbedTLS ECB expects exact block-size input.
- PBKDF2 uses `mbedtls_pkcs5_pbkdf2_hmac_ext()` when available, otherwise a manually initialized HMAC context.
- Argon2 always delegates to cryptsetup’s `argon2()` wrapper.
- BitLocker key decrypt uses AES-CCM authenticated decrypt through `mbedtls_ccm_auth_decrypt()`.
- `crypt_backend_memeq()` delegates to `mbedtls_ct_memcmp()`; FIPS mode always returns false.

Storage relevance:
- A self-contained userspace crypto backend with narrower algorithm coverage than OpenSSL/gcrypt, but direct cipher support without kernel fallback for listed ciphers.
