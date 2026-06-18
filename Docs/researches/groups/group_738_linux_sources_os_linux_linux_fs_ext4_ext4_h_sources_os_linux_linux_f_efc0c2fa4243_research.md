# Group Research: group_738_linux_sources_os_linux_linux_fs_ext4_ext4_h_sources_os_linux_linux_f_efc0c2fa4243

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. All five listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4.h -->
# File Research: sources/os/linux/linux/fs/ext4/ext4.h

## Purpose

`ext4.h` is the central internal ext4 header. It defines ext4’s core on-disk formats, in-memory inode/superblock state, feature flags, mount flags, block mapping contracts, directory formats, allocation state, journaling hooks, and cross-file function declarations used throughout `fs/ext4`.

## Main Definitions

- Basic ext4 scalar types:
  - `ext4_grpblk_t`: block offset within a block group.
  - `ext4_fsblk_t`: filesystem-wide physical block number.
  - `ext4_lblk_t`: file logical block number.
  - `ext4_group_t`: block group number.

- Allocation and mapping:
  - `enum criteria` defines mballoc search levels, from fast power-of-two/goal searches to slow full group scans.
  - `EXT4_MB_HINT_*` flags describe allocator hints such as goal-only, delayed allocation reservation, stream allocation, reserved pool use, and strict checks.
  - `struct ext4_allocation_request` carries logical range, physical hints, neighboring blocks, requested length, target inode, and flags.
  - `struct ext4_map_blocks` is the compact mapping request/result object used by `ext4_map_blocks()` and related functions.
  - `EXT4_MAP_*` flags encode mapped, new, unwritten, delayed, boundary, and query-state results.

- On-disk metadata:
  - `struct ext4_group_desc` defines group descriptor layout, including block/inode bitmap locations, inode table location, free counts, checksum fields, exclude bitmap fields, and high 64-bit block address halves.
  - `struct ext4_inode` defines the on-disk inode, including classic fields, block array, OS-dependent fields, extended timestamps, checksum fields, creation time, version high bits, and project ID.
  - `struct ext4_super_block` defines the full ext4 superblock layout, including counts, block geometry, feature flags, journal references, hash seeds, 64-bit counters, MMP fields, quota inode numbers, checksum seed, encoding fields, orphan file inode, and final checksum.

- In-memory metadata:
  - `struct ext4_inode_info` wraps VFS inode state with ext4-specific fields:
    - raw block data, file ACL, block group, inode flags/state, xattr lock, orphan tracking, fast commit state, raw inode lock, disk size, data semaphore, JBD2 inode, metadata buffer tracking, creation time, preallocation state, extent status tree, pending cluster reservations, inline data fields, quota state, completed I/O lists, fsync transaction IDs, checksum seed, project ID, and fscrypt state.
  - `struct ext4_sb_info` is the large per-mounted-filesystem state object:
    - block geometry, descriptor arrays, mount options, reserved blocks, counters, block group locks, journal state, orphan info, quota config, buddy allocator state, mballoc tunables/statistics, locality groups, flex groups, writeback workqueues, MMP state, folio order limits, checksum seed, extent status shrinker, xattr caches, ratelimits, dummy encryption policy, writepages lock, DAX info, block device error tracking, fast commit queues/state, and atomic write unit limits.

## Feature and Flag Model

- Inode flags include ext2/ext3-compatible flags plus ext4 additions:
  - extents, huge file, verity, EA inode, DAX, inline data, project inheritance, casefolding, encryption, journal data, immutable, append-only, noatime, nodump.
- `ext4_check_flag_values()` uses build-time checks to keep `EXT4_*_FL` values aligned with `EXT4_INODE_*` bit numbers.
- Feature flags are split into:
  - compatible: journal, xattr, dir index, fast commit, stable inodes, orphan file.
  - readonly-compatible: sparse super, large file, huge file, metadata checksum, quota, bigalloc, project quota, verity, orphan present.
  - incompatible: compression, filetype, journal recovery, extents, 64bit, MMP, flex_bg, EA inode, inline data, encrypt, casefold, largedir, checksum seed.
- Macro-generated helpers provide `ext4_has_feature_*`, `ext4_set_feature_*`, and `ext4_clear_feature_*`.
- Supported feature masks define what this kernel can mount as ext2, ext3, or ext4.

## Directory and Name Handling

- Defines classic and modern directory entries:
  - `struct ext4_dir_entry`
  - `struct ext4_dir_entry_2`
  - `struct ext4_dir_entry_hash`
  - `struct ext4_dir_entry_tail`
- Casefolded encrypted directories store hashes after the aligned filename area.
- `ext4_dir_rec_len()` accounts for hash trailer space when needed.
- Directory record length conversion helpers handle special encodings for 64 KiB and larger block sizes.
- HTree directory constants and hash versions are declared, including legacy, half-MD4, TEA, unsigned variants, and SipHash.
- `struct ext4_filename` carries user name, disk name, hash info, optional fscrypt buffer, and optional casefold name.

## Journaling and Error Interfaces

- Declares ext4 journal trigger types and `struct ext4_journal_trigger`, currently including orphan-file checksum triggers.
- Error reporting interfaces include:
  - `__ext4_error`
  - `__ext4_error_inode`
  - `__ext4_error_file`
  - `__ext4_std_error`
  - `__ext4_warning`
  - `__ext4_msg`
  - `__ext4_grp_locked_error`
- Public macros add caller function and line metadata.
- Emergency state helpers return `-EIO` for forced shutdown and `-EROFS` for emergency read-only state.

## Allocation and Block Group State

- `struct ext4_group_info` tracks buddy allocator state for a block group:
  - free tree, first free block, total free blocks, fragments, largest/average free fragment order, prealloc list, optional double-check bitmap, allocation semaphore, and free counters by order.
- Group info bits track lazy initialization, trim state, corrupt block/inode bitmaps, and bitmap read state.
- Group lock helpers wrap per-blockgroup spinlocks and maintain a contention counter.
- Bigalloc macros convert between blocks and clusters and mask or fill cluster offsets.

## Inline Helpers and Invariants

- Timestamp helpers encode/decode extended epoch/nanosecond fields and gracefully handle old inode sizes where extra fields do not fit.
- Inode size helpers handle large directories and regular files using high size bits.
- Superblock count helpers read/write 64-bit block counters split into low/high fields.
- `ext4_valid_inum()` validates root inode and non-reserved inode ranges.
- `is_special_ino()` recognizes reserved, quota, and orphan-file inodes.
- `ext4_update_i_disksize()` and `ext4_update_inode_size()` serialize disk-size growth under `i_data_sem`.
- `ext4_inode_can_atomic_write()` allows atomic writes only for regular extent-based files with a nonzero filesystem atomic write unit minimum.

## Declared Cross-Module APIs

The header declares major ext4 subsystem entrypoints, including:

- bitmap checksum and validation
- block allocator and mballoc
- inode allocation, read/write, truncate, page write, DAX/iomap, project quota
- indirect block mapping
- extents mapping, insert, truncate, replay, fiemap, swap, unwritten conversion
- fast commit tracking, commit, replay cleanup
- directory indexing, lookup, insert, delete, inline directory handling
- resize and online group addition
- superblock read/checksum/error handling
- MMP
- orphan list/file handling
- fscrypt, fsverity, sysfs, read folio/readahead, page I/O

## Dependencies

- Linux kernel VFS, buffer-head, block-device, quota, fscrypt, fsverity, DAX, percpu counters, rbtrees, xarrays, shrinkers, JBD2.
- Includes `extents_status.h` and `fast_commit.h`, so inode and superblock structures directly embed extent status and fast commit state.

## Research Notes

This file is the architectural contract for ext4. Most implementation files depend on it for structure layout, flag compatibility, allocation constants, and subsystem prototypes. Changes here have wide blast radius because many definitions are both on-disk ABI and internal synchronization contracts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4_extents.h -->
# File Research: sources/os/linux/linux/fs/ext4/ext4_extents.h

## Purpose

`ext4_extents.h` defines ext4’s extent tree on-disk structures and small helper routines for extent traversal, extent length state, physical block packing, and KUnit-test-visible extent hooks.

## Main Definitions

- `struct ext4_extent_tail`
  - Stores the checksum at the end of non-inode extent blocks.
  - Checksum covers filesystem UUID, inode number, and extent block data.

- `struct ext4_extent`
  - Leaf extent record.
  - Fields:
    - `ee_block`: first logical block covered.
    - `ee_len`: extent length and unwritten-state encoding.
    - `ee_start_hi` / `ee_start_lo`: split physical block address.

- `struct ext4_extent_idx`
  - Internal extent-tree index record.
  - Fields:
    - `ei_block`: logical block range covered by child.
    - `ei_leaf_lo` / `ei_leaf_hi`: child extent/index block physical address.
    - `ei_unused`: padding.

- `struct ext4_extent_header`
  - Present at each extent tree node, including the inode-root node.
  - Tracks magic, current entries, maximum entries, tree depth, and generation.

- `struct ext4_ext_path`
  - Runtime path used while traversing or modifying the extent tree.
  - Holds physical block, depth, max depth, current extent/index/header, and buffer head.

- `struct partial_cluster`
  - Used during extent removal for bigalloc cluster boundary handling.
  - Tracks physical cluster, logical block, and whether the partial cluster is initial, freeable, or not freeable.

## Constants and Encoding

- `EXT4_EXT_MAGIC` is the extent header magic.
- `EXT4_MAX_EXTENT_DEPTH` caps extent tree depth at 5.
- `EXT_INIT_MAX_LEN` is 32768 blocks.
- `EXT_UNWRITTEN_MAX_LEN` is 32767 blocks.
- `ee_len` uses its high bit to encode unwritten extents:
  - values up to `0x8000` are initialized extents.
  - values above `0x8000` are unwritten extents with actual length adjusted by subtracting `EXT_INIT_MAX_LEN`.
  - `0x8000` is a special initialized 32768-block extent.

## Helper Macros and Functions

- Tree navigation:
  - `EXT_FIRST_EXTENT`
  - `EXT_FIRST_INDEX`
  - `EXT_LAST_EXTENT`
  - `EXT_LAST_INDEX`
  - `EXT_MAX_EXTENT`
  - `EXT_MAX_INDEX`
  - `EXT_HAS_FREE_INDEX`
- Header access:
  - `ext_inode_hdr()` returns the inode-root extent header from `EXT4_I(inode)->i_data`.
  - `ext_block_hdr()` returns the extent header from a buffer head.
  - `ext_depth()` returns the inode-root tree depth.
- Tail access:
  - `EXT4_EXTENT_TAIL_OFFSET()`
  - `find_ext4_extent_tail()`
- Extent state:
  - `ext4_ext_mark_unwritten()`
  - `ext4_ext_is_unwritten()`
  - `ext4_ext_get_actual_len()`
  - `ext4_ext_mark_initialized()`
- Physical block packing:
  - `ext4_ext_pblock()` combines `ee_start_lo` and `ee_start_hi`.
  - `ext4_idx_pblock()` combines `ei_leaf_lo` and `ei_leaf_hi`.
  - `ext4_ext_store_pblock()` splits a physical block into extent fields.
  - `ext4_idx_store_pblock()` splits a physical block into index fields.

## Declared APIs

- `__ext4_ext_dirty()` marks extent metadata dirty under a journal handle.
- `ext4_ext_zeroout()` zeroes blocks covered by an extent.
- Under `CONFIG_EXT4_KUNIT_TESTS`, exposes:
  - `ext4_ext_space_root_idx_test()`
  - `ext4_split_convert_extents_test()`

## Dependencies

- Includes `ext4.h`, so it depends on ext4 inode types, block types, buffer heads, endian helpers, and JBD2 handle declarations.

## Research Notes

This header is small but encodes the core extent ABI. The most important invariant is the overloaded `ee_len` high bit: callers must use the helper functions rather than raw length arithmetic when unwritten extents are possible.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4_extents.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4_jbd2.c -->
# File Research: sources/os/linux/linux/fs/ext4/ext4_jbd2.c

## Purpose

`ext4_jbd2.c` implements ext4’s runtime wrapper layer around JBD2. It selects inode data journaling mode, starts/stops journal handles, supports no-journal pseudo-handles, ensures transaction credits, assigns metadata checksum triggers, forgets/revokes buffers, and marks metadata dirty.

## Main Functions

- `ext4_inode_journal_mode(struct inode *inode)`
  - Chooses one of:
    - journal data
    - ordered data
    - writeback data
  - Returns writeback if no journal exists.
  - Uses journal data for non-regular files, EA inodes, full data journaling mount mode, or `EXT4_INODE_JOURNAL_DATA` without delayed allocation.
  - Encrypted regular file data is not fully journaled and falls back to ordered mode.
  - Uses mount `DATA_FLAGS` for ordered/writeback decisions.

- `ext4_get_nojournal()` / `ext4_put_nojournal()`
  - Implement no-journal nesting using small integer pseudo-handles stored in `current->journal_info`.
  - Guarded by `EXT4_NOJOURNAL_MAX_REF_COUNT`.

- `ext4_journal_check_start(struct super_block *sb)`
  - Verifies journal start is allowed.
  - Checks emergency state, read-only superblock, full freeze warning, and aborted journal state.
  - If the journal aborted, calls `ext4_abort()` and returns `-EROFS`.

- `__ext4_journal_start_sb(...)`
  - Tracepoints journal starts by inode or superblock.
  - Calls `ext4_journal_check_start()`.
  - Uses no-journal pseudo-handle when no journal exists or fast commit replay is active.
  - Otherwise starts JBD2 with `jbd2__journal_start()` using `GFP_NOFS`.

- `__ext4_journal_stop(...)`
  - Stops a journal handle.
  - Handles no-journal pseudo-handles separately.
  - Preserves `handle->h_err`, calls `jbd2_journal_stop()`, and reports ext4 standard errors when needed.

- `__ext4_journal_start_reserved(...)`
  - Starts a pre-reserved JBD2 handle after validating the filesystem state.
  - Frees the reserved handle on start failure.

- `__ext4_journal_ensure_credits(...)`
  - Ensures a handle has enough buffer and revoke credits.
  - Returns success for no-journal handles.
  - Fails with `-EROFS` for aborted handles.
  - Extends the transaction when current credits are insufficient.

- `ext4_journal_abort_handle(...)`
  - Records handle error, traces buffer abort, prints transaction abort context, and aborts the JBD2 handle.

- `ext4_check_bdev_write_error(struct super_block *sb)`
  - In no-journal paths, checks block-device writeback errors using `errseq`.
  - Reports async metadata writeback errors through `ext4_error_err()` to avoid reusing stale metadata.

- `__ext4_journal_get_write_access(...)`
  - Gets JBD2 write access for a metadata buffer.
  - In no-journal mode, checks block-device write errors instead.
  - Assigns JBD2 buffer triggers when metadata checksums are enabled and a trigger type is supplied.

- `__ext4_forget(...)`
  - Forgets or revokes freed blocks.
  - No-journal path clears dirty state, waits on the buffer, and calls `__bforget()`.
  - Full data journaling and non-journaled data use `jbd2_journal_forget()`.
  - Metadata or journaled data in ordered/writeback cases uses `jbd2_journal_revoke()`.
  - On revoke failure, aborts the handle and reports an ext4 error.

- `__ext4_journal_get_create_access(...)`
  - Gets create access for newly created metadata buffers and installs checksum triggers when needed.

- `__ext4_handle_dirty_metadata(...)`
  - Marks metadata buffers dirty.
  - In journal mode, uses `jbd2_journal_dirty_metadata()`.
  - In no-journal mode, marks via `mmb_mark_buffer_dirty()` for inode metadata buffers or `mark_buffer_dirty()`.
  - If the inode needs synchronous updates, syncs the dirty buffer and reports I/O errors.

## Error Handling

- Journal access errors generally abort the current handle.
- Metadata dirty failures are treated as severe unless the handle is already aborted.
- Standard ext4 error reporting is used to update filesystem error state.
- No-journal paths still check block-device writeback errors to avoid silent metadata corruption.

## Dependencies

- Includes `ext4_jbd2.h`.
- Uses JBD2 APIs, ext4 error reporting, mount options, ext4 feature checks, buffer-head helpers, tracepoints, and errseq writeback tracking.

## Research Notes

This file is the operational bridge between ext4 metadata mutation and JBD2 transaction semantics. Its no-journal pseudo-handle path is a notable design point: callers can use the same wrapper APIs whether a journal exists or not, but correctness still depends on explicit dirtying, syncing, and block-device write-error checks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4_jbd2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4_jbd2.h -->
# File Research: sources/os/linux/linux/fs/ext4/ext4_jbd2.h

## Purpose

`ext4_jbd2.h` declares ext4’s journaling interface, transaction credit formulas, handle operation types, wrapper macros, inline JBD2 adapters, data journaling mode helpers, revoke credit helpers, direct-I/O journal compatibility checks, and journal teardown helper.

## Transaction Credit Model

- `EXT4_SINGLEDATA_TRANS_BLOCKS(sb)`
  - Estimates credits for modifying one data block.
  - Uses a larger estimate for extents-enabled filesystems.

- `EXT4_XATTR_TRANS_BLOCKS`
  - Credits for extended attribute metadata updates.

- `EXT4_DATA_TRANS_BLOCKS(sb)`
  - Combines single-data-block, xattr, and quota transaction needs.

- `EXT4_META_TRANS_BLOCKS(sb)`
  - Credits for superblock, inode, quota, and xattr metadata.

- `EXT4_MAX_TRANS_DATA`
  - Arbitrary maximum anticipated data blocks for large write/truncate transactions.

- `EXT4_RESERVE_TRANS_BLOCKS`
  - Low-credit threshold reserve used before extending or restarting large transactions.

- `EXT4_INDEX_EXTRA_TRANS_BLOCKS`
  - Extra credits for indexed directory insertion and htree splits.

- Quota credit macros:
  - `EXT4_QUOTA_TRANS_BLOCKS`
  - `EXT4_QUOTA_INIT_BLOCKS`
  - `EXT4_QUOTA_DEL_BLOCKS`
  - `EXT4_MAXQUOTAS_*`

## Handle Types

Defines numeric operation types for tracing/logging:

- `EXT4_HT_MISC`
- `EXT4_HT_INODE`
- `EXT4_HT_WRITE_PAGE`
- `EXT4_HT_MAP_BLOCKS`
- `EXT4_HT_DIR`
- `EXT4_HT_TRUNCATE`
- `EXT4_HT_QUOTA`
- `EXT4_HT_RESIZE`
- `EXT4_HT_MIGRATE`
- `EXT4_HT_MOVE_EXTENTS`
- `EXT4_HT_XATTR`
- `EXT4_HT_EXT_CONVERT`

## Declared APIs

- Inode dirtying and inode write reservation:
  - `ext4_mark_iloc_dirty()`
  - `ext4_reserve_inode_write()`
  - `__ext4_mark_inode_dirty()`
  - `ext4_expand_extra_isize()`

- Journal wrappers:
  - `__ext4_journal_get_write_access()`
  - `__ext4_forget()`
  - `__ext4_journal_get_create_access()`
  - `__ext4_handle_dirty_metadata()`
  - `__ext4_journal_start_sb()`
  - `__ext4_journal_stop()`
  - `__ext4_journal_start_reserved()`
  - `__ext4_journal_ensure_credits()`

## Wrapper Macros

- Macros inject `__func__` and `__LINE__` into lower-level functions:
  - `ext4_journal_get_write_access`
  - `ext4_forget`
  - `ext4_journal_get_create_access`
  - `ext4_handle_dirty_metadata`
  - `ext4_journal_stop`
  - `ext4_journal_start_reserved`

- Journal start convenience macros:
  - `ext4_journal_start_sb`
  - `ext4_journal_start`
  - `ext4_journal_start_with_reserve`
  - `ext4_journal_start_with_revoke`

## Inline Helpers

- `ext4_handle_valid(handle)`
  - Distinguishes real JBD2 handles from no-journal small-integer pseudo-handles.

- `ext4_handle_sync(handle)`
  - Marks a valid handle synchronous.

- `ext4_handle_is_aborted(handle)`
  - Checks aborted state only for valid JBD2 handles.

- `ext4_free_metadata_revoke_credits(sb, blocks)`
  - Accounts for metadata block freeing, scaling by cluster ratio.

- `ext4_trans_default_revoke_credits(sb)`
  - Default revoke credit estimate.

- `ext4_journal_extend()` / `ext4_journal_restart()`
  - No-op for no-journal handles; otherwise call JBD2.

- `ext4_journal_ensure_credits_fn(...)`
  - Ensures credits and can run a cleanup expression before transaction restart.
  - Returns negative error, zero for enough/extended credits, or one if restarted.

- `ext4_journal_ensure_credits(...)`
  - Simpler credit ensure wrapper.

- `ext4_journal_blocks_per_folio(inode)`
  - Delegates to JBD2 only when a journal exists.

- `ext4_journal_force_commit(journal)`
  - Forces commit if journal is non-null.

- `ext4_jbd2_inode_add_write()` / `ext4_jbd2_inode_add_wait()`
  - Adds ranged write/wait tracking to the inode’s JBD2 inode.

- `ext4_update_inode_fsync_trans()`
  - Records transaction IDs needed for fsync/fdatasync.

## Data Journaling Mode Helpers

- Modes:
  - `EXT4_INODE_JOURNAL_DATA_MODE`
  - `EXT4_INODE_ORDERED_DATA_MODE`
  - `EXT4_INODE_WRITEBACK_DATA_MODE`

- Predicates:
  - `ext4_should_journal_data()`
  - `ext4_should_order_data()`
  - `ext4_should_writeback_data()`

- `ext4_free_data_revoke_credits(inode, blocks)`
  - Returns zero for full data journaling and for non-journaled data.
  - For journaled data, accounts for blocks plus partial clusters at extent boundaries.

## Direct I/O Compatibility

- `ext4_should_dioread_nolock(inode)` allows direct I/O read without `i_rwsem` only when:
  - `DIOREAD_NOLOCK` mount option is set.
  - inode is regular.
  - inode uses extents.
  - data journaling is not enabled.
  - delayed allocation is enabled.

## Journal Teardown

- `ext4_journal_destroy(struct ext4_sb_info *sbi, journal_t *journal)`
  - Sets `EXT4_MF_JOURNAL_DESTROY`.
  - Forces a commit and flushes pending superblock update work.
  - Calls `jbd2_journal_destroy()`.
  - Clears `sbi->s_journal`.

## Dependencies

- Includes Linux VFS and JBD2 headers plus `ext4.h`.
- Depends on ext4 superblock state, quota feature helpers, inode journaling state, mount flags, and JBD2 transaction APIs.

## Research Notes

This header is the compile-time contract for all ext4 code that mutates metadata under journaling. Its credit formulas are conservative estimates that shape transaction sizing and restart behavior across inode, directory, xattr, quota, extent, resize, and truncate paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/ext4_jbd2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents-test.c -->
# File Research: sources/os/linux/linux/fs/ext4/extents-test.c

## Purpose

`extents-test.c` is a KUnit test module for ext4 extent split and conversion behavior. It verifies direct extent split/convert logic and higher-level map/create paths, including fallback zeroout behavior when extent insertion fails.

## Test Subject

The tests focus on behavior around:

- `ext4_split_convert_extents()`, exposed to tests as `ext4_split_convert_extents_test()`.
- `ext4_map_query_blocks()`.
- `ext4_map_create_blocks()`.
- conversion from unwritten to written extents.
- conversion from written to unwritten extents.
- zeroout fallback when split insertion fails with `-ENOSPC`.
- extent status cache synchronization for higher-level paths.

## Fixed Test Geometry

- `EXT_DATA_PBLK = 100`
- `EXT_DATA_LBLK = 10`
- `EXT_DATA_LEN = 3`
- Block size is configured as 4096 bytes.
- Each test starts with one extent covering logical blocks `[10, 13)` and physical blocks `[100, 103)`.
- The extent may start as written or unwritten depending on test parameters.

## Test Context

- `struct kunit_ctx`
  - Holds a mocked `ext4_inode_info`.
  - Holds `k_data`, a memory buffer simulating disk data for zeroout tests.

- `struct kunit_ext_state`
  - Expected logical block, length, and unwritten state for resulting extents.

- `struct kunit_ext_data_state`
  - Expected character value and block range in the simulated data buffer.

- `struct kunit_ext_test_param`
  - Parameterizes all test variants:
    - description
    - test type
    - initial unwritten state
    - split flags
    - split map
    - zeroout enable/disable
    - expected extent count
    - expected extent states
    - expected data buffer segments for zeroout tests

## Mock Filesystem Setup

- Defines a minimal `file_system_type` named `"extents test"`.
- `extents_kunit_init()`:
  - Allocates `ext4_sb_info`.
  - Creates a superblock through `fs_context_for_mount()` and `sget_fc()`.
  - Sets ext4 private superblock state.
  - Sets block size and block size bits.
  - Enables zeroout threshold unless disabled by the test parameter.
  - Registers the extent status shrinker.
  - Allocates a mock `ext4_inode_info`.
  - Initializes the inode extent status tree and locks.
  - Marks the inode as extent-based.
  - Allocates `k_data` and fills it with `'X'`.
  - Constructs a depth-zero extent tree directly in `i_data`.
  - Inserts the matching extent status cache entry.
  - Activates static stubs for dirtying and zeroout.

- `extents_kunit_exit()`:
  - Unregisters the extent status shrinker.
  - Deactivates the superblock.
  - Frees superblock private state, inode state, and data buffer.

## Static Stubs

- `__ext4_ext_dirty_stub()`
  - Returns success without journaling.

- `ext4_ext_insert_extent_stub()`
  - Returns `ERR_PTR(-ENOSPC)` to force zeroout fallback.

- `ext4_ext_zeroout_stub()`
  - Validates the requested extent is within the fixed test extent.
  - Zeroes the corresponding range in `k_data`.

- `ext4_issue_zeroout_stub()`
  - Validates logical and physical offsets line up.
  - Zeroes the corresponding range in `k_data`.

## Test Execution

- `check_buffer()`
  - Verifies that a buffer range is filled with one expected byte.
  - Logs first mismatch.

- `ext4_map_create_blocks_helper()`
  - Calls `ext4_map_query_blocks()` to populate map flags and physical block information.
  - Calls `ext4_map_create_blocks()` to trigger split/conversion.
  - Used instead of full `ext4_map_blocks()` to avoid mocking unrelated code.

- `test_split_convert()`
  - Shared test body for all parameter sets.
  - Optionally stubs `ext4_ext_insert_extent()` to force zeroout fallback.
  - Finds the initial extent and validates starting state.
  - Runs either:
    - direct `ext4_split_convert_extents_test()`, or
    - high-level query/create block path.
  - Re-reads the extent tree and compares every expected extent.
  - For high-level paths, verifies extent status cache contains corresponding written/unwritten status and physical block.
  - For zeroout tests, validates simulated data buffer segments.

## Parameter Groups

- `test_split_convert_params`
  - Direct split/convert tests.
  - Covers:
    - unwritten to written conversion for first half, second half, and middle.
    - written to unwritten conversion for first half, second half, and middle.
    - zeroout fallback for the same variants.
  - Direct split tests ignore extent status cache checks because the split function uses `EXT4_EX_NOCACHE`.

- `test_convert_initialized_params`
  - High-level tests for the `ext4_ext_map_blocks() -> convert_initialized_extent()` path.
  - Covers written-to-unwritten conversion with normal split and zeroout fallback.

- `test_handle_unwritten_params`
  - High-level tests for the `ext4_ext_map_blocks() -> ext4_ext_handle_unwritten_extents()` path.
  - Covers:
    - unwritten-to-written conversion via endio-style `EXT4_GET_BLOCKS_CONVERT`.
    - unwritten-to-written conversion via non-endio `EXT4_GET_BLOCKS_CREATE`.
    - zeroout fallback for both paths.
    - non-zeroout split behavior with zeroout disabled.

## KUnit Registration

- Uses `KUNIT_CASE_PARAM_WITH_INIT()` instead of the more compact array macro because of noted output parsing limitations.
- Registers three parameterized invocations of `test_split_convert()`.
- Suite name: `ext4_extents_test`.
- Module license: GPL.

## Dependencies

- KUnit framework and static stubs.
- Minimal VFS superblock/context helpers.
- ext4 core header and extents header.
- Extent status tree functions.
- Test-only exports enabled by `CONFIG_EXT4_KUNIT_TESTS`.

## Research Notes

This test is focused and synthetic. It does not mount a real ext4 filesystem; instead, it builds the minimum inode/superblock/extent-status state needed to exercise extent split and conversion code. The simulated data buffer is important because it verifies not only tree shape but also zeroout correctness, preventing fallback conversion from leaking stale bytes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents-test.c -->