# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.h

## Purpose
Internal declarations for Argon2 encoded hash string handling.

## Key Content
Declares decoded length constants, `encode_string()`, `decode_string()`, `b64len()`, and `numlen()`. Documents caller responsibilities for preinitializing buffers in `argon2_context`.

## Dependencies and Coupling
Includes `argon2.h`. Implemented by `encoding.c` and consumed by `argon2.c`.

## Invariants and Risks
The header exposes minimum decoded salt/output constants, but validation ultimately uses the broader Argon2 limits in `validate_inputs()`.
