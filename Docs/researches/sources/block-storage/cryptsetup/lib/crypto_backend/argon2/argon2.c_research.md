# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.c

## Purpose
Vendored Argon2 public API implementation: hashing, encoded hash generation, verification, error messages, and encoded-length calculation.

## Key Content
`argon2_ctx()` validates inputs, normalizes requested memory into lane/slice-aligned blocks, initializes an `argon2_instance_t`, fills memory, and finalizes the tag. `argon2_hash()` builds a context from simple arguments and can return raw hash, encoded hash, or both. Type-specific wrappers cover Argon2d, Argon2i, and Argon2id. Verification decodes encoded strings into a context, recomputes the hash, and compares using `argon2_compare()`.

## Dependencies and Coupling
Uses `argon2.h`, `encoding.h`, and `core.h`. Calls core functions for validation, initialization, memory filling, and finalization.

## Invariants and Risks
Memory is wiped before freeing temporary outputs. Verification allocates buffers sized to the encoded string as an upper bound. The API supports Argon2 version 1.0 decoding and current version 1.3 encoding.
