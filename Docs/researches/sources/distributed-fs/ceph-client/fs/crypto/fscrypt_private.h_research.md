# sources/distributed-fs/ceph-client/fs/crypto/fscrypt_private.h

## Purpose
`fscrypt_private.h` is the internal contract for the fscrypt implementation. It defines on-disk encryption contexts, in-memory inode and master-key state, crypto mode descriptors, HKDF context IDs, and private helper prototypes shared by the fscrypt source files in `fs/crypto/`.

## Important APIs, Types, and Functions
- On-disk formats: `struct fscrypt_context_v1`, `struct fscrypt_context_v2`, and `union fscrypt_context` model the persisted per-inode encryption context. Helpers `fscrypt_context_size()`, `fscrypt_context_is_valid()`, and `fscrypt_context_nonce()` centralize version-aware parsing.
- Policy view: `union fscrypt_policy` wraps UAPI v1/v2 policies. `fscrypt_policy_size()`, `fscrypt_policy_contents_mode()`, `fscrypt_policy_fnames_mode()`, `fscrypt_policy_flags()`, and `fscrypt_policy_du_bits()` provide version-aware accessors.
- Runtime key state: `struct fscrypt_inode_info` is attached to inodes once an encryption key is available. It stores prepared crypto material, the selected mode, policy, nonce, master-key back pointer, direct-key reference, inline-crypto flag, data-unit bits, inode hash, and optional SipHash dirhash key.
- Prepared keys: `struct fscrypt_prepared_key` can hold either a Crypto API `crypto_sync_skcipher` transform or, when inline crypto is enabled, a `blk_crypto_key`.
- Master-key state: `struct fscrypt_master_key_secret` stores master key material, HKDF state, key size, and hardware-wrapped status. `struct fscrypt_master_key` stores the keyring entry, user keyring, active/structural refs, decrypted inode list, per-mode prepared keys, inode-hash key, and present/incompletely-removed/absent status.
- IV representation: `union fscrypt_iv` supports raw byte IVs and blk-crypto DUN arrays. `fscrypt_max_file_dun_bits()` computes the maximum data-unit-number bit width from filesystem maxbytes and data-unit size.
- Cross-file APIs are declared for HKDF, inline crypto, keyring, key setup, v1 setup, and policy conversion/validation.

## Control Flow and Integration
The header is included by the implementation files and defines the common handoff sequence: policy/context parsing in `policy.c`, key discovery in `keyring.c`, key setup in `keysetup.c`, optional v1 compatibility in `keysetup_v1.c`, optional blk-crypto in `inline_crypt.c`, and VFS operation guards in `hooks.c`. Filesystems integrate through `super_block->s_cop` callbacks, inode fscrypt pointers, and exported fscrypt helpers.

## State and Persistence
Persistent state is the versioned fscrypt context stored by filesystems, including algorithm modes, flags, key descriptor/identifier, optional data-unit size, and per-file nonce. In-memory state lives in `fscrypt_inode_info` until inode eviction and in `fscrypt_master_key` until all active and structural refs are dropped. Master keys can be present, incompletely removed while unlocked inodes remain, or absent. Secret material is explicitly zeroized when no longer needed.

## Dependencies
The header depends on kernel fscrypt UAPI definitions, SHA-512 HMAC helpers, SipHash, blk-crypto, inode/superblock state, Linux keyrings, lists, refcounts, RCU, and Crypto API types. Compile-time behavior changes under `CONFIG_FS_ENCRYPTION_INLINE_CRYPT`.

## Risks and Edge Cases
- Context and policy sizes must stay synchronized with UAPI layout; the header uses build-time checks for context sizes.
- Version-specific accessors call `BUG()`/`WARN_ON_ONCE()` if used on unvalidated objects.
- Concurrent publication of prepared keys and inode crypto info relies on release/acquire barriers defined here and implemented in setup files.
- Hardware-wrapped keys are represented alongside raw keys but have different maximum sizes and KDF behavior.
- Master-key refs distinguish object lifetime from active key usability; misuse can leak keys or prematurely destroy prepared subkeys.

## Test Signals
Useful signals include fscrypt ioctl tests for v1/v2 policies, unsupported context sizes, key add/remove/re-add lifecycle, inline-crypto and non-inline builds, hardware-wrapped-key rejection paths, casefolded encrypted directory dirhash setup, and KASAN/KCSAN coverage around refcount and release/acquire publication.
