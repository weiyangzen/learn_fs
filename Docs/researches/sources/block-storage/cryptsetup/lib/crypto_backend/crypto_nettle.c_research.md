# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nettle.c

Implements the Nettle backend.

Key points:
- Version string is compile-time if `nettle/version.h` is available.
- Hash table stores function pointers for init/update/digest plus HMAC set-key/update/digest.
- Supports SHA-1, SHA-224/256/384/512, RIPEMD-160, and SHA3 variants when `NETTLE_SHA3_FIPS202` is true.
- Adds local HMAC wrappers for SHA3 because Nettle lacks direct HMAC helper wrappers for them.
- Hash contexts store a union of concrete Nettle hash contexts and reset by re-running the init function.
- HMAC contexts copy the key, retain key length, and reset by reapplying the key.
- RNG is unavailable and returns `-EINVAL`.
- PBKDF2 uses `nettle_pbkdf2()` after creating a cryptsetup HMAC context; Argon2 delegates to `argon2()`.
- Ciphers and BitLocker AES-CCM are kernel-only.
- Constant-time comparison returns inverted `memeql_sec()` semantics to match cryptsetup’s memcmp-like return convention.
- FIPS mode always returns false.

Storage relevance:
- A hash/HMAC/PBKDF provider paired with kernel cipher handling.
- Important for builds preferring Nettle while still relying on kernel crypto for storage encryption modes.
