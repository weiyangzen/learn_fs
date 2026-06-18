# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend.h

## Purpose
Main internal crypto backend API for libcryptsetup.

## Key Content
Declares backend lifecycle/version/flags, hash, HMAC, RNG, PBKDF limits and execution, PBKDF benchmarking, CRC32/CRC32C, Base64, UTF-8/UTF-16 conversion, block cipher operations, kernel cipher benchmark/checks, storage encryption wrappers, temporary BITLK AES-CCM key decrypt helper, secure memzero/memcpy/memeq helpers, and FIPS status queries.

## Dependencies and Coupling
Included widely by libcryptsetup and backend implementation files. Provides an abstraction over concrete providers such as OpenSSL, gcrypt, NSS, nettle, mbedTLS, kernel crypto, and internal PBKDF code.

## Invariants and Risks
Callers receive errno-style negative failures. Backend flags advertise special behavior such as kernel support, PBKDF2 signed-iteration limits, and native Argon2 availability.
