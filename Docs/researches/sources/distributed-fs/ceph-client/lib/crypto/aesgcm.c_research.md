# sources/distributed-fs/ceph-client/lib/crypto/aesgcm.c

## Purpose
This file implements a compact AES-GCM authenticated encryption library on top of AES-CTR and GF(2^128) GHASH.

## Important APIs, Types, and Functions
Exported APIs are `aesgcm_expandkey()`, `aesgcm_encrypt()`, and `aesgcm_decrypt()`. Internal helpers are `aesgcm_mac()` and `aesgcm_crypt()`. The context `struct aesgcm_ctx` stores an AES encryption key, GHASH key, and auth tag size.

## Control Flow
Key expansion validates auth tag size and prepares AES, then encrypts the zero block to derive the GHASH key. Encryption initializes the 96-bit IV counter, encrypts/decrypts data with AES-CTR starting at counter value 2, and authenticates ciphertext and associated data with GHASH plus encrypted counter block 1. Decryption authenticates the input ciphertext first with `crypto_memneq()`, clears the temporary tag on failure, and only then decrypts.

## State and Persistence
Caller-owned context persists AES/GHASH key material and tag size. Per-message state includes the big-endian counter block, GHASH accumulator, temporary AES block, and tag buffer. No storage persists outside memory.

## Dependencies and Integration Points
It depends on AES, GF128 hash, crypto utils, unaligned/big-endian helpers, and module exports. Optional selftests use NIST/McGrew-Viega-style vectors and exercise in-place encrypt/decrypt.

## Risks and Test Signals
Risks include counter overflow behavior, tag-size validation, GHASH length encoding, decrypt-before-auth mistakes, partial final block handling, and IV reuse by callers. Test signals include AES-GCM known-answer tests for 128/192/256-bit keys, AAD coverage, tag failure tests, and in-place operation selftests.
