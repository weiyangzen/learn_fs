# File Research: sources/block-storage/cryptsetup/lib/utils_crypt.c

## Purpose
Implements cipher, integrity, PBKDF, and hex conversion utility logic.

## Key Responsibilities
- Parses cipher specs into cipher name, key count, and mode.
- Maps shorthand/default cipher modes such as `plain` and absent mode to `cbc-plain`.
- Parses integrity strings into kernel-style integrity mode names.
- Validates PBKDF names case-insensitively.
- Converts hex strings to bytes using constant-data-flow helper logic.
- Converts bytes to safe-allocated hex strings and logs bytes as hex.
- Detects `null`/`cipher_null` cipher specs.

## Important Details
- CAPI cipher names are treated specially because embedded dashes in driver names can be ambiguous.
- `crypt_hex_to_bytes()` optionally uses safe allocation for key material.
- `crypt_bytes_to_hex(0, ...)` returns `"-"` in a safe allocation.
- Integrity parser enforces key-size expectations for AEAD, HMAC, PHMAC, and CMAC modes.

## Dependencies
Uses public libcryptsetup constants, `utils_crypt.h`, safe memory allocation, and backend constant-time memory helpers.
