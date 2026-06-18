# Group Research: group_728_linux_sources_os_linux_linux_fs_crypto_fscrypt_private_h_sources_os__4233e75e3920

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/fscrypt_private.h -->
# File Research: sources/os/linux/linux/fs/crypto/fscrypt_private.h

## Summary
Private fscrypt header defining the in-kernel representations, constants, helper accessors, and internal function interfaces used by Linux filesystem encryption. It bridges UAPI policies/contexts, inode encryption state, master-key state, crypto mode metadata, HKDF contexts, inline-crypto integration, keyring management, key setup, v1 compatibility, and policy operations.

## Main Responsibilities
- Define fscrypt context versions stored on disk: `fscrypt_context_v1`, `fscrypt_context_v2`, and `union fscrypt_context`.
- Define in-kernel policy wrapper `union fscrypt_policy` and helpers for policy size, modes, flags, and data-unit size.
- Define per-inode encryption state in `struct fscrypt_inode_info`.
- Define prepared-key state in `struct fscrypt_prepared_key`, supporting Crypto API transforms and optional blk-crypto keys.
- Define IV layout via `union fscrypt_iv`, including file data-unit index and DIRECT_KEY nonce use.
- Define HKDF context labels that domain-separate fscrypt KDF outputs.
- Define master-key secret and live master-key state structures.
- Declare internal APIs implemented across `crypto.c`, `fname.c`, `hkdf.c`, `inline_crypt.c`, `keyring.c`, `keysetup.c`, `keysetup_v1.c`, and `policy.c`.

## Key Data Structures
- `struct fscrypt_inode_info`: cached key material and policy for an inode, including selected mode, nonce, data-unit size, master-key backpointer, direct-key pointer, directory SipHash key, and inline-crypto flag.
- `struct fscrypt_master_key_secret`: KDF state, raw or hardware-wrapped key bytes, size, and hardware-wrapped flag.
- `struct fscrypt_master_key`: filesystem-level master key object with active/structural refs, present/removal state, per-user keyring, decrypted inode list, cached per-mode keys, and inode-hash key.
- `struct fscrypt_mode`: maps fscrypt mode numbers to friendly names, Crypto API cipher strings, key sizes, security strength, IV size, logging state, and blk-crypto mode numbers.

## Important Behavior
The header documents the master-key state model: `PRESENT`, `INCOMPLETELY_REMOVED`, and `ABSENT`. Active refs keep a key in the filesystem keyring and keep prepared subkeys alive; structural refs keep the object memory alive. This distinction is central to safe key removal while decrypted inodes may still be cached.

`fscrypt_is_key_prepared()` uses acquire loads paired with release stores in key preparation paths, because per-mode keys can be published concurrently. Inline crypto is abstracted so non-inline builds compile to stubs that reject hardware-wrapped keys and use Crypto API transforms.

The file also intentionally undefines misleading `FSCRYPT_MAX_KEY_SIZE` for kernel code, replacing it with raw, hardware-wrapped, and maximum-any-key size constants.

## Research Notes
This header is the dependency hub for fscrypt internals. The most important invariants are context/policy version sizing, domain-separated HKDF labels, master-key lifecycle/refcount rules, and the separation between inode-owned per-file keys, shared per-mode keys, and legacy direct keys.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/fscrypt_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/hkdf.c -->
# File Research: sources/os/linux/linux/fs/crypto/hkdf.c

## Summary
Implements fscrypt’s HKDF-SHA512 support. It provides HKDF-Extract initialization for master keys or hardware-derived software secrets, and HKDF-Expand for deriving domain-separated fscrypt subkeys and identifiers.

## Main Responsibilities
- Initialize an `hmac_sha512_key` from master key material with HKDF-Extract.
- Expand the prepared HKDF key into output key material for specific fscrypt contexts.
- Prefix HKDF info strings with `fscrypt\0` and a context byte to prevent cross-purpose reuse.

## Key APIs
- `fscrypt_init_hkdf()`: computes PRK using HMAC-SHA512 with a zero salt, prepares reusable HMAC state, and zeroizes the temporary PRK.
- `fscrypt_hkdf_expand()`: implements RFC 5869 HKDF-Expand with SHA-512, supporting arbitrary output length up to the HKDF limit and wiping temporary partial-block output.

## Important Behavior
Fscrypt always performs HKDF-Extract even though master keys should already be pseudorandom. This permits shorter master keys for modes that do not require a full SHA-512-length input and keeps the KDF behavior uniform.

HKDF-Expand uses prior block chaining for multi-block output, appends a counter byte, and includes the fscrypt-specific prefix and context byte before caller-provided info. This design isolates derived outputs such as key identifiers, per-file keys, direct keys, dirhash keys, IV_INO_LBLK keys, and inode hash keys.

## Research Notes
This file is small but security-critical. The main correctness property is that every caller must use a unique context/info combination, and `fscrypt_private.h` centralizes those context IDs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/hkdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/hooks.c -->
# File Research: sources/os/linux/linux/fs/crypto/hooks.c

## Summary
Implements fscrypt hooks used by higher-level filesystem operations. It enforces key availability and policy consistency for open/link/rename/lookup/setattr/setflags, and handles encrypted symlink sizing, encryption, decryption/no-key presentation, and `st_size` reporting.

## Main Responsibilities
- Require encryption keys before opening encrypted regular files.
- Enforce that encrypted directory trees do not contain children with incompatible policies.
- Prepare link and rename operations, rejecting no-key names and cross-policy moves.
- Prepare lookup/readdir paths that may need to operate without keys.
- Prepare size-changing setattr operations by requiring the file key.
- Support casefold flag changes on encrypted directories by deriving dirhash keys.
- Prepare, encrypt, read, cache, and stat encrypted symlink targets.

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
`fscrypt_file_open()` first requires the target key, then cheaply checks under RCU whether the parent is unencrypted. Only if needed does it take a parent dentry reference and compare policies. This avoids expensive parent refcounting for the common unencrypted-parent case.

Lookup preparation distinguishes “key unavailable” from hard failure. No-key names are allowed for deletion-oriented operations, but link and rename reject them with `-ENOKEY`.

Encrypted symlinks store a little-endian ciphertext length prefix for historical reasons and count a trailing NUL in the stored length even though ciphertext does not semantically need one. `fscrypt_get_symlink()` decrypts when the key exists, otherwise returns the no-key encoded target. Decrypted targets are cached in `inode->i_link` with release semantics; no-key encodings are not cached because they become stale when the key is added.

## Research Notes
This file is the VFS-facing enforcement layer. It depends on policy comparison from `policy.c`, key setup from `keysetup.c`, filename encryption helpers, and the inode `i_link` cache behavior expected by path lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/inline_crypt.c -->
# File Research: sources/os/linux/linux/fs/crypto/inline_crypt.c

## Summary
Implements fscrypt integration with blk-crypto inline encryption. It decides whether a regular file can use inline encryption, prepares and evicts blk-crypto keys, derives software secrets from hardware-wrapped keys, assigns bio crypto contexts, checks bio mergeability, gates direct I/O support, and limits I/O to avoid data-unit-number wraparound.

## Main Responsibilities
- Discover block devices used by a filesystem, using `s_cop->get_devices` when available.
- Compute the number of DUN bytes required by the inode’s IV generation policy.
- Select inline encryption when the file, mode, mount options, policy, data-unit size, and all block devices support it.
- Initialize `struct blk_crypto_key` objects and start using them on all filesystem block devices.
- Evict blk-crypto keys during prepared-key destruction.
- Ask inline-encryption hardware to derive software secrets from hardware-wrapped keys.
- Generate DUN arrays from fscrypt IVs and attach them to bios.
- Determine whether a bio can merge additional encrypted data.
- Report whether encrypted DIO is supported for an inode.
- Limit I/O block counts for `IV_INO_LBLK_32` DUN wraparound.

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
Inline encryption is selected only for regular-file contents encryption, only when the fscrypt mode has a blk-crypto equivalent, and only when the filesystem is mounted with `SB_INLINECRYPT`. For `IV_INO_LBLK_32`, inline encryption is disabled when filesystem block size differs from page size because some filesystem code only checks mergeability for the first block in a page.

Hardware-wrapped keys require inline encryption for file contents. The software secret derived from hardware is used for non-contents KDF needs, while the wrapped key itself is passed to blk-crypto for actual contents encryption.

Bio mergeability compares both crypto key pointer identity and DUN contiguity. `fscrypt_limit_io_blocks()` handles the rare case where `IV_INO_LBLK_32` would wrap within a logically contiguous I/O.

## Research Notes
The core dependency is the block layer’s blk-crypto API. Correctness depends on each filesystem calling `fscrypt_set_bio_crypt_ctx()` before adding pages and honoring `fscrypt_mergeable_bio()` or equivalent DUN-contiguity limits.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/inline_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/keyring.c -->
# File Research: sources/os/linux/linux/fs/crypto/keyring.c

## Summary
Implements fscrypt filesystem-level master-key management and the related ioctls. It stores master keys per superblock, tracks which users added v2 keys, supports provisioning keys from the Linux keyrings service, handles hardware-wrapped key setup, supports test dummy encryption, removes keys safely, evicts decrypted inodes when possible, and reports key status.

## Main Responsibilities
- Maintain `sb->s_master_keys`, a per-filesystem hash table of `fscrypt_master_key` objects.
- Manage active and structural references for master-key lifecycle.
- Register and use internal key types `.fscrypt` and `fscrypt-provisioning`.
- Add master keys via `FS_IOC_ADD_ENCRYPTION_KEY`.
- Remove current-user or all-user key claims via remove-key ioctls.
- Track v2 key ownership per user using an internal keyring under each master key.
- Derive key identifiers with HKDF, including distinct raw-key and hardware-wrapped-key contexts.
- Retrieve keys from `fscrypt-provisioning` Linux keyring entries.
- Add and identify per-boot random test dummy keys.
- Evict dentries/inodes unlocked with a removed key and report busy files.
- Report present, absent, or incompletely removed key state.

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
Master keys can be present, incompletely removed, or absent. Removing a present key wipes its secret and drops the active ref associated with `mk_present`. If decrypted inodes still reference it, the object remains in the filesystem keyring in an incompletely removed state until those inodes are evicted or the key is re-added.

V2 policy keys are identified by cryptographic identifiers rather than arbitrary descriptors. Each user adding a v2 key gets a user-specific internal key under `mk_users`; a user cannot remove the key itself while other users still have claims unless using the privileged all-users ioctl.

Adding a hardware-wrapped key derives a software secret through inline-encryption hardware, initializes HKDF from that software secret, and uses a separate HKDF context for the key identifier to keep raw and wrapped-key identifiers distinct.

Removal first clears user claims, then initiates key removal if no claims remain. It syncs the filesystem, prunes dentries for decrypted inodes, relies on `fscrypt_drop_inode()` to evict inodes when refs drop, and reports `FILES_BUSY` if inodes remain.

## Research Notes
This file is the fscrypt key lifecycle authority. Correctness depends on `mk_sem`, `s_master_keys->lock`, RCU lookup, active/struct refcount transitions, keyring quota behavior, and cooperation with inode teardown in `keysetup.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/keysetup.c -->
# File Research: sources/os/linux/linux/fs/crypto/keysetup.c

## Summary
Implements fscrypt key setup for encrypted inodes. It selects encryption modes, allocates Crypto API transforms or blk-crypto keys, derives per-file and per-mode keys, handles v2 policy KDFs, initializes per-inode encryption info, prepares new encrypted inodes, and tears encryption info down during inode eviction/free/drop.

## Main Responsibilities
- Define supported fscrypt modes and their cipher strings, key sizes, IV sizes, security strengths, and blk-crypto mappings.
- Select contents or filename encryption mode based on inode type.
- Allocate and initialize Crypto API skcipher transforms.
- Prepare and destroy `fscrypt_prepared_key` objects.
- Derive shared per-mode keys with HKDF for DIRECT_KEY and IV_INO_LBLK policies.
- Derive per-file keys with HKDF for standard v2 policies.
- Derive SipHash keys for casefolded directory hashes and inode-number hashing.
- Set up v2 keys, including hardware-wrapped key restrictions.
- Find master keys and fall back to legacy v1 subscribed keyrings when needed.
- Allocate, publish, and race-resolve `fscrypt_inode_info`.
- Prepare new encrypted inodes before filesystem transactions.
- Free inode encryption info and cached symlink targets.
- Tell the VFS to drop inodes whose master key was removed.

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
Per-mode prepared keys are shared under a global setup mutex and published with release stores so concurrent inodes can acquire them safely. Standard v2 policies derive per-file encryption keys from master-key HKDF and the inode nonce. DIRECT_KEY v2 derives per-mode keys rather than reusing master keys directly. `IV_INO_LBLK_64` and `IV_INO_LBLK_32` derive per-mode keys with filesystem UUID in HKDF info.

`IV_INO_LBLK_32` also derives an inode-hash SipHash key on demand. Existing inodes hash immediately; new inodes may not have an inode number yet, so hashing can be delayed until `fscrypt_set_context()`.

`fscrypt_get_encryption_info()` treats missing keys as a nonfatal result and requires callers to check `fscrypt_has_encryption_key()`. It can also treat unsupported contexts or algorithms as nonfatal when operations need to proceed for deletion.

Publishing `fscrypt_inode_info` uses `cmpxchg_release()` because multiple tasks can race to set up the same existing inode. The winner links the inode into the master key’s decrypted-inode list and takes an active key ref.

## Research Notes
This file is the central bridge between policy, master-key storage, and actual per-inode encryption capability. Its key invariants are KDF context selection, master-key size validation, safe publication of shared keys and inode info, and cleanup coordination with key removal.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/keysetup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/keysetup_v1.c -->
# File Research: sources/os/linux/linux/fs/crypto/keysetup_v1.c

## Summary
Implements compatibility support for legacy fscrypt v1 encryption policies. It supports the original AES-128-ECB-based per-file KDF, process-subscribed keyring lookup, and legacy DIRECT_KEY handling through a global direct-key table.

## Main Responsibilities
- Search current task subscribed keyrings for legacy `logon` keys by descriptor.
- Validate legacy key payload size and minimum key size.
- Derive v1 per-file keys using the historical AES-ECB KDF.
- Support v1 DIRECT_KEY by preparing and sharing direct master-key transforms.
- Maintain a hash table of direct keys keyed by descriptor and mode, while comparing raw key bytes with constant-time comparison.
- Fall back to filesystem legacy key prefixes when provided.

## Key APIs
- `fscrypt_setup_v1_file_key()`
- `fscrypt_setup_v1_file_key_via_subscribed_keyrings()`
- `fscrypt_put_direct_key()`

## Important Behavior
Legacy v1 non-DIRECT_KEY derivation encrypts chunks of the raw master key using AES-128-ECB with the inode nonce as the AES key. The file comments explicitly call this nonstandard, nonextensible, uneven in entropy distribution, and reversible if a derived key is compromised.

For DIRECT_KEY, the file uses a global `fscrypt_direct_keys` table so files sharing the same descriptor, mode, and raw key can share a prepared key. The hash table does not key by raw key to avoid leaking secret-dependent timing through hashing; raw keys are compared with `crypto_memneq()`.

Process-subscribed keyring lookup is intentionally legacy fallback and should not override filesystem-level keys.

## Research Notes
This is compatibility code for deprecated v1 policy behavior. Newer security properties, user accounting, HKDF, and key removal semantics live in v2 filesystem-level keyring paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/keysetup_v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/crypto/policy.c -->
# File Research: sources/os/linux/linux/fs/crypto/policy.c

## Summary
Implements fscrypt policy validation, policy/context conversion, encryption-policy ioctls, inheritance checks, context creation for new inodes, permitted-context enforcement, and test dummy encryption mount-option parsing/showing.

## Main Responsibilities
- Compare fscrypt policies by version and exact serialized policy size.
- Convert policy versions to master-key specifiers.
- Retrieve filesystem dummy policy hooks.
- Validate v1 and v2 encryption mode combinations.
- Validate flags including padding, DIRECT_KEY, IV_INO_LBLK_64, IV_INO_LBLK_32, and v2 data-unit size.
- Convert policies to on-disk inode contexts and contexts back to policies.
- Set encryption policies on empty directories.
- Return policies via original and extended ioctls.
- Return encryption nonce for testing.
- Enforce that children in encrypted directories have permitted matching policies.
- Provide inheritable policy for new files.
- Build and set contexts for new encrypted inodes.
- Parse, compare, and display `test_dummy_encryption`.

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
V1 policies are deprecated and limited to legacy mode combinations. V2 policies allow newer combinations such as AES-256-XTS with AES-256-HCTR2 and SM4-XTS with SM4-CTS, plus v1-compatible combinations.

DIRECT_KEY requires contents and filename modes to match and requires an IV large enough to include the nonce. IV_INO_LBLK policies require AES-256-XTS, stable inode numbers, 32-bit inode numbers, and file data-unit indices that fit in 32 bits. `IV_INO_LBLK_32` is mutually exclusive with sub-block data units for now.

Setting a v2 policy verifies that the current user has added the referenced key, unless privileged override applies elsewhere in key verification. Setting a policy is restricted to owner/capable callers, requires writable mount state, locks the inode, and only succeeds on an empty directory with no existing policy or with the same existing policy.

`fscrypt_has_permitted_context()` allows encrypted children only when their policy matches the encrypted parent, but allows both parent and child with unrecognized policies so deletion remains possible.

## Research Notes
This file defines the compatibility and safety boundary for policy data that reaches disk. It is the main guard against unsupported mode/flag combinations and against inconsistent encrypted directory trees.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/crypto/policy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/d_path.c -->
# File Research: sources/os/linux/linux/fs/d_path.c

## Summary
Implements kernel pathname rendering helpers and the `getcwd` syscall. It builds paths backward into caller buffers while handling RCU path walks, concurrent renames, mount traversal, detached paths, deleted dentries, synthetic dentry names, raw dentry paths, and user-copy for cwd.

## Main Responsibilities
- Provide backward-prepend buffer primitives.
- Safely copy dentry names under possible rename races.
- Walk dentries and mounts from a path back to a supplied root.
- Return pathnames relative to the process root or absolute root.
- Support synthetic filesystem `d_dname` callbacks.
- Format simple/dynamic dentry names for pseudo filesystems.
- Provide raw dentry-only paths.
- Implement `sys_getcwd`.

## Key APIs
- `__d_path()`
- `d_absolute_path()`
- `d_path()`
- `dynamic_dname()`
- `simple_dname()`
- `dentry_path_raw()`
- `dentry_path()`
- `getcwd` syscall

## Important Behavior
Path strings are constructed from the end of the buffer backward. Overflow sets the buffer length negative and returns `-ENAMETOOLONG` through `extract_string()`.

Name copying is intentionally tolerant of concurrent rename races. It uses optimistic loads and `copy_from_kernel_nofault()`; if a race produces a mismatched pointer/length and copying faults, the copied bytes are filled with `x`. Sequence checks on `rename_lock` and `mount_lock` decide whether to retry and discard such garbage.

`prepend_path()` handles mount roots by walking up to parent mounts, distinguishes absolute root, detached/not-attached paths, and escaped paths, and ensures `/` is emitted for root.

`d_path()` appends `" (deleted)"` for unlinked dentries and delegates to `d_dname` for synthetic dentries that are not mounted roots. `getcwd()` returns `(unreachable)` when the process cwd is outside its root, returns `-ENOENT` for unlinked cwd, and copies the final path to userspace.

## Research Notes
This file is concurrency-sensitive VFS utility code. Its central invariant is that optimistic path construction is acceptable only because rename/mount sequence counters force retries when concurrent mutations matter.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/d_path.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dax.c -->
# File Research: sources/os/linux/linux/fs/dax.c

## Summary
Implements Linux filesystem DAX helpers for direct access to persistent memory without page cache pages. It manages DAX entries in an address-space xarray, entry locking and waiting, DAX folio association/sharing, busy-page detection, invalidation, writeback, iomap read/write, zeroing, unsharing, mmap fault handling for PTE/PMD mappings, synchronous faults, dedupe comparison, and remap preparation.

## Main Responsibilities
- Encode DAX xarray value entries with flags for locked, PMD, zero-page, and empty states.
- Provide waitqueue-based locking and wakeup for DAX entries.
- Manage DAX folio mapping/index/share state and compound-order reset.
- Associate and disassociate DAX entries with address spaces and VMAs.
- Detect busy DAX pages before layout changes or truncation.
- Delete and invalidate DAX mapping entries and ranges.
- Break DAX layouts by unmapping and waiting for page idleness.
- Flush dirty DAX mappings for writeback/fsync.
- Translate iomap file offsets to DAX PFNs and kernel addresses.
- Copy around unaligned CoW writes and shared extents.
- Load zero pages for sparse holes.
- Unshare CoW ranges.
- Zero DAX ranges and truncate partial blocks.
- Implement `dax_iomap_rw()` for direct read/write.
- Handle DAX mmap faults through PTE and optional PMD paths.
- Finish synchronous MAP_SYNC faults after fsync.
- Compare DAX ranges for dedupe and prepare remap operations.

## Key APIs
- Entry/layout: `dax_lock_folio()`, `dax_unlock_folio()`, `dax_lock_mapping_entry()`, `dax_unlock_mapping_entry()`
- Busy/invalidation: `dax_layout_busy_page_range()`, `dax_layout_busy_page()`, `dax_delete_mapping_entry()`, `dax_delete_mapping_range()`, `dax_break_layout()`, `dax_break_layout_final()`, `dax_invalidate_mapping_entry_sync()`
- Writeback: `dax_writeback_mapping_range()`
- I/O and zeroing: `dax_file_unshare()`, `dax_zero_range()`, `dax_truncate_page()`, `dax_iomap_rw()`
- Faults: `dax_iomap_fault()`, `dax_finish_sync_fault()`
- Remap/dedupe: `dax_dedupe_file_range_compare()`, `dax_remap_file_range_prep()`
- Folio utility: `dax_folio_reset_order()`

## Important Behavior
DAX entries are xarray value entries, not page pointers. Four low bits encode lock, PMD size, zero page, and empty locking placeholder. PMD entries cover aligned PMD-sized index ranges; waitqueue keys align PMD indices so all offsets in a PMD range wait on the same lock.

`grab_mapping_entry()` favors existing PTE entries over PMD entries. A PMD zero or empty entry can be downgraded when a PTE is needed. Real PMD storage entries are left in place, and PTE writes dirty the whole PMD entry.

DAX folios represent device memory pages. Shared file mappings clear `folio->mapping` and use `folio->share`. `dax_folio_reset_order()` restores compound folios to order-0 state when sharing refs drop.

Writeback writeprotects mappings with `pfn_mkclean_range()`, flushes persistent memory with `dax_flush()`, and clears dirty tags only after cache flush and while fault insertion is serialized by entry locks.

Iomap read/write directly maps device ranges with `dax_direct_access()`. Reads from holes/unwritten extents zero the user iterator. Writes to new or shared extents invalidate mappings so mmap sees write(2) data. CoW paths copy head/tail data around unaligned writes to avoid stale bytes.

Fault handling uses locked DAX entries and iomap mappings. Read faults on holes insert zero pages; write faults allocate or map storage. Synchronous MAP_SYNC write faults can return a PFN and require caller completion through `dax_finish_sync_fault()` after fsync. PMD faults fall back when alignment, VMA bounds, COW, file size, or existing PTE entries prevent huge mappings.

## Research Notes
This file is highly synchronization-sensitive. Correctness depends on xarray entry locking, page table invalidation, DAX read locks, dirty/TOWRITE tags, iomap extent semantics, memory-failure/rmap expectations for DAX folios, and filesystem locks that prevent concurrent truncation or mapping changes during fault and layout operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dax.c -->