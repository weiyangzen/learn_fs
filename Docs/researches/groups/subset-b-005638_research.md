# Research: subset-b-005638

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/fscrypt_private.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/fscrypt_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/hkdf.c -->
# sources/distributed-fs/ceph-client/fs/crypto/hkdf.c

## Purpose
`hkdf.c` implements fscrypt's HKDF-SHA512 extract and expand operations. It derives isolated subkeys from raw master keys or from software secrets derived by inline-crypto hardware for hardware-wrapped master keys.

## Important APIs, Types, and Functions
- `fscrypt_init_hkdf()` performs HKDF-Extract with an all-zero SHA-512-length salt, prepares an `hmac_sha512_key`, and zeroizes the pseudorandom key buffer.
- `fscrypt_hkdf_expand()` performs HKDF-Expand using the prepared HMAC key. It prefixes all info strings with `"fscrypt\0"` and a one-byte fscrypt context ID before appending caller-provided info and a counter.
- The context IDs are defined in `fscrypt_private.h`, including key identifiers, per-file encryption keys, direct keys, IV_INO_LBLK keys, dirhash keys, inode hash keys, and hardware-wrapped-key identifiers.

## Control Flow
Master-key add paths initialize `secret->hkdf` with `fscrypt_init_hkdf()`. Later key setup paths call `fscrypt_hkdf_expand()` to derive output material for key identifiers, per-file keys, per-mode keys, and SipHash keys. The expand loop emits full SHA-512 blocks directly into the output buffer and uses a temporary buffer only for the final partial block.

## State and Persistence
This file persists no external state. The prepared HKDF state is stored in `struct fscrypt_master_key_secret` while the master key is present. Intermediate PRK and temporary partial-output buffers are wiped with `memzero_explicit()`.

## Dependencies and Integration
It depends on kernel SHA-512 HMAC primitives from `crypto/sha2.h` and the private fscrypt context IDs. It is integrated by `keyring.c` for key identifiers and master-key initialization, `keysetup.c` for v2 subkeys and SipHash keys, and test dummy key generation.

## Risks and Edge Cases
- `fscrypt_hkdf_expand()` warns if output exceeds the RFC 5869 maximum of 255 hash blocks, but callers must still provide sensible lengths.
- Context byte uniqueness is security-critical; reusing a context/info combination across purposes would break key separation.
- No random salt is persisted, so the design assumes fscrypt master keys are already pseudorandom.
- The function is documented as thread-safe because it uses only stack HMAC contexts around an immutable prepared key.

## Test Signals
Test vectors can cover deterministic output for fixed master keys, distinct output across all fscrypt HKDF contexts, partial-block output zeroization paths, maximum-length warnings, and compatibility with key identifiers generated in `keyring.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/hkdf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/hooks.c -->
# sources/distributed-fs/ceph-client/fs/crypto/hooks.c

## Purpose
`hooks.c` provides exported fscrypt hooks that filesystems call from higher-level VFS operations. It enforces key availability, encrypted-tree policy consistency, no-key-name handling, symlink encryption/decryption, setattr restrictions, and casefold dirhash preparation.

## Important APIs and Functions
- `fscrypt_file_open()` requires the file key, then verifies the opened inode is permitted under its parent directory policy.
- `__fscrypt_prepare_link()` and `__fscrypt_prepare_rename()` reject no-key dentries and cross-directory moves that would violate encrypted-directory policy inheritance.
- `__fscrypt_prepare_lookup()` sets up encrypted filename handling and marks no-key dentries. `fscrypt_prepare_lookup_partial()` supports filesystems that implement filename encryption themselves.
- `__fscrypt_prepare_readdir()` sets up directory encryption info while allowing unsupported policies to behave like no-key access.
- `__fscrypt_prepare_setattr()` requires the key before size changes.
- `fscrypt_prepare_setflags()` derives a v2 dirhash key when enabling `FS_CASEFOLD_FL` on an encrypted directory.
- `fscrypt_prepare_symlink()`, `__fscrypt_encrypt_symlink()`, `fscrypt_get_symlink()`, and `fscrypt_symlink_getattr()` implement encrypted symlink sizing, encryption, no-key presentation, plaintext caching, and stat-size correction.

## Control Flow
Open begins with `fscrypt_require_key()` and then performs a cheap RCU parent check; only encrypted parents trigger the expensive parent dentry reference and policy comparison. Link and rename use dentry no-key flags as a proxy for unavailable directory keys, then call `fscrypt_has_permitted_context()` for policy enforcement. Symlink creation is two-stage: `fscrypt_prepare_symlink()` computes on-disk size before inode creation, then `__fscrypt_encrypt_symlink()` encrypts after `fscrypt_prepare_new_inode()` has prepared the symlink key.

## State and Persistence
The file updates dentry state via `fscrypt_prepare_dentry()`, initializes `ci_dirhash_key` in inode crypto info when casefolding is enabled, writes encrypted symlink bodies in the historical `fscrypt_symlink_data` format, and caches decrypted symlink targets in `inode->i_link`. It does not persist policies itself; it relies on policy and context helpers.

## Dependencies and Integration
It depends on filename helpers such as `fscrypt_setup_filename()`, `fscrypt_fname_encrypt()`, `fscrypt_fname_disk_to_usr()`, and `fscrypt_fname_alloc_buffer()`, policy helpers from `policy.c`, key setup from `keysetup.c`, and VFS dentry/inode APIs. Its exported symbols are used by fscrypt-enabled filesystems in open, lookup, link, rename, readdir, setattr, symlink, get_link, and getattr paths.

## Risks and Edge Cases
- Parent policy verification must run even for unencrypted children under encrypted parents to detect offline tampering.
- `RENAME_EXCHANGE` requires checking both swapped inodes against their target encrypted directories.
- Symlink ciphertext stores a redundant little-endian length and counts an extra terminator; max-length calculations must keep this historical format intact.
- `fscrypt_get_symlink()` must not cache no-key encoded targets because they become stale when the key is added later.
- Casefolded encrypted directories require v2 policies; v1 has no dirhash-key derivation.

## Test Signals
Test open/link/rename failures across mismatched encrypted policies, no-key lookup/delete behavior, symlink round trips with and without keys, symlink `st_size` matching visible target length, `FS_CASEFOLD_FL` rejection for v1 policies, and `RENAME_EXCHANGE` policy violations in both directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/inline_crypt.c -->
# sources/distributed-fs/ceph-client/fs/crypto/inline_crypt.c

## Purpose
`inline_crypt.c` implements fscrypt support for blk-crypto inline encryption, where encryption/decryption is handled by the block layer or hardware as part of bio processing rather than by filesystem-layer Crypto API transforms.

## Important APIs and Functions
- `fscrypt_select_encryption_impl()` decides whether an inode can use inline crypto based on file type, mode support, mount flag, IV method constraints, data-unit size, DUN byte width, and block-device support.
- `fscrypt_prepare_inline_crypt_key()` initializes a `blk_crypto_key`, starts using it on all filesystem block devices, and publishes it through `prep_key->blk_key`.
- `fscrypt_destroy_inline_crypt_key()` evicts a blk-crypto key from all devices and frees it.
- `fscrypt_derive_sw_secret()` asks inline-crypto hardware to derive a software secret from a hardware-wrapped key.
- `__fscrypt_inode_uses_inline_crypto()`, `fscrypt_set_bio_crypt_ctx()`, `fscrypt_mergeable_bio()`, `fscrypt_dio_supported()`, and `fscrypt_limit_io_blocks()` are the filesystem-facing I/O helpers.

## Control Flow
Key setup calls `fscrypt_select_encryption_impl()` before preparing the file key. If accepted, later preparation calls `fscrypt_prepare_inline_crypt_key()` instead of creating a skcipher transform. I/O submission calls `fscrypt_set_bio_crypt_ctx()` to generate a blk-crypto DUN from the fscrypt IV and attach the key to the bio. Filesystems call `fscrypt_mergeable_bio()` and `fscrypt_limit_io_blocks()` to avoid mixing keys or discontiguous DUN ranges.

## State and Persistence
Inline-crypto selection is cached in `ci->ci_inlinecrypt`. Prepared blk-crypto keys live in `fscrypt_prepared_key.blk_key`, either per-file or in per-mode arrays embedded in a master key. No new on-disk state is created here; DUNs are derived from policy flags, inode state, nonce, hashed inode number, and logical positions.

## Dependencies and Integration
The file depends on blk-crypto, block devices, superblock `s_cop->get_devices`, filesystem mount flag `SB_INLINECRYPT`, fscrypt IV generation, and fscrypt policy flags. It integrates with `keysetup.c` for key preparation and with filesystem bio/direct-I/O submission paths.

## Risks and Edge Cases
- Inline crypto is only selected for regular-file contents, never filename encryption.
- IV_INO_LBLK_32 with blocksize smaller than page size is excluded because some filesystems only check mergeability once per page.
- Hardware-wrapped contents keys require inline crypto; fallback to filesystem-layer crypto would expose an unusable wrapped key.
- Multi-device filesystems must support the selected blk-crypto configuration on every device returned by `get_devices()`.
- DIO support returns false on missing keys and requires inline crypto for encrypted files.
- `fscrypt_limit_io_blocks()` prevents 32-bit DUN wrap inside a bio for IV_INO_LBLK_32.

## Test Signals
Exercise mount with and without `inlinecrypt`, unsupported blk-crypto modes, multi-device rejection, IV_INO_LBLK_32 block-size restrictions, bio merge refusal across different keys/DUN discontinuities, hardware-wrapped-key support and rejection, DIO eligibility, and DUN wrap limiting near `U32_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/inline_crypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/keyring.c -->
# sources/distributed-fs/ceph-client/fs/crypto/keyring.c

## Purpose
`keyring.c` implements the filesystem-level fscrypt master-key keyring and the ioctls for adding, removing, and querying encryption keys. It also registers fscrypt-specific Linux key types and supports test-dummy keys.

## Important APIs, Types, and Functions
- `struct fscrypt_keyring` stores the per-superblock hash table of `fscrypt_master_key` objects.
- Lifetime helpers: `fscrypt_put_master_key()`, `fscrypt_put_master_key_activeref()`, `fscrypt_initiate_key_removal()`, and `fscrypt_destroy_keyring()`.
- Lookup and insertion: `allocate_filesystem_keyring()`, `fscrypt_find_master_key()`, `add_new_master_key()`, `add_existing_master_key()`, `do_add_master_key()`, and `add_master_key()`.
- User claim tracking: `allocate_master_key_users_keyring()`, `find_master_key_user()`, `add_master_key_user()`, and `remove_master_key_user()`.
- Ioctls: `fscrypt_ioctl_add_key()`, `fscrypt_ioctl_remove_key()`, `fscrypt_ioctl_remove_key_all_users()`, and `fscrypt_ioctl_get_key_status()`.
- Provisioning key support: `key_type_fscrypt_provisioning` and `get_keyring_key()` let userspace provide key material via a constrained keyring key.
- Test helpers: `fscrypt_get_test_dummy_key_identifier()` and `fscrypt_add_test_dummy_key()`.

## Control Flow
Adding a key validates the user argument, checks privileges for descriptor-based v1 keys, loads raw key material either directly or from an fscrypt-provisioning key, initializes HKDF and key identifiers for v2 keys, and inserts or revives the master key under `fscrypt_add_key_mutex`. Removing a key first removes the current user claim or all user claims, then transitions the master key from present to incompletely removed by wiping secret material and dropping the present active reference. If unlocked inodes remain, the code syncs the filesystem, prunes dentries for decrypted inodes, and reports busy-file status if eviction cannot complete.

## State and Persistence
Keyring state is per mounted superblock in `sb->s_master_keys`. Master-key objects track secret material, user claims, decrypted inodes, prepared per-mode keys, active refs, structural refs, and `mk_present`. The Linux keyring entries in `mk_users` represent which users have added a v2 key. No keys are persisted to disk by this code; userspace must re-add them after remount.

## Dependencies and Integration
The implementation depends on Linux keyrings, capabilities, RCU hash traversal, refcounting, key quotas, blk-crypto software-secret derivation for hardware-wrapped keys, HKDF, dcache/inode eviction, and fscrypt key setup. It is consumed by `keysetup.c`, `policy.c`, filesystem ioctl handlers, and unmount teardown.

## Risks and Edge Cases
- Active and structural refs intentionally mean different things; incorrect ref handling could leave removed keys in the hash table or free them while lookups race.
- `mk_present` is read locklessly in some paths and must be updated with `WRITE_ONCE()`.
- Removal can be incomplete if decrypted inodes remain busy; userspace must inspect status flags.
- Descriptor-based keys are privileged because descriptors are not cryptographic identifiers.
- Hardware-wrapped keys use a distinct key-identifier HKDF context to avoid collisions with raw software secrets.
- `mk_users->keys.nr_leaves_on_tree` is inspected under `mk_sem`; user-claim races must stay serialized.

## Test Signals
Use fscrypt ioctl tests for add/remove/status under one user and multiple users, descriptor privilege checks, provisioning-key type/flag mismatch, hardware-wrapped add paths, re-adding incompletely removed keys, busy inode status flags, unmount teardown, and KCSAN/lockdep coverage for RCU/refcount/keyring interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/keysetup.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/keysetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/keysetup_v1.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/keysetup_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/policy.c -->
# sources/distributed-fs/ceph-client/fs/crypto/policy.c

## Purpose
`policy.c` validates fscrypt policies, converts between UAPI policies and persisted contexts, implements policy ioctls, enforces encrypted-directory policy inheritance, writes new inode contexts, and parses test-dummy encryption mount options.

## Important APIs and Functions
- `fscrypt_policies_equal()`, `fscrypt_policy_to_key_spec()`, and `fscrypt_get_dummy_policy()` provide common policy utilities.
- `fscrypt_supported_policy()` dispatches to v1/v2 validation, including mode pairs, flags, casefold, direct-key, IV_INO_LBLK, stable inode, 32-bit inode, and data-unit-size checks.
- `fscrypt_new_context()` and `fscrypt_policy_from_context()` convert between in-memory policy and on-disk context.
- Ioctls: `fscrypt_ioctl_set_policy()`, `fscrypt_ioctl_get_policy()`, `fscrypt_ioctl_get_policy_ex()`, and `fscrypt_ioctl_get_nonce()`.
- `fscrypt_has_permitted_context()` enforces that encrypted directory trees contain only children with the same encryption policy.
- `fscrypt_policy_to_inherit()`, `fscrypt_context_for_new_inode()`, and `fscrypt_set_context()` support new inode creation.
- `fscrypt_parse_test_dummy_encryption()`, `fscrypt_dummy_policies_equal()`, and `fscrypt_show_test_dummy_encryption()` handle the testing mount option.

## Control Flow
Setting a policy copies the versioned policy from userspace, checks ownership/capability, obtains a write reference, locks the inode, and either sets a new policy on an empty live directory or returns `-EEXIST` if a different policy already exists. v2 policy setup verifies that the current user has added the requested key identifier. New inode creation later uses the inherited policy and nonce prepared by `keysetup.c`, builds a context, performs delayed IV_INO_LBLK_32 inode hashing if needed, and calls the filesystem `set_context()` callback.

## State and Persistence
This file is responsible for constructing the persisted fscrypt context bytes that store mode numbers, flags, key descriptor/identifier, data-unit size, reserved fields, and nonce. It also stores test-dummy policy state in the filesystem's mount option structure through caller-provided `fscrypt_dummy_policy`.

## Dependencies and Integration
It depends on filesystem fscrypt operations (`get_context`, `set_context`, `empty_dir`, `get_dummy_policy`, stable-inode queries, data-unit-size support), mount write coordination, inode ownership checks, keyring verification, random nonce generation, and key setup. Hooks and setup code call policy helpers to inherit, compare, and enforce contexts.

## Risks and Edge Cases
- v1 policies are still supported but warned as deprecated and rejected for casefolded directories.
- v2 flags `DIRECT_KEY`, `IV_INO_LBLK_64`, and `IV_INO_LBLK_32` are mutually exclusive.
- IV_INO_LBLK policies require stable 32-bit inode numbers and bounded data-unit-number width.
- `fscrypt_has_permitted_context()` permits two unrecognized policies to match for delete support, but otherwise fails closed on unexpected errors.
- `fscrypt_ioctl_set_policy()` has a gcc workaround when copying variable-size policies from userspace.
- `FS_IOC_GET_ENCRYPTION_NONCE` is explicitly for testing and exposes non-secret per-file nonce.

## Test Signals
Run ioctl coverage for set/get policy v1/v2, non-directory and non-empty directory rejection, policy mismatch returning `-EEXIST`, unsupported mode/flag/data-unit combinations, v2 key-not-added rejection, encrypted-tree child policy checks, context conversion round trips, IV_INO_LBLK capability gates, and test-dummy option conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/crypto/policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/d_path.c -->
# sources/distributed-fs/ceph-client/fs/d_path.c

## Purpose
`d_path.c` implements kernel helpers and the `getcwd` syscall path for converting dentries and mounts into printable path strings. It builds paths backwards into caller buffers while tolerating concurrent renames and mount changes.

## Important APIs, Types, and Functions
- `struct prepend_buffer` and helpers `prepend_char()`, `prepend_copy()`, `prepend()`, `prepend_name()`, and `extract_string()` manage reverse buffer construction and overflow reporting.
- `__prepend_path()` walks dentries and mounts up to a root and reports normal, absolute-root, detached, or escaped states.
- `prepend_path()` wraps the path walk with RCU and sequence retry handling for `rename_lock` and `mount_lock`.
- Public helpers include `__d_path()`, `d_absolute_path()`, `d_path()`, `dynamic_dname()`, `simple_dname()`, `dentry_path_raw()`, and `dentry_path()`.
- `SYSCALL_DEFINE2(getcwd)` implements the kernel side of `getcwd(2)`.

## Control Flow
The core algorithm starts at the target dentry and prepends `/name` components until it reaches the supplied root or a mount boundary. At mount roots it crosses to the parent mountpoint unless the mount is global root or detached. The optimistic RCU walk uses sequence counters; if rename or mount sequence validation fails, it retries under the relevant lock mode. `d_path()` first handles synthetic `d_dname` dentries, then uses the caller's current root and adds `" (deleted)"` for unlinked dentries.

## State and Persistence
This file does not persist state. It reads dentry names, parent pointers, mount parent/mountpoint pointers, current task root/pwd, and dentry deleted state. Outputs are transient strings placed at an offset inside the caller buffer.

## Dependencies and Integration
It depends on VFS dentry/mount internals, `fs_struct` sequence counters, RCU, seqcount helpers, safe kernel nofault copying, user-copy helpers, and syscall allocation helpers. Its exported functions are used by procfs, audit/logging, filesystem diagnostics, and callers that need stable textual paths.

## Risks and Edge Cases
- Name pointer and length can be mismatched during rename; `prepend_copy()` fills faulted regions with placeholder bytes and relies on sequence retry to discard bad output.
- Return pointers usually point inside the supplied buffer, not necessarily at its beginning.
- Deleted path suffixes are ambiguous by design.
- `__d_path()` returns `NULL` when unreachable from the supplied root; `d_absolute_path()` returns `-EINVAL` for detached/unreachable paths beyond allowed root behavior.
- Buffer overflow is tracked by setting `len` negative and returning `-ENAMETOOLONG`.
- `getcwd()` prepends `"(unreachable)"` if cwd is outside the process root.

## Test Signals
Exercise path generation under concurrent rename/mount movement, deleted dentries, synthetic `d_dname` dentries, detached mounts, unreachable cwd, too-small buffers, root path handling, and user-copy failures in `getcwd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/d_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dax.c -->
# sources/distributed-fs/ceph-client/fs/dax.c

## Purpose
`dax.c` implements filesystem Direct Access support for persistent memory and other DAX devices. It manages DAX XArray entries, entry locking/waiting, page-fault insertion, direct read/write through iomap, writeback flushing, truncate/invalidate behavior, CoW/unshare, zeroing, dedupe compare, and layout-break handling for busy pinned pages.

## Important APIs, Types, and Functions
- Entry encoding helpers: `dax_make_entry()`, `dax_to_pfn()`, `dax_to_folio()`, `dax_entry_order()`, `dax_is_pmd_entry()`, `dax_is_zero_entry()`, and `dax_is_empty_entry()`.
- Locking/waiting: `dax_entry_waitqueue()`, `get_next_unlocked_entry()`, `wait_entry_unlocked_exclusive()`, `dax_lock_entry()`, `dax_unlock_entry()`, and `put_unlocked_entry()`.
- Folio association: `dax_folio_reset_order()`, `dax_associate_entry()`, `dax_disassociate_entry()`, `dax_busy_page()`, `dax_lock_folio()`, and `dax_lock_mapping_entry()`.
- Mapping lifecycle: `grab_mapping_entry()`, `dax_layout_busy_page_range()`, `dax_break_layout()`, `dax_break_layout_final()`, `dax_delete_mapping_entry()`, `dax_delete_mapping_range()`, and `dax_invalidate_mapping_entry_sync()`.
- I/O and persistence: `dax_iomap_rw()`, `dax_iomap_iter()`, `dax_zero_range()`, `dax_truncate_page()`, `dax_file_unshare()`, `dax_writeback_mapping_range()`, and `dax_writeback_one()`.
- Fault handling: `dax_iomap_fault()`, `dax_iomap_pte_fault()`, optional `dax_iomap_pmd_fault()`, `dax_fault_iter()`, `dax_finish_sync_fault()`, and zero-hole loaders.
- Range operations: `dax_dedupe_file_range_compare()` and `dax_remap_file_range_prep()`.

## Control Flow
For faults, callers enter `dax_iomap_fault()` with the required filesystem locks. PTE or PMD handlers grab a locked mapping entry, obtain iomap mappings, handle holes with zero pages, obtain PFNs with `dax_iomap_direct_access()`, insert or update the DAX entry, copy around shared CoW data if needed, and insert PTE/PMD mappings or return `VM_FAULT_NEEDDSYNC` for synchronous faults. Direct I/O uses `dax_iomap_rw()` and `iomap_iter()` to copy directly between iterators and DAX kernel addresses. Writeback tags dirty entries, write-protects mappings, flushes cache lines to persistence, and clears dirty/writeback tags under entry locks.

## State and Persistence
DAX state is stored as value entries in `mapping->i_pages`; bits encode lock state, PMD size, zero page, and empty placeholder entries. `mapping->nrpages` tracks page-equivalent coverage. DAX folios are associated with mappings and indices or marked shared via `folio->mapping == NULL` and `folio->share`. Persistent data lives on the DAX device and is made durable by `dax_flush()` and fsync paths; this file manages CPU cache persistence rather than page cache contents.

## Dependencies and Integration
The file depends on XArray, iomap, DAX device direct-access APIs, MM fault insertion helpers, reverse-map and VMA interval trees, writeback controls, page/folio internals, memory-failure/rmap expectations, block error translation, and tracepoints in `trace/events/fs_dax.h`. Filesystems integrate through iomap ops, DAX address spaces, truncate/punch/remap paths, mmap fault handlers, and fsync/writeback.

## Risks and Edge Cases
- XArray value entries overlap with internal error encodings, so fault errors are returned as XArray internal VM_FAULT entries rather than ERR_PTRs.
- PMD/PTE conflicts favor existing PTE entries; zero/empty PMD entries can be downgraded, while real PMD mappings are retained and dirtied.
- Entry lock waiting must account for inode teardown, stale `xa_state`, and PMD-aligned waitqueue keys.
- Shared/CoW mappings require invalidating existing entries and copying head/tail data to avoid exposing stale bytes.
- Synchronous `MAP_SYNC` faults defer PTE/PMD insertion until fsync completes.
- Busy pinned DAX pages must be unmapped and waited on before layout changes; NOWAIT callers receive `-ERESTARTSYS`.
- Hardware poison recovery uses `DAX_RECOVERY_WRITE` for writes after `-EHWPOISON`.
- Many paths assume page-size filesystem block granularity, especially writeback.

## Test Signals
Exercise DAX read/write through iomap, sparse-hole reads, mmap PTE and PMD faults, PMD fallback conditions, MAP_SYNC faults and `dax_finish_sync_fault()`, dirty writeback and flush ordering, truncate/punch invalidation, busy page detection with GUP pins, CoW/shared extent copy-around, zero/truncate-page behavior, unshare, dedupe compare, hardware-poison recovery writes, and lockdep/KCSAN coverage for XArray entry locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dax.c -->
