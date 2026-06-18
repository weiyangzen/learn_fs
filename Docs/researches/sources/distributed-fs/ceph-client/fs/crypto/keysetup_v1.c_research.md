# sources/distributed-fs/ceph-client/fs/crypto/keysetup_v1.c

## Purpose
`keysetup_v1.c` contains compatibility support for deprecated fscrypt v1 policies. It implements the legacy AES-128-ECB per-file KDF, legacy process-subscribed keyring lookup, and v1 direct-key caching.

## Important APIs, Types, and Functions
- `find_and_lock_process_key()` searches subscribed process keyrings for a `logon` key with the fscrypt descriptor prefix and validates its `struct fscrypt_key` payload and minimum size.
- `struct fscrypt_direct_key` caches a prepared key for v1 `DIRECT_KEY` policies by superblock, descriptor, mode, and raw key bytes.
- `fscrypt_put_direct_key()` drops a direct-key ref and removes the cache entry when the last user exits.
- `find_or_insert_direct_key()` performs timing-conscious lookup by descriptor and uses `crypto_memneq()` to compare raw keys.
- `setup_v1_file_key_direct()` and `setup_v1_file_key_derived()` implement direct master-key use or legacy AES-derived per-file keys.
- `fscrypt_setup_v1_file_key()` and `fscrypt_setup_v1_file_key_via_subscribed_keyrings()` are the exported internal entry points.

## Control Flow
For v1 keys from the filesystem-level keyring, `keysetup.c` calls `fscrypt_setup_v1_file_key()` with raw master key bytes. If no filesystem-level key exists, `keysetup.c` may call `fscrypt_setup_v1_file_key_via_subscribed_keyrings()` as a legacy fallback, first using the standard fscrypt key prefix and optionally the filesystem's legacy prefix. Direct-key policies share a cached prepared transform; non-direct policies derive a per-file key by encrypting blocks of the master key with AES keyed by the file nonce.

## State and Persistence
The direct-key table is global in memory and keyed by descriptor hash buckets. Each `fscrypt_direct_key` stores the prepared key, descriptor, mode, raw key bytes for equality checks, superblock, and refcount. No new persistent state is written; v1 policies use the on-disk descriptor in the fscrypt context.

## Dependencies and Integration
This file depends on Linux `logon` key type, user key payloads, AES helper routines, Crypto API utility comparison, hash tables, spinlocks, and common key preparation in `keysetup.c`. It is isolated from v2 HKDF paths except through shared `fscrypt_inode_info` and prepared-key APIs.

## Risks and Edge Cases
- The legacy KDF is reversible if a derived key is compromised; comments explicitly direct new code to HKDF.
- Direct-key cache stores raw key bytes in memory until the cache entry is released, so sensitive freeing is required.
- Hashing by descriptor avoids timing leakage of raw key bytes but descriptor collisions require full checks.
- Process-subscribed keyrings have visibility/removal semantics that v2 filesystem-level keys were designed to replace.
- Payload size and minimum key-size checks must reject malformed logon keys before use.

## Test Signals
Test v1 key lookup through process keyrings, legacy prefix fallback, malformed payload rejection, too-short key rejection, direct-key cache reuse and release, non-direct AES-derived key setup, and compatibility with old v1 encrypted directories.
