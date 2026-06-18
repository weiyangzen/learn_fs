# Group Research: group_980_linux_stable_sources_os_linux_linux_stable_fs_ext4_ext4_h_sources_os_189de7f5de65

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/ext4.h

## Summary
Central ext4 internal header. It defines ext4's on-disk metadata formats, in-memory inode and superblock state, mount and feature flags, allocator and mapping contracts, directory entry formats, error-reporting wrappers, and most cross-file function declarations used by the Linux stable ext4 implementation.

## Main Responsibilities
- Defines core ext4 scalar types: filesystem blocks, logical blocks, group numbers, and group-relative block offsets.
- Defines allocation inputs and flags for multiblock allocation, delayed allocation, bigalloc clusters, block freeing, and block mapping.
- Describes on-disk group descriptors, inodes, superblocks, directory entries, checksum tails, orphan-file blocks, and MMP blocks.
- Defines `struct ext4_inode_info` and `struct ext4_sb_info`, the main in-memory state containers for per-inode and per-mount ext4 behavior.
- Provides helpers for feature-bit testing and mutation, inode state/flag manipulation, size and timestamp encoding, block/group math, directory record sizing, and locking.
- Declares the public internal APIs implemented by ext4's allocation, inode, extent, directory, journaling, resize, orphan, inline-data, sysfs, block-validity, page-I/O, MMP, and verity files.

## Important Structures
- `struct ext4_allocation_request`: input to `ext4_mb_new_blocks()` and block allocator goal selection.
- `struct ext4_map_blocks`: logical-to-physical mapping result and request carrier for `ext4_map_blocks()` and query/create variants.
- `struct ext4_io_end` / `struct ext4_io_submit`: buffered writeback completion and bio aggregation state, especially for unwritten extent conversion.
- `struct ext4_group_desc`: on-disk block group descriptor, including low/high bitmap, inode table, free counts, flags, checksums, and exclude bitmap fields.
- `struct ext4_inode`: on-disk inode layout, including extents/indirect block storage, extended timestamps, checksums, version high bits, and project ID.
- `struct ext4_inode_info`: VFS inode wrapper with raw inode data, block group locality, xattr semaphore, orphan tracking, fast commit lists/ranges, `i_disksize`, `i_data_sem`, jbd2 inode, delayed allocation reservations, extent status tree, preallocations, inline-data offsets, quota state, completed I/O lists, fsync transaction IDs, checksum seed, project ID, and fscrypt state.
- `struct ext4_super_block`: on-disk superblock layout, including feature masks, journal metadata, group geometry, error history, quota inode numbers, checksum seed, encoding, orphan-file inode, and checksum.
- `struct ext4_sb_info`: in-memory superblock with geometry caches, group descriptors, counters, mount flags, journal/orphan state, mballoc caches and tunables, flex groups, lazy inode initialization, MMP, checksum seeds, shrinkers, xattr caches, journal triggers, error state, DAX state, atomic write units, and fast commit queues.

## Key Behavior
Feature handling is macro-generated through `EXT4_FEATURE_*_FUNCS()`, producing `ext4_has_feature_*`, `ext4_set_feature_*`, and `ext4_clear_feature_*` helpers over compatible, read-only-compatible, and incompatible superblock feature masks. Supported feature masks for ext2, ext3, and ext4 are defined in this header.

Inode flags are represented both as on-disk `EXT4_*_FL` masks and bit indices such as `EXT4_INODE_EXTENTS`. `ext4_check_flag_values()` enforces that these remain consistent at build time. Dynamic inode state bits share storage with `i_flags` on 64-bit builds and use `i_state_flags` on smaller word-size builds.

Timestamp helpers encode and decode ext4's extra epoch and nanosecond fields, falling back to clamped 32-bit seconds when a legacy inode lacks enough extra space.

Directory definitions cover legacy and `file_type` entries, encrypted+casefolded hash suffixes, checksum tails, record-length encoding for block sizes up to 256 KiB, htree hash versions, and link-count behavior for indexed directories.

The header centralizes error paths: `ext4_error*`, `ext4_warning*`, `ext4_msg`, `ext4_abort`, and group-locked error wrappers attach caller location, inode/file/block context, and optional errno to superblock error accounting.

## Synchronization and Lifetime
`i_data_sem` serializes extent/indirect tree mutation against truncate and uses lock subclasses for normal, second-inode, quota, and EA-inode cases. `xattr_sem` separates extended attribute reads/writes from regular data `i_rwsem` traffic. `s_writepages_rwsem` protects writeback against remount or inode flag changes that alter journaling, delayed allocation, DAX, or direct-I/O behavior. Fast commit queues are protected by `s_fc_lock` with NOFS wrappers.

RCU is used for resizable arrays such as group descriptors, group info, and flex groups. Group locks come from `blockgroup_lock`, with contention tracking used by the allocator.

## Dependencies
Includes JBD2, quotas, fscrypt, fsverity, percpu counters, block devices, FIEMAP, rbtree, seqlock, and ext4 subheaders `extents_status.h` and `fast_commit.h`. It is included by most ext4 implementation files and is the shared contract between allocator, extent, journaling, inode, directory, resize, and recovery logic.

## Risks
This header encodes ABI-sensitive on-disk layouts and feature masks; any change must preserve endian handling, struct offsets, and compatibility with e2fsprogs and older kernels. Many inline helpers assume the caller already holds the right inode, group, journal, or resize locks. Size, timestamp, cluster, and block-number helpers are easy to misuse across bigalloc, 64-bit, non-extent, and large-directory cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4_extents.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/ext4_extents.h

## Summary
Defines ext4's extent tree on-disk structures, in-memory traversal path, extent length/state helpers, physical block packing helpers, and KUnit-visible extent testing hooks.

## Main Responsibilities
- Describes the extent block tail checksum record.
- Defines leaf extents, internal extent indexes, and extent block headers.
- Defines `struct ext4_ext_path`, the traversal state used by lookup, insertion, split, truncate, and conversion paths.
- Defines `struct partial_cluster` for bigalloc-aware extent removal decisions.
- Provides macros for locating first, last, and maximum extents or indexes inside a header.
- Provides inline helpers for root/in-block headers, tree depth, unwritten/initialized state, logical length, and physical block encoding.

## Important Details
Extent blocks use a 12-byte header followed by either extents or indexes. Non-inode extent blocks can store `struct ext4_extent_tail` at the end of the block for metadata checksums without rebalancing the tree.

`ee_len` encodes both length and unwritten state. Initialized extents can reach `EXT_INIT_MAX_LEN` blocks. Unwritten extents use the high bit and can reach `EXT_UNWRITTEN_MAX_LEN`; the exact value `0x8000` is treated as initialized length 32768 rather than unwritten length zero.

Physical blocks are split into low 32-bit and high 16-bit fields in both extents and indexes. `ext4_ext_pblock()`, `ext4_idx_pblock()`, `ext4_ext_store_pblock()`, and `ext4_idx_store_pblock()` are the canonical conversions.

## Key APIs
- `__ext4_ext_dirty()`.
- `ext4_ext_zeroout()`.
- KUnit-only `ext4_ext_space_root_idx_test()` and `ext4_split_convert_extents_test()` when `CONFIG_EXT4_KUNIT_TESTS` is enabled.

## Dependencies
Includes `ext4.h` and uses ext4 inode state, buffer heads, JBD2 handles, and logical/physical block typedefs. The main implementation lives in `extents.c`.

## Risks
Extent tree correctness depends on careful endian conversion and exact interpretation of `ee_len`. `struct ext4_ext_path` contains raw pointers into inode or buffer-head extent blocks; callers must preserve buffer lifetime and update dirty state through the journaling path.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4_extents.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4_jbd2.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/ext4_jbd2.c

## Summary
Implements ext4's concrete wrapper layer around JBD2. It selects inode data journaling mode, starts and stops journal handles, supports no-journal pseudo-handles, manages reserved handles and credits, revokes or forgets freed blocks, attaches metadata checksum triggers, detects backing-device metadata writeback errors, and dirties metadata buffers.

## Main Responsibilities
- Determines per-inode data mode with `ext4_inode_journal_mode()`.
- Validates journal start conditions against forced shutdown, emergency read-only, read-only superblocks, freeze state, and aborted journals.
- Starts normal, superblock, reserved, and no-journal transactions.
- Stops transactions and reports handle errors through ext4 superblock error paths.
- Ensures transaction and revoke credits are available, extending transactions when needed.
- Aborts handles on JBD2 failures and records the first handle error.
- Implements ext4 forget/revoke policy for metadata blocks and journaled data.
- Gets write/create access to metadata buffers and installs checksum triggers when needed.
- Marks metadata dirty through JBD2 or through buffer dirtying in no-journal mode.

## Key APIs
- `ext4_inode_journal_mode()`.
- `__ext4_journal_start_sb()`.
- `__ext4_journal_stop()`.
- `__ext4_journal_start_reserved()`.
- `__ext4_journal_ensure_credits()`.
- `__ext4_journal_get_write_access()`.
- `__ext4_forget()`.
- `__ext4_journal_get_create_access()`.
- `__ext4_handle_dirty_metadata()`.

## Important Behavior
No-journal operation is represented by small non-pointer `handle_t *` values stored in `current->journal_info`; `ext4_get_nojournal()` and `ext4_put_nojournal()` increment and decrement this pseudo-reference count.

Data journaling is disabled for encrypted regular file data, falling back to ordered mode. Full data journaling also bypasses revoke use in `__ext4_forget()` because the journal does not need those revoke records.

`__ext4_journal_get_write_access()` checks the block device writeback errseq in no-journal mode. This protects against re-reading stale metadata after an asynchronous metadata write failed.

`__ext4_handle_dirty_metadata()` always marks buffers metadata, priority, and uptodate. With a valid journal handle it calls `jbd2_journal_dirty_metadata()`. Without a journal it marks the buffer dirty directly, optionally through the inode's metadata buffer tracker, and synchronously writes it for sync inodes.

## Dependencies
Depends on `ext4_jbd2.h`, JBD2 transaction APIs, ext4 error reporting from `super.c`, tracepoints in `trace/events/ext4.h`, buffer-head state, and metadata checksum feature state from `ext4.h`.

## Risks
Correctness hinges on passing the right handle type: no-journal pseudo-handles must never be treated as real JBD2 handles. Revoke decisions depend on data mode and metadata classification. Credit shortages, aborted journals, and async metadata writeback errors all feed into filesystem shutdown or read-only behavior, so silent handling mistakes can corrupt on-disk state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4_jbd2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4_jbd2.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/ext4_jbd2.h

## Summary
Declares ext4's journaling interface and transaction credit model over JBD2. It provides transaction block estimates, handle operation type IDs, wrappers for starting/stopping/extending/restarting transactions, metadata access helpers, inode fsync transaction tracking, data mode predicates, revoke-credit calculations, direct-I/O locking policy, and journal destruction sequencing.

## Main Responsibilities
- Defines transaction credit constants for data, metadata, xattr, quota, htree index, truncate/write reserve, and default revoke work.
- Defines handle type IDs used for logging and tracing, such as inode, write page, map blocks, directory, truncate, quota, resize, migrate, move extents, xattr, and extent conversion.
- Declares inode dirtying and inode-location journaling helpers.
- Declares concrete wrapper functions implemented in `ext4_jbd2.c`.
- Provides macros that attach caller function and line to write/create access, forget, dirty metadata, and journal stop operations.
- Provides inline wrappers for current handle, handle validity, sync flagging, force commit, ranged inode write/wait registration, and fsync transaction IDs.

## Important Behavior
`ext4_handle_valid()` treats small integer pseudo-handles below `EXT4_NOJOURNAL_MAX_REF_COUNT` as no-journal handles. Most wrapper helpers become no-ops when passed such handles.

`ext4_journal_ensure_credits_fn()` first tries to ensure or extend credits. If a restart is required, it runs a caller-supplied cleanup expression before restarting the transaction and returns `1` to signal that restart happened.

`ext4_free_metadata_revoke_credits()` scales metadata revoke credits by cluster ratio because freeing metadata blocks can free clusters. Data revoke credits are only needed for journaled data outside full data-journal mode, with extra boundary cluster accounting.

`ext4_should_dioread_nolock()` allows the no-`i_rwsem` direct-I/O read path only for regular extent-based files, when data journaling is off, the mount option is enabled, and delayed allocation is enabled.

`ext4_journal_destroy()` sets `EXT4_MF_JOURNAL_DESTROY`, forces any running commit, flushes pending superblock update work, then destroys the JBD2 journal and clears `s_journal`.

## Dependencies
Includes Linux `fs.h`, JBD2, and `ext4.h`. It depends on quota capability helpers, ext4 mount options, inode journaling state, and JBD2's handle, inode, transaction, and journal operations.

## Risks
Credit estimates are conservative contracts with many callers; underestimating them can force restarts or fail metadata updates. The pseudo-handle encoding is intentionally unusual and must be checked with `ext4_handle_valid()` before dereferencing. `ext4_journal_destroy()` relies on ordering with commit callbacks and superblock update work.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ext4_jbd2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents-test.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/extents-test.c

## Summary
KUnit test suite for ext4 extent split and conversion behavior. It constructs a minimal ext4 inode with one three-block extent, stubs selected extent and zeroout operations, then validates direct split/convert paths and higher-level `ext4_map_create_blocks()` paths for written-to-unwritten, unwritten-to-written, and zeroout fallback cases.

## Main Responsibilities
- Creates a synthetic superblock, `ext4_sb_info`, and `ext4_inode_info` suitable for extent tests.
- Builds a depth-0 extent tree rooted in the inode's `i_data`.
- Initializes the extent status tree and verifies it for high-level map-create tests.
- Provides KUnit static stubs for extent dirtying, forced insert failure, extent zeroout, and block zeroout.
- Exercises `ext4_split_convert_extents_test()` directly.
- Exercises `ext4_map_query_blocks()` plus `ext4_map_create_blocks()` for high-level initialized and unwritten conversion paths.
- Verifies final extent layout, unwritten flags, physical block mapping, extent status cache state, and zeroed data-buffer regions.

## Test Fixture
The fixture uses:
- `EXT_DATA_LBLK = 10`.
- `EXT_DATA_PBLK = 100`.
- `EXT_DATA_LEN = 3`.
- 4 KiB block size.
- One inode extent covering logical blocks `[10, 13)` and physical blocks `[100, 103)`.
- A separate three-block `k_data` buffer initialized with `X` to model underlying disk data for zeroout validation.

`extents_kunit_init()` allocates the mount/inode objects, registers the extent status shrinker, marks the inode as extents-based, configures optional zeroout, builds the initial extent header and extent, inserts the matching extent status entry, and activates common stubs. `extents_kunit_exit()` unregisters shrinker state, deactivates the synthetic superblock, and frees fixture allocations.

## Important Helpers
- `ext4_ext_insert_extent_stub()` returns `-ENOSPC` to force zeroout fallback.
- `ext4_ext_zeroout_stub()` zeroes the modeled data buffer for a whole extent.
- `ext4_issue_zeroout_stub()` zeroes the modeled data buffer for a logical/physical range and checks that logical and physical offsets match.
- `ext4_map_create_blocks_helper()` calls `ext4_map_query_blocks()` first to populate map flags and physical block data, then calls `ext4_map_create_blocks()`.
- `test_split_convert()` performs initial assertions, invokes the selected test path, verifies expected extents, optionally checks the extent status cache, and optionally verifies modeled zeroout results.

## Parameter Coverage
`test_split_convert_params` covers direct split/convert behavior:
- Unwritten to written conversion at the beginning, end, and middle of the extent.
- Written to unwritten conversion at the beginning, end, and middle.
- Zeroout fallback for the same split shapes, expecting one fully written extent and selective zeroing of regions outside or inside the requested split.

`test_convert_initialized_params` covers high-level conversion of initialized extents to unwritten through `ext4_map_create_blocks()`, including normal split and zeroout fallback cases.

`test_handle_unwritten_params` covers high-level handling of unwritten extents becoming written through end-I/O-style `EXT4_GET_BLOCKS_CONVERT` and non-end-I/O `EXT4_GET_BLOCKS_CREATE` paths, with and without zeroout fallback.

## KUnit Registration
The suite is named `ext4_extents_test`. It registers three parameterized cases using `KUNIT_CASE_PARAM_WITH_INIT()` because the file notes parsing limitations in the compact `KUNIT_ARRAY_PARAM()` form. The test module declares GPL licensing.

## Dependencies
Depends on KUnit, static stubs, ext4 core definitions, extent tree helpers, extent status helpers, and KUnit-only test exports from `ext4_extents.h` / `extents.c`.

## Risks
The fixture intentionally mocks only a narrow slice of ext4, so it is strong for extent split/conversion invariants but not a full integration test of journaling, allocation, writeback, or real block I/O. Global `k_ctx` means tests assume KUnit's fixture lifecycle isolates cases correctly. The expected zeroout matrix is sensitive to exact fallback semantics in extent conversion code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents-test.c -->