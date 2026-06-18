# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.c

## Purpose
Argon2 encoded-string parser and formatter, including internal unpadded Base64 helpers.

## Key Content
Implements constant-time-ish Base64 character mapping, unpadded Base64 encode/decode, strict minimal decimal parsing, `decode_string()` for `$argon2<T>[$v=...]$m=...,t=...,p=...$salt$hash`, `encode_string()`, and helper length calculators `b64len()` and `numlen()`.

## Dependencies and Coupling
Uses `encoding.h`, `core.h`, `argon2_type2string()`, and `validate_inputs()`. Called by `argon2_hash()` and `argon2_verify()`.

## Invariants and Risks
Decoded strings must match the requested Argon2 type and may not contain trailing data. Decimal fields reject leading-zero nonminimal forms and overflow. Salt and output buffers must be preallocated by the caller with maximum accepted sizes.
