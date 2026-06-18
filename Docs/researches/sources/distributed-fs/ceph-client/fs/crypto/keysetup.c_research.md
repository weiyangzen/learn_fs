# sources/distributed-fs/ceph-client/fs/crypto/keysetup.c

## Purpose
`keysetup.c` turns a validated fscrypt policy and master key into the actual runtime encryption key for an inode. It selects encryption modes, prepares Crypto API or blk-crypto keys, derives v2 subkeys, publishes `fscrypt_inode_info`, and cleans it up at inode eviction.

## Important APIs and Functions
- `fscrypt_modes[]` maps fscrypt mode numbers to names, Crypto API strings, key sizes, security strengths, IV sizes, and blk-crypto modes.
- `select_encryption_mode()` chooses contents mode for regular files and filenames mode for directories/symlinks.
- `fscrypt_allocate_skcipher()`, `fscrypt_prepare_key()`, `fscrypt_destroy_prepared_key()`, and `fscrypt_set_per_file_enc_key()` prepare and destroy runtime crypto keys.
- `setup_per_mode_enc_key()` derives and caches v2 per-mode keys for direct-key and IV_INO_LBLK policies.
- `fscrypt_derive_dirhash_key()` and `fscrypt_hash_inode_number()` derive SipHash-based directory and inode hash state.
- `fscrypt_setup_v2_file_key()` handles v2 key derivation strategies.
- `setup_file_encryption_key()` finds the master key, handles test-dummy and v1 fallback, validates key size, selects inline crypto, and sets up the file key.
- `fscrypt_get_encryption_info()`, `fscrypt_prepare_new_inode()`, `fscrypt_put_encryption_info()`, `fscrypt_free_inode()`, and `fscrypt_drop_inode()` are exported lifecycle helpers.

## Control Flow
For existing inodes, `fscrypt_get_encryption_info()` reads the on-disk context, converts it to a policy, validates support, then calls `fscrypt_setup_encryption_info()`. That allocates `fscrypt_inode_info`, picks a mode, computes data-unit bits, sets up keys, and publishes the pointer with `cmpxchg_release()` so racing threads share a single instance. For new inodes, `fscrypt_prepare_new_inode()` inherits the directory policy, generates a nonce, sets up key state before a filesystem transaction, and later `fscrypt_set_context()` persists the context.

## State and Persistence
Runtime inode state is stored in `fscrypt_inode_info` until eviction. It may own a per-file key, share a per-mode prepared key from the master key, or hold a legacy direct-key reference. If the key came from the filesystem-level keyring, the inode is linked into `mk_decrypted_inodes` and contributes an active master-key ref. Persistent context writing is delegated to `policy.c`/filesystem callbacks, except this file triggers setup before writes.

## Dependencies and Integration
It depends on Crypto API skcipher allocation, inline-crypto helpers, HKDF, SipHash, Linux random nonce generation, inode state, superblock fscrypt operations, keyring lookup, v1 setup, and policy conversion. Filesystems call its exported helpers during lookup/open/read/write/create/evict/drop_inode paths.

## Risks and Edge Cases
- Crypto API allocation masks intentionally avoid problematic async/offload drivers; missing algorithms return `-ENOPKG`.
- Per-mode key preparation is shared and protected by `fscrypt_mode_key_setup_mutex`; publication uses release/acquire barriers.
- Hardware-wrapped keys are valid only for v2 IV_INO_LBLK contents encryption with inline crypto.
- `fscrypt_get_encryption_info()` returns success for missing keys; callers must use `fscrypt_has_encryption_key()` or `fscrypt_require_key()`.
- New IV_INO_LBLK_32 inodes may lack an inode number until context setting, so inode hashing can be delayed.
- `fscrypt_drop_inode()` runs in atomic context and uses lockless `mk_present`, accepting benign races.

## Test Signals
Cover algorithm-missing paths, v1 and v2 key setup, missing-key behavior, racing concurrent setup, inline vs filesystem-layer selection, direct-key/per-file/per-mode derivations, encrypted new-inode creation and rollback cleanup, key removal causing inode eviction, dirty inode retention, and IV_INO_LBLK_32 delayed inode hash setup.
