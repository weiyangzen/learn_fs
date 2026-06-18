# sources/distributed-fs/ceph-client/lib/crypto/aescfb.c

## Purpose
This file implements the generic AES-CFB library encryption/decryption helpers and optional selftests.

## Important APIs, Types, and Functions
It exports `aescfb_encrypt()` and `aescfb_decrypt()`. Selftest state is an `aescfb_tv[]` vector table and module init/exit functions under `CONFIG_CRYPTO_SELFTESTS`.

## Control Flow
Encryption copies the IV to a local chaining value, encrypts it to produce keystream blocks, XORs source to destination block-by-block, and shifts ciphertext into the chaining value. Decryption precomputes keystream from IV/source ciphertext and alternates two keystream buffers so in-place decryption is safe. Selftest prepares an encryption key, checks encrypt/decrypt and in-place encryption against vectors.

## State and Persistence
No state persists in the module. Callers provide an AES encryption key and IV; local chaining and keystream buffers are stack state.

## Dependencies and Integration Points
It depends on `crypto/aescfb.h`, AES library encryption-key preparation/encryption, XOR helpers, and module exports. It is built as `libaescfb.o` when `CRYPTO_LIB_AESCFB` is selected.

## Risks and Test Signals
Risks include in-place decryption hazards, handling lengths not divisible by 16, IV mutation expectations, and AES key misuse. Selftests with varied key sizes and in-place operations are the primary signal.
