# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend_internal.h

## Purpose
Private crypto backend declarations shared among backend implementation units.

## Key Content
Declares internal PBKDF2, internal/external Argon2 wrapper, kernel cipher context structure, kernel cipher init/encrypt/decrypt/destroy/check functions, BITLK kernel AES-CCM decrypt helper, and internal constant-time memory comparison.

## Dependencies and Coupling
Includes `crypto_backend.h`. Used by backend source files that need implementation-only helpers not exposed to the rest of libcryptsetup.

## Invariants and Risks
`struct crypt_cipher_kernel` owns two file descriptors and must be destroyed to avoid descriptor leaks. Kernel helper availability depends on `ENABLE_AF_ALG`.
