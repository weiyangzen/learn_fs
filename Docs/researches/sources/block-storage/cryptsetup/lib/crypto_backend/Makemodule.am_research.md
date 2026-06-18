# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/Makemodule.am

## Purpose
Autotools build module for the internal crypto backend archive.

## Key Content
Builds `libcrypto_backend.la` from common backend interfaces, kernel cipher support, crypto storage wrappers, PBKDF checks, CRC32, base64, UTF-8 conversion, Argon2 generic wrapper, cipher generic/check helpers, and memory utilities. Conditionally adds provider implementations for gcrypt, OpenSSL, NSS, kernel, nettle, and mbedTLS. Optionally adds internal PBKDF2 and links bundled `libargon2.la`.

## Dependencies and Coupling
Selected by configure-time conditionals. The main `libcryptsetup.la` links this archive directly.

## Invariants and Risks
All backend provider source lists must match configure feature tests. When `CRYPTO_INTERNAL_ARGON2` is enabled, the internal Argon2 archive must be built before this archive.
