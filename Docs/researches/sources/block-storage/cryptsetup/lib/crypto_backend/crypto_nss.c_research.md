# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nss.c

Implements the NSS backend.

Key points:
- `crypt_backend_init()` uses `NSS_NoDB_Init(".")` and records an NSS version string when `NSS_GetVersion()` is available.
- Supported hash/HMAC algorithms are SHA-1, SHA-256, SHA-384, and SHA-512.
- Hash contexts use `PK11_CreateDigestContext()`, `PK11_DigestBegin/Op/Final()`, and reset after final.
- HMAC imports a symmetric key into an internal NSS slot and creates a context by mechanism.
- RNG uses `PK11_GenerateRandom()` and rejects FIPS requests with `-EINVAL`.
- PBKDF2 delegates to generic `pkcs5_pbkdf2()` with table-provided HMAC block length; Argon2 delegates to `argon2()`.
- Ciphers and BitLocker AES-CCM are kernel-only.
- Constant-time comparison uses `NSS_SecureMemcmp()`.
- FIPS mode always returns false in this backend.

Storage relevance:
- Provides NSS hash/HMAC/RNG/PBKDF integration while leaving storage ciphers to the Linux kernel backend.
