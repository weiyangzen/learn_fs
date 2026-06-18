# Group Research: group_970_linux_stable_sources_os_linux_linux_stable_fs_crypto_fscrypt_private_a1d0c944f836

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/fscrypt_private.h -->
# File Research: sources/os/linux/linux-stable/fs/crypto/fscrypt_private.h

## Summary
Private fscrypt header defining the in-kernel data structures, constants, helper accessors, and internal interfaces used by Linux filesystem encryption. It ties together on-disk encryption contexts, in-memory policies, inode encryption state, prepared keys, IV construction, HKDF domain separation, filesystem master-key lifecycle, inline-crypto support, key setup, v1 compatibility, and policy handling.

## Main Responsibilities
- Define fscrypt context versions stored on disk: `fscrypt_context_v1`, `fscrypt_context_v2`, and `union fscrypt_context`.
- Define `union fscrypt_policy` and helpers for policy size, contents/filename modes, flags, and data-unit size.
- Define `struct fscrypt_inode_info`, the per-inode encryption state cached for encrypted files.
- Define `struct fscrypt_prepared_key`, supporting both Crypto API transforms and optional blk-crypto keys.
- Define fscrypt IV representation in `union fscrypt_iv`, including DIRECT_KEY nonce and DUN array views.
- Define HKDF context byte assignments for key identifiers, per-file keys, direct keys, IV_INO_LBLK keys, dirhash keys, and inode-hash keys.
- Define master-key secret and live master-key state structures, including active/structural refcount semantics.
- Declare internal APIs implemented by `crypto.c`, `fname.c`, `hkdf.c`, `inline_crypt.c`, `keyring.c`, `keysetup.c`, `keysetup_v1.c`, and `policy.c`.

## Key Data Structures
- `struct fscrypt_inode_info`: stores the prepared encryption key, ownership flags, inline-crypto flag, data-unit bits, hashed inode number, selected mode, inode/master-key backpointers, direct-key pointer, dirhash SipHash key, inherited policy, and file nonce.
- `struct fscrypt_master_key_secret`: stores HKDF state, key type, key size, and raw or hardware-wrapped key bytes while needed.
- `struct fscrypt_master_key`: filesystem-level master-key object with RCU keyring linkage, `mk_sem`, active and structural refs, user-claim keyring, decrypted-inode list, cached per-mode prepared keys, inode-hash key, and present/removal state.
- `struct fscrypt_mode`: maps fscrypt mode numbers to user-friendly names, Crypto API cipher strings, key sizes, security strengths, IV sizes, logging state, and blk-crypto mode numbers.

## Important Behavior
The header documents the master-key state machine: present, incompletely removed, and absent. Active refs keep a key in the filesystem keyring and preserve embedded prepared keys; structural refs only preserve the object memory. This distinction lets key removal wipe secrets immediately while keeping tracking state for decrypted inodes that are still cached.

`fscrypt_is_key_prepared()` uses acquire loads paired with release stores in the key-preparation paths. This is needed because per-mode prepared keys can be published concurrently and then reused by racing inodes.

The file explicitly undefines the UAPI `FSCRYPT_MAX_KEY_SIZE` for kernel code because hardware-wrapped keys make that raw-key-specific name misleading. Kernel internals instead use raw, hardware-wrapped, and maximum-any-key size constants.

## Research Notes
This is the fscrypt internal dependency hub. The central invariants are exact context/policy sizes, domain-separated HKDF labels, master-key refcount/lifecycle rules, and the split between inode-owned per-file keys, shared per-mode keys, legacy direct keys, and hardware-wrapped blk-crypto keys.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/fscrypt_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/hkdf.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/hkdf.c

## Summary
Implements fscrypt's HKDF-SHA512 support. It initializes reusable HKDF extract state from fscrypt master keys or hardware-derived software secrets, then expands that state into domain-separated subkeys and identifiers.

## Main Responsibilities
- Compute HKDF-Extract using HMAC-SHA512 with a zero salt.
- Prepare a reusable `hmac_sha512_key` for repeated HKDF-Expand operations.
- Expand key material with `fscrypt\0` plus a fscrypt-specific context byte prepended to the caller's info string.
- Zero temporary pseudorandom key and partial-block buffers after use.

## Key APIs
- `fscrypt_init_hkdf()`: computes the HKDF pseudorandom key from master key material and prepares the HMAC key schedule.
- `fscrypt_hkdf_expand()`: implements RFC 5869 HKDF-Expand, including previous-block chaining, counter bytes, and fscrypt's context prefix.

## Important Behavior
Fscrypt performs HKDF-Extract even though master keys are expected to be pseudorandom. This permits shorter master keys for modes that do not need SHA-512-length input while keeping KDF behavior uniform across modes.

HKDF-Expand prepends `fscrypt\0` and a one-byte context to every info string. This prevents accidental reuse between derived outputs such as key identifiers, per-file contents keys, direct keys, IV_INO_LBLK keys, dirhash keys, and inode-number hash keys.

## Research Notes
The file is small but security-critical. Correctness depends on all callers choosing unique context/info combinations; `fscrypt_private.h` centralizes the context byte assignments used here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/hkdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/hooks.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/hooks.c

## Summary
Implements VFS-facing fscrypt hooks for higher-level filesystem operations. It enforces key availability and policy consistency for open/link/rename/lookup/readdir/setattr/setflags, and handles encrypted symlink sizing, encryption, decryption or no-key presentation, caching, and `st_size` reporting.

## Main Responsibilities
- Require encryption keys before opening encrypted regular files.
- Enforce that encrypted directory trees do not contain children with incompatible policies.
- Reject hard links and renames involving no-key dentries or cross-policy moves.
- Prepare lookup/readdir operations that may proceed without keys for deletion-oriented workflows.
- Require the file key before size-changing `setattr`.
- Derive directory hash keys when enabling casefolding on encrypted v2-policy directories.
- Prepare encrypted symlink disk sizes and encrypt symlink targets.
- Return decrypted symlink targets when the key is present or no-key encoded targets when absent.
- Override encrypted symlink `st_size` with the size userspace actually sees.

## Key APIs
- `fscrypt_file_open()`
- `__fscrypt_prepare_link()`
- `__fscrypt_prepare_rename()`
- `__fscrypt_prepare_lookup()`
- `fscrypt_prepare_lookup_partial()`
- `__fscrypt_prepare_readdir()`
- `__fscrypt_prepare_setattr()`
- `fscrypt_prepare_setflags()`
- `fscrypt_prepare_symlink()`
- `__fscrypt_encrypt_symlink()`
- `fscrypt_get_symlink()`
- `fscrypt_symlink_getattr()`

## Important Behavior
`fscrypt_file_open()` first requires the target key, then uses a lightweight RCU parent check to avoid unnecessary parent dentry refcounting when the parent is unencrypted. It only takes a parent reference and compares policies when the parent may be encrypted.

Lookup preparation treats an unavailable key differently from a hard failure. No-key names are permitted for operations that allow deletion without a key, while link and rename reject no-key dentries with `-ENOKEY`.

Encrypted symlinks store a little-endian ciphertext length prefix for historical reasons and include a trailing NUL in the stored length even though the ciphertext does not semantically require one. Decrypted symlink targets are cached in `inode->i_link` with release semantics; no-key encodings are not cached because adding the key would make them stale.

## Research Notes
This file is the fscrypt enforcement layer closest to VFS operations. It relies on key setup from `keysetup.c`, policy comparison from `policy.c`, filename helpers, and the VFS symlink `i_link` cache contract.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/inline_crypt.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/inline_crypt.c

## Summary
Implements fscrypt integration with blk-crypto inline encryption. It selects inline encryption when policy, mode, mount options, data-unit size, key type, and all block devices support it; prepares and evicts blk-crypto keys; derives software secrets from hardware-wrapped keys; assigns bio crypto contexts; and checks mergeability, direct I/O support, and DUN wrap limits.

## Main Responsibilities
- Discover filesystem block devices through `s_cop->get_devices` or fall back to `sb->s_bdev`.
- Compute required DUN byte width for DIRECT_KEY, IV_INO_LBLK, and default IV strategies.
- Select inline encryption only for regular-file contents encryption with a blk-crypto-capable mode and `SB_INLINECRYPT`.
- Initialize `struct blk_crypto_key` objects and start using them on every filesystem block device.
- Evict blk-crypto keys from block devices and free them securely.
- Ask hardware to derive a software secret from a hardware-wrapped key for non-contents KDF use.
- Generate DUN arrays from fscrypt IVs and attach them to bios.
- Determine whether encrypted data can be merged into an existing bio.
- Report whether direct I/O is supported for an encrypted inode.
- Limit I/O block counts to avoid `IV_INO_LBLK_32` DUN wraparound within a bio.

## Key APIs
- `fscrypt_select_encryption_impl()`
- `fscrypt_prepare_inline_crypt_key()`
- `fscrypt_destroy_inline_crypt_key()`
- `fscrypt_derive_sw_secret()`
- `__fscrypt_inode_uses_inline_crypto()`
- `fscrypt_set_bio_crypt_ctx()`
- `fscrypt_mergeable_bio()`
- `fscrypt_dio_supported()`
- `fscrypt_limit_io_blocks()`

## Important Behavior
Inline encryption is selected only for regular-file contents, only if the mode maps to blk-crypto, only if the filesystem is mounted with `inlinecrypt`, and only if every backing block device supports the requested mode, data-unit size, DUN width, and key type.

For `IV_INO_LBLK_32`, inline encryption is disabled when filesystem block size differs from page size because some filesystem paths check crypto mergeability only for the first block in a page. Hardware-wrapped keys require inline encryption for file contents; if no suitable inline-crypto capability exists, setup fails.

Bio mergeability compares both crypto key pointer identity and DUN contiguity. `fscrypt_limit_io_blocks()` prevents rare DUN wrap cases from being submitted as one logically contiguous I/O.

## Research Notes
The core external dependency is the block layer's blk-crypto API. Filesystems must call `fscrypt_set_bio_crypt_ctx()` before adding pages and respect `fscrypt_mergeable_bio()` or equivalent DUN-contiguity limits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/inline_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/keyring.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/keyring.c

## Summary
Implements fscrypt filesystem-level master-key management and the related ioctls. It maintains per-superblock master keys, tracks users that added v2 keys, provisions keys from a dedicated Linux key type, supports hardware-wrapped keys and test dummy encryption, removes keys safely, evicts decrypted inodes when possible, and reports key status.

## Main Responsibilities
- Maintain `sb->s_master_keys`, a per-filesystem hash table of `fscrypt_master_key` objects.
- Manage active and structural references for master-key lifecycle.
- Register internal key types `.fscrypt` and `fscrypt-provisioning`.
- Add master keys through `FS_IOC_ADD_ENCRYPTION_KEY`.
- Remove current-user or all-user key claims through remove-key ioctls.
- Track v2 key ownership per user using a keyring under each master key.
- Derive v2 key identifiers with HKDF, using distinct contexts for raw and hardware-wrapped keys.
- Retrieve provisioning keys from Linux keyring entries.
- Generate and add per-boot random test dummy encryption keys.
- Evict dentries/inodes unlocked by removed keys and report busy files.
- Return absent, present, or incompletely removed key status.

## Key APIs
- `fscrypt_find_master_key()`
- `fscrypt_put_master_key()`
- `fscrypt_put_master_key_activeref()`
- `fscrypt_ioctl_add_key()`
- `fscrypt_ioctl_remove_key()`
- `fscrypt_ioctl_remove_key_all_users()`
- `fscrypt_ioctl_get_key_status()`
- `fscrypt_get_test_dummy_key_identifier()`
- `fscrypt_add_test_dummy_key()`
- `fscrypt_verify_key_added()`
- `fscrypt_init_keyring()`
- `fscrypt_destroy_keyring()`

## Important Behavior
Master keys can be present, incompletely removed, or absent. Removing a present key clears `mk_present`, wipes the secret, and drops the active ref associated with presence. If decrypted inodes still reference it, the object stays in the filesystem keyring in the incompletely removed state until those inodes are evicted or the key is re-added.

V2 policy keys are identified by cryptographic identifiers rather than arbitrary descriptors. Each user adding a v2 key gets a user-specific claim under `mk_users`; a normal remove ioctl removes only the current user's claim and removes the key itself only when no claims remain. The all-users ioctl requires `CAP_SYS_ADMIN`.

Hardware-wrapped key addition asks inline-crypto hardware for a software secret, initializes HKDF from that software secret, and derives the public key identifier using a hardware-wrapped-specific HKDF context. This prevents a raw key equal to a derived software secret from colliding with a wrapped key identifier.

Removal syncs the filesystem, prunes dentries for decrypted inodes, relies on `fscrypt_drop_inode()` to evict inodes once references drop, and reports `FILES_BUSY` when inodes remain. It returns success for useful progress while placing final state details in status flags.

## Research Notes
This file is the fscrypt key lifecycle authority. Correctness depends on `mk_sem`, the `s_master_keys` spinlock, RCU lookup, acquire/release publication of the filesystem keyring, active/structural ref transitions, keyring quota behavior, and cooperation with inode teardown in `keysetup.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/keysetup.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/keysetup.c

## Summary
Implements fscrypt key setup for encrypted inodes. It defines supported encryption modes, selects contents or filename encryption mode by inode type, prepares Crypto API or blk-crypto keys, derives per-file and per-mode keys, handles v2 policy KDFs and hardware-wrapped restrictions, publishes per-inode encryption info, prepares new encrypted inodes, and tears encryption state down during inode eviction/free/drop.

## Main Responsibilities
- Define `fscrypt_modes[]` for AES-XTS, AES-CBC-CTS, AES-CBC-ESSIV, SM4, Adiantum, and AES-HCTR2.
- Select contents encryption for regular files and filename encryption for directories/symlinks.
- Allocate and initialize synchronous skcipher transforms for filesystem-layer crypto.
- Prepare and destroy `fscrypt_prepared_key` objects.
- Derive shared per-mode keys for DIRECT_KEY and IV_INO_LBLK policies.
- Derive per-file keys for default v2 policies.
- Derive SipHash keys for casefolded directory hashes and inode-number hashing.
- Set up v2 file keys, including hardware-wrapped key constraints.
- Locate master keys in the filesystem keyring or fall back to legacy subscribed keyrings for v1 policies.
- Allocate, publish, and race-resolve `fscrypt_inode_info`.
- Prepare new encrypted inodes before filesystem transactions.
- Free inode encryption info and cached symlink targets.
- Tell VFS drop-inode logic to evict inodes whose master key has been removed.

## Key APIs
- `fscrypt_prepare_key()`
- `fscrypt_destroy_prepared_key()`
- `fscrypt_set_per_file_enc_key()`
- `fscrypt_derive_dirhash_key()`
- `fscrypt_hash_inode_number()`
- `fscrypt_get_encryption_info()`
- `fscrypt_prepare_new_inode()`
- `fscrypt_put_encryption_info()`
- `fscrypt_free_inode()`
- `fscrypt_drop_inode()`

## Important Behavior
Mode setup logs the actual Crypto API implementation the first time each mode is used, helping diagnose unexpected acceleration or fallback choices. It forbids weak keys through Crypto API flags and verifies transform IV sizes against fscrypt mode metadata.

Per-mode keys are shared under the master key and are protected by `fscrypt_mode_key_setup_mutex`; release/acquire publication lets racing tasks safely reuse them. V2 DIRECT_KEY and IV_INO_LBLK policies derive mode keys with HKDF rather than using master keys directly.

Hardware-wrapped keys are accepted only for v2 IV_INO_LBLK policies and require inline crypto for regular-file contents. The wrapped key is passed to blk-crypto for contents encryption, while the hardware-derived software secret is used for HKDF-derived non-contents material.

`fscrypt_setup_encryption_info()` publishes `fscrypt_inode_info` with `cmpxchg_release()` because multiple tasks can race to initialize an existing inode. The winner links the inode into the master key's decrypted-inode list and takes an active ref; losers clean up their temporary key material.

## Research Notes
This file is the bridge between policy/keyring state and per-inode usable encryption state. The main invariants are mode compatibility, KDF context separation, safe publication of shared keys and inode info, and accurate active-ref accounting for key removal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/keysetup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/keysetup_v1.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/keysetup_v1.c

## Summary
Implements compatibility key setup for original fscrypt v1 policies. It supports the legacy AES-128-ECB nonce-based per-file KDF, process-subscribed logon key lookup, and v1 DIRECT_KEY caching through a global direct-key table.

## Main Responsibilities
- Search current task subscribed keyrings for v1 `logon` keys with fscrypt or filesystem legacy prefixes.
- Validate legacy `struct fscrypt_key` payload size and minimum key length.
- Maintain a global hash table of prepared direct keys for v1 DIRECT_KEY policies.
- Prepare and refcount direct-key entries by descriptor, mode, and raw key bytes.
- Derive v1 per-file encryption keys using the file nonce as an AES-128 key over master-key blocks.
- Set up v1 file keys either directly or via derived per-file keys.

## Key APIs
- `fscrypt_put_direct_key()`
- `fscrypt_setup_v1_file_key()`
- `fscrypt_setup_v1_file_key_via_subscribed_keyrings()`

## Important Behavior
The direct-key table hashes by descriptor rather than raw key to avoid leaking secret key bytes through timing, then uses `crypto_memneq()` for constant-time raw-key comparison. Entries are scoped by superblock, descriptor, mode, and raw key and are freed when the refcount reaches zero.

The legacy v1 KDF encrypts master-key blocks with AES-128-ECB using the file nonce as the AES key. Comments explicitly note this method is nonstandard, non-extensible, and reversible if a derived key is compromised; new code should use v2 HKDF instead.

Subscribed-keyring lookup remains a fallback only for v1 policies and only after filesystem-level key lookup has failed, preventing process keyrings from overriding filesystem-level keys.

## Research Notes
This file exists to preserve v1 behavior while containing its risks. New fscrypt functionality such as v2 HKDF, per-user key claims, and hardware-wrapped keys intentionally does not route through this path.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/keysetup_v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/policy.c -->
# File Research: sources/os/linux/linux-stable/fs/crypto/policy.c

## Summary
Implements fscrypt policy validation, conversion between policy and on-disk context formats, policy ioctls, permitted-context checks, inheritance, context creation for new inodes, and test dummy encryption option parsing/display.

## Main Responsibilities
- Compare fscrypt policies by version-specific size.
- Convert policies to master-key specifiers.
- Validate v1 and v2 encryption mode combinations and flags.
- Enforce DIRECT_KEY, IV_INO_LBLK, casefold, stable-inode, 32-bit-inode, max-file-size, and sub-block data-unit constraints.
- Create on-disk fscrypt contexts from policies and nonces.
- Reconstruct policies from on-disk contexts.
- Get, set, and export encryption policies through ioctls.
- Export encryption nonces for testing.
- Enforce that encrypted directories contain only children with permitted matching policies.
- Determine the policy new children inherit from encrypted directories or dummy-encryption mounts.
- Write fscrypt contexts for newly prepared inodes.
- Parse, compare, and show `test_dummy_encryption` mount policies.

## Key APIs
- `fscrypt_policies_equal()`
- `fscrypt_policy_to_key_spec()`
- `fscrypt_get_dummy_policy()`
- `fscrypt_supported_policy()`
- `fscrypt_policy_from_context()`
- `fscrypt_ioctl_set_policy()`
- `fscrypt_ioctl_get_policy()`
- `fscrypt_ioctl_get_policy_ex()`
- `fscrypt_ioctl_get_nonce()`
- `fscrypt_has_permitted_context()`
- `fscrypt_policy_to_inherit()`
- `fscrypt_context_for_new_inode()`
- `fscrypt_set_context()`
- `fscrypt_parse_test_dummy_encryption()`
- `fscrypt_dummy_policies_equal()`
- `fscrypt_show_test_dummy_encryption()`

## Important Behavior
V1 policies are intentionally restricted to legacy mode combinations and only support padding plus DIRECT_KEY flags. They are rejected for casefolded directories because v1 has no way to derive the secret dirhash key.

V2 policies add AES-HCTR2 filename mode pairing, SM4 pairings, IV_INO_LBLK flags, and configurable data-unit sizes. Mutually exclusive flags are rejected. IV_INO_LBLK policies require AES-256-XTS contents mode, filesystem-stable inode numbers, 32-bit inode numbers, and file data-unit indices that fit in 32 bits.

Setting a v2 policy verifies that the current user has added the referenced master key, unless overridden by `CAP_FOWNER`. Setting a v1 policy emits a warning recommending v2. Setting a policy is allowed only on an owned/capable empty directory that does not already have a different policy.

`fscrypt_has_permitted_context()` allows deletion of children when both parent and child have unrecognized policies, but otherwise requires matching policies under encrypted parents and forbids unencrypted children in encrypted directories.

## Research Notes
This file is the policy gatekeeper. It separates syntactic context conversion from semantic support checks, and it enforces the filesystem properties required for IV schemes that depend on inode numbers or data-unit geometry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/crypto/policy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/d_path.c -->
# File Research: sources/os/linux/linux-stable/fs/d_path.c

## Summary
Implements kernel pathname string construction helpers and the `getcwd` syscall. It builds paths backward into caller buffers under RCU/sequence protection, handles concurrent rename and mount changes, supports synthetic dentry names, reports deleted or unreachable paths, and exports raw dentry path helpers.

## Main Responsibilities
- Provide a backward-growing `prepend_buffer` abstraction for path assembly.
- Safely copy dentry names that may race with rename using nofault kernel copies.
- Walk dentry and mount parent chains to construct paths relative to a root.
- Retry path construction under `rename_lock` and `mount_lock` sequence counters when races are detected.
- Implement `__d_path()`, `d_absolute_path()`, and exported `d_path()`.
- Support synthetic filesystem names through `dentry_operations::d_dname`.
- Provide `dynamic_dname()` and `simple_dname()` helpers for synthetic dentry naming.
- Implement raw and deleted-aware dentry path helpers.
- Implement `getcwd`, including unreachable path handling.

## Key APIs
- `__d_path()`
- `d_absolute_path()`
- `d_path()`
- `dynamic_dname()`
- `simple_dname()`
- `dentry_path_raw()`
- `dentry_path()`
- `SYSCALL_DEFINE2(getcwd)`

## Important Behavior
Path strings are prepended from the end of the supplied buffer. On overflow, the helpers preserve a suffix where possible and mark the buffer as failed so callers return `-ENAMETOOLONG`.

`prepend_name()` uses acquire loading for the name pointer and `READ_ONCE()` for length. Because pointer and length can be inconsistent during concurrent rename, `prepend_copy()` uses `copy_from_kernel_nofault()` and fills with `x` on fault; the sequence retry later discards raced output.

`prepend_path()` first attempts an RCU/sequence-count walk and falls back to locked sequence retry when rename or mount sequence counters require it. It distinguishes paths that reach the supplied root, absolute root, detached/not-yet-attached mounts, and escaped dentries.

`d_path()` appends `" (deleted)"` for unlinked dentries and delegates to `d_dname` for synthetic names unless the synthetic dentry is the mounted root. `getcwd` returns `(unreachable)` when the process working directory is outside its root.

## Research Notes
This file is concurrency-heavy VFS utility code. Its key invariants are dentry lifetime under RCU, race detection through global rename/mount sequence counters, safe handling of unstable names, and caller awareness that returned strings may start inside the provided buffer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/d_path.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dax.c -->
# File Research: sources/os/linux/linux-stable/fs/dax.c

## Summary
Implements filesystem DAX support for page-cache-like exceptional entries, direct persistent-memory I/O, DAX mmap faults, writeback/cache flushing, layout breaking, zeroing/truncation, unshare/CoW handling, dedupe comparison, and remap preparation. It uses XArray value entries to represent locked/empty/zero/real DAX mappings at PTE or PMD granularity.

## Main Responsibilities
- Define and manage DAX XArray entry encoding for lock state, PMD size, zero pages, and empty placeholders.
- Provide wait queues and locking helpers for DAX exceptional entries.
- Associate and disassociate DAX folios with address spaces, including shared-folio tracking.
- Reset compound DAX folios to order-0 state when mappings are removed.
- Lock DAX entries by folio or mapping/index for memory-management users.
- Grab or create locked mapping entries, including PMD-to-PTE downgrade behavior.
- Detect busy pinned DAX pages before layout changes.
- Invalidate/delete DAX entries and clear dirty/writeback tags.
- Break DAX layouts by unmapping mappings, waiting for DMA/pins, and deleting entries.
- Copy around unaligned writes and CoW edges.
- Implement DAX reads/writes through iomap and direct persistent-memory access.
- Handle PTE and PMD DAX faults, holes, zero pages, synchronous faults, CoW faults, and write faults.
- Flush dirty DAX ranges to the persistent domain for data-integrity writeback.
- Support DAX zeroing, truncate-page zeroing, file unshare, dedupe comparison, and remap prep.

## Key APIs
- `dax_folio_reset_order()`
- `dax_lock_folio()` / `dax_unlock_folio()`
- `dax_lock_mapping_entry()` / `dax_unlock_mapping_entry()`
- `dax_layout_busy_page_range()` and `dax_layout_busy_page()`
- `dax_delete_mapping_entry()` and `dax_delete_mapping_range()`
- `dax_break_layout()` and `dax_break_layout_final()`
- `dax_invalidate_mapping_entry_sync()`
- `dax_file_unshare()`
- `dax_zero_range()` and `dax_truncate_page()`
- `dax_iomap_rw()`
- `dax_iomap_fault()`
- `dax_finish_sync_fault()`
- `dax_dedupe_file_range_compare()`
- `dax_remap_file_range_prep()`
- `dax_writeback_mapping_range()`

## Important Behavior
DAX entries are XArray value entries, not normal page-cache pages. Four low bits encode locked, PMD, zero-page, and empty-entry state; the remaining bits carry the PFN. Entry locking is serialized through the mapping XArray lock plus hashed wait queues keyed by XArray and aligned entry start.

PTE entries are favored over PMD entries. PMD zero or empty entries can be downgraded when a PTE entry is needed. Real PMD storage entries are not evicted merely to upgrade/downgrade; PTE writes can dirty the whole PMD entry as appropriate.

DAX folio association tracks whether a persistent-memory folio belongs to one mapping or has become shared across mappings. Shared folios clear `mapping` and use `share`; removal decrements sharing, resets compound state, restores pgmap pointers, and verifies sub-folio refcounts.

Layout breaking first unmaps mappings to stop new fast GUP pins, scans DAX entries for busy pages, waits for pins/DMA when a callback is supplied, and deletes mapping entries once no busy page remains. NOWAIT callers can pass no callback and receive `-ERESTARTSYS` on the first busy page.

Fault handling uses iomap to resolve storage. Read faults on holes install zero pages; write faults allocate or CoW real storage; `MAP_SYNC` synchronous faults can return `VM_FAULT_NEEDDSYNC` with a PFN for later insertion after `fsync`. PMD faults fall back unless alignment, VMA range, EOF, and CoW constraints are satisfied.

Writeback tags DAX entries to write, write-protects all VMAs mapping the PFN range, flushes CPU caches to the persistent domain, then clears dirty tags while holding the entry lock so concurrent faults cannot dirty the same PFN between protection and flush completion.

## Research Notes
This file is a central coordination layer among iomap, XArray, MM faults, ZONE_DEVICE pages, persistent-memory flushing, GUP/DMA exclusion, and filesystem layout changes. The most important invariants are locked-entry wakeups, dirty/writeback tag ordering, PMD/PTE granularity rules, folio sharing metadata, and caller-provided filesystem locking around faults, truncate, punch hole, and direct I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dax.c -->