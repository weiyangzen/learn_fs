# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_openssl.c

Implements the OpenSSL/LibreSSL backend.

Key points:
- Handles legacy OpenSSL, LibreSSL, and OpenSSL 3 provider APIs behind `OPENSSL3_API`.
- OpenSSL 3 path creates a private `OSSL_LIB_CTX` outside FIPS mode, loads default provider, optionally loads legacy provider, and records provider/thread/Argon2 flags in the backend version.
- Compatibility wrappers support older OpenSSL/LibreSSL allocation APIs.
- Hash names normalize selected BLAKE2 spellings before lookup/fetch.
- OpenSSL 3 uses fetched `EVP_MD`/`EVP_CIPHER`; non-3 uses classic `EVP_get_*`.
- Hash contexts use `EVP_MD_CTX`; HMAC uses `EVP_MAC` for OpenSSL 3 and `HMAC_CTX` for older APIs.
- RNG uses `RAND_bytes()` and rejects lengths above `INT_MAX`.
- PBKDF2 uses OpenSSL 3 `EVP_KDF` or old `PKCS5_PBKDF2_HMAC()` with integer overflow guards.
- Argon2 uses OpenSSL 3 KDF when available, including threads/lanes/memory parameters; otherwise delegates to cryptsetup `argon2()`.
- Cipher init constructs names like `aes-256-xts` or `sm4-ctr`, validates key length, disables padding, and falls back to kernel cipher if OpenSSL lacks the algorithm.
- BitLocker key decrypt uses AES-256-CCM via EVP when CCM controls are available.
- FIPS detection uses OpenSSL 3 default property status or legacy `FIPS_mode()` when compiled with `ENABLE_FIPS`.

Storage relevance:
- Broadest userspace backend in this group, with both native cipher support and kernel fallback.
- Provider context behavior is important for algorithms that live in OpenSSL 3 legacy provider.
