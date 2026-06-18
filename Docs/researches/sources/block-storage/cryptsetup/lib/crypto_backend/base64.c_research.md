# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/base64.c

## Purpose
Base64 encode/decode helpers for the crypto backend.

## Key Content
Implements RFC4648 alphabet encoding with `=` padding and a decoder that tolerates whitespace around input characters. Decode validates padding positions, unused low bits in padded sextets, and rejects trailing non-whitespace data after padding. Errors other than allocation failure are normalized to `-EINVAL`.

## Dependencies and Coupling
Includes `crypto_backend.h`. Used by higher-level metadata/token code needing binary-to-text conversion.

## Invariants and Risks
`crypt_base64_decode()` requires `out_length`. If input length is `(size_t)-1`, it treats input as NUL-terminated. Output buffers are heap allocated and caller-owned.
