# sources/distributed-fs/ceph-client/fs/btrfs/fs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/fs.c` implements core filesystem-wide helpers declared in `fs.h`: checksum algorithm metadata and one-shot/incremental checksum operations, supported block-size validation, exclusive operation state transitions, and superblock feature flag setters/clearers. The file was read as a complete 347-line implementation.

## Important APIs, Types, and Functions

The checksum table `btrfs_csums[]` maps Btrfs checksum type IDs to digest size and display name for CRC32C, xxhash64, SHA-256, and BLAKE2b. Exported checksum helpers are `btrfs_csum_type_size`, `btrfs_super_csum_size`, `btrfs_super_csum_name`, `btrfs_get_num_csums`, `btrfs_csum`, `btrfs_csum_init`, `btrfs_csum_update`, and `btrfs_csum_final`.

Other exported helpers are `btrfs_supported_blocksize`, `btrfs_exclop_start`, `btrfs_exclop_start_try_lock`, `btrfs_exclop_start_unlock`, `btrfs_exclop_finish`, `btrfs_exclop_balance`, `__btrfs_set_fs_incompat`, `__btrfs_clear_fs_incompat`, `__btrfs_set_fs_compat_ro`, and `__btrfs_clear_fs_compat_ro`.

## Control Flow

Checksum control flow is switch-based on the already-validated checksum type. One-shot `btrfs_csum()` writes the digest directly to the caller's output buffer in the correct little-endian form for integer digests. Incremental hashing initializes a `btrfs_csum_ctx`, updates the algorithm-specific context, then finalizes to the output buffer. Invalid types hit `BUG()` because mount-time validation is expected to have rejected them.

`btrfs_supported_blocksize()` asserts power-of-two bounds, accepts `PAGE_SIZE`, 4 KiB, and `BTRFS_MIN_BLOCKSIZE`, and under experimental support may accept block sizes larger than page size unless highmem makes that unsafe. Exclusive-operation control uses `fs_info->super_lock` to serialize `exclusive_operation`: start succeeds only from `BTRFS_EXCLOP_NONE`, try-lock allows same-operation reentry or paused-balance plus device-add compatibility, finish resets to none and notifies sysfs, and balance helper transitions between balance and paused states.

Feature flag setters/clearers read the superblock copy, double-check under `super_lock`, update incompat or compat-ro flags, log the change, and set `BTRFS_FS_FEATURE_CHANGED` so sysfs/commit paths can observe changed feature state.

## State and Persistence Behavior

Checksum helpers are stateless except for caller-owned `struct btrfs_csum_ctx`. Exclusive operation state is stored in memory in `fs_info->exclusive_operation` and protected by `super_lock`; it is exported through sysfs notification but is not on-disk state. Feature helpers mutate `fs_info->super_copy` feature bits, which later become persistent through normal superblock commit/write paths. They intentionally do not clear the `BTRFS_FS_FEATURE_CHANGED` bit.

## Dependencies and Integration Points

The file depends on Linux crypto helpers for CRC32C, xxhash, SHA-256, and BLAKE2b through headers included by `fs.h`, plus `messages.h`, `accessors.h`, and `volumes.h`. Checksum helpers are used by metadata/data checksum verification and superblock handling. Exclusive-operation helpers coordinate balance, device add/remove, replace, resize, and swap activation. Feature helpers are used by code that enables/disables format features such as free-space tree and extended inode refs.

## Risks and Edge Cases

Checksum type bounds are trusted after mount validation; any caller passing an unchecked type can trigger `BUG()`. The CRC32C path uses inverted seed/finalization and little-endian storage, so it must remain consistent with on-disk format expectations. Experimental block-size support deliberately rejects highmem larger-than-page cases because not all features implement page-by-page handling. Exclusive-operation callers must pair start/try-lock with unlock/finish exactly; missing finish can block later operations. Feature helpers update only the in-memory super copy and rely on transaction/superblock writeback to persist the change.

## Test Signals

Useful tests include checksum known-answer tests for all supported algorithms, incremental versus one-shot digest equivalence, mount validation of checksum types, supported block-size matrix tests across debug/experimental/highmem configurations, sysfs-visible exclusive-operation transitions during balance/device operations, and feature flag persistence after transactions that enable or clear compat-ro/incompat features.
