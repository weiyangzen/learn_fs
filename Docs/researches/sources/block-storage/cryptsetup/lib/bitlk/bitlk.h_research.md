# File Research: sources/block-storage/cryptsetup/lib/bitlk/bitlk.h

## Purpose
Public internal header for BitLocker-compatible metadata structures and operations used by cryptsetup’s BITLK format support.

## Key Content
Defines nonce, salt, MAC tag, validation datum sizes, normal state constant, encryption type enum, VMK protection enum, FVE entry type/value enums, and in-memory structures for VMKs, FVEK, validation metadata, and parsed BITLK volume metadata. Declares read, dump, unlock, activation, and cleanup functions.

## Dependencies and Coupling
Forward-declares `crypt_device`, `device`, and `volume_key` so BITLK code can integrate with libcryptsetup internals without exposing full definitions. Constants must match parser assumptions in `bitlk.c`.

## Invariants and Risks
`struct bitlk_metadata` owns allocated strings, VMK list, FVEK, and validation allocation; callers must use `BITLK_bitlk_metadata_free()`. The `sha256_fve` member is declared as `const char *sha256_fve[32]` but used as raw 32-byte digest storage in `bitlk.c`; this should be treated carefully because the type does not express the actual data shape.
