# subset-b-005652 Research

Grouped source research for ext4 ioctl handling and ext4 multiblock allocator KUnit coverage. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/ext4/ioctl.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/ioctl.c` implements ext4's file and filesystem ioctl surface, plus the VFS fileattr bridge and a small superblock-overhead update helper. It is the dispatch point for user-visible controls such as inode generation get/set, online resize, move extents, extent migration, delayed-allocation flushing, boot-loader inode swap, FITRIM, fscrypt and fsverity ioctls, forced shutdown, journal checkpointing, filesystem label/UUID get/set, superblock tunables, file flags, project quota IDs, and extent-status cache inspection. The source was read as a complete 2019-line file.

## Important APIs, Types, and Functions

The external entry points are `ext4_ioctl()`, `ext4_compat_ioctl()`, `ext4_fileattr_get()`, `ext4_fileattr_set()`, `ext4_force_shutdown()`, `ext4_reset_inode_seed()`, and `ext4_update_overhead()`. The central internal dispatcher is `__ext4_ioctl()`, which switches on ioctl command numbers and delegates to specialized helpers.

Superblock update helpers are built around `typedef void ext4_update_sb_callback(...)`, with callbacks `ext4_sb_setlabel()`, `ext4_sb_setuuid()`, `ext4_sb_setparams()`, and `set_overhead()`. `ext4_update_primary_sb()`, `ext4_update_backup_sb()`, and `ext4_update_superblocks_fn()` update the primary and sparse backup superblocks, journaling the primary and up to two backups before switching remaining backups to unjournaled dirty-buffer writes.

File and inode mutation helpers include `swap_inode_boot_loader()`, `swap_inode_data()`, `memswap()`, `ext4_ioctl_check_immutable()`, `dax_compatible()`, `ext4_dax_dontcache()`, `ext4_ioctl_setflags()`, and `ext4_ioctl_setproject()`. Filesystem-control helpers include `ext4_ioctl_group_add()`, `ext4_ioctl_shutdown()`, `ext4_ioc_getfsmap()`, `ext4_getfsmap_format()`, `ext4_ioctl_get_es_cache()`, `ext4_ioctl_checkpoint()`, `ext4_ioctl_setlabel()`, `ext4_ioctl_getlabel()`, `ext4_ioctl_getuuid()`, `ext4_ioctl_setuuid()`, `ext4_ioctl_get_tune_sb()`, and `ext4_ioctl_set_tune_sb()`.

Important data shapes include `struct getfsmap_info`, user ABI structures such as `struct fsmap_head`, `struct fsuuid`, `struct ext4_tune_sb_params`, `struct fiemap`, `struct move_extent`, and `struct ext4_new_group_data`, plus persistent ext4 objects `struct ext4_super_block`, `struct ext4_sb_info`, `struct ext4_inode_info`, `struct ext4_iloc`, and JBD2 `handle_t`.

## Control Flow

`ext4_ioctl()` is a thin wrapper over `__ext4_ioctl()`. The dispatcher obtains the file inode, superblock, and mount idmap, logs the command through `ext4_debug()`, and handles each supported ioctl with command-specific permission checks, user-copy validation, mount-write acquisition, inode locking, journaling, and subsystem delegation. Unsupported commands return `-ENOTTY`; compat ioctl translation maps selected 32-bit commands to native commands and uses `compat_ptr()` for shared handlers.

Simple metadata reads return data directly to userspace: version get returns `i_generation`, file label and UUID getters lock the superblock buffer and copy stable snapshots, get state reports selected in-memory inode state bits, and `FS_IOC_GETFSMAP` copies a header, validates reserved fields and offset constraints, converts VFS keys to ext4 fsmap keys, streams records through `ext4_getfsmap_format()`, and copies the final header back.

Write paths generally follow a common pattern: validate capability or owner checks, call `mnt_want_write_file()`, acquire any needed inode or resize locks, start an ext4 journal transaction if persistent metadata is being modified, update in-memory inode or superblock state, mark buffers or inode locations dirty, stop the journal, and drop the write reference. Examples include generation setting, flag setting, project ID changes, online resize, group add/extend, filesystem label and UUID changes, superblock tuning, and overhead update.

Online resize commands are serialized with `ext4_resize_begin()` and `ext4_resize_end()`. `EXT4_IOC_GROUP_EXTEND`, `EXT4_IOC_GROUP_ADD`, and `EXT4_IOC_RESIZE_FS` reject bigalloc where unsupported, call the corresponding resize helper, mark fast commits ineligible for resize, flush the journal if present, and register lazy inode-table initialization when group descriptor checksums and `INIT_INODE_TABLE` require it.

`EXT4_IOC_SWAP_BOOT` delegates to `swap_inode_boot_loader()`, which loads `EXT4_BOOT_LOADER_INO`, locks both inodes, rejects unsafe file types and flags, writes and invalidates page cache, waits for direct I/O, starts a journal transaction, initializes the boot loader inode if unused, swaps ext4 inode data and size/version fields, updates generation numbers and checksum seeds, adjusts quota accounting, marks both inodes dirty, and reverts the swap on selected failures.

The fileattr bridge has separate control flow from ioctl dispatch: `ext4_fileattr_get()` maps ext4 visible flags and project IDs into `struct file_kattr`; `ext4_fileattr_set()` masks requested flags to user-modifiable bits, checks immutable restrictions, calls `ext4_ioctl_setflags()`, and then calls `ext4_ioctl_setproject()`.

## State and Persistence Behavior

Persistent inode state changes include `i_generation`, timestamps, i_version, ext4 inode flags, extent-vs-indirect format migration, journal-data mode, project quota ID, boot-loader inode contents, and quota accounting. Inode flag updates reserve and dirty the inode location inside a journal transaction, while later journal-data or extent-format transitions call dedicated migration helpers after the flag transaction.

Persistent filesystem state changes are concentrated in superblock updates. `ext4_update_superblocks_fn()` guards against concurrent online resize with `EXT4_FLAGS_RESIZING`, journals the primary superblock and at most two backup superblocks, then updates remaining sparse backups without a journal. It recalculates superblock checksums where needed and syncs each dirty buffer. Label, UUID, tunable, and overhead updates all use this callback mechanism.

Forced shutdown modifies in-memory mount state by setting `EXT4_FLAGS_SHUTDOWN`, optionally freezing/thawing the block device or flushing and aborting the JBD2 journal, clearing discard, and reporting shutdown through `fserror_report_shutdown()`. Checkpointing persists journal state by calling `jbd2_journal_flush()` with optional discard or zeroout flags but does not directly modify file data.

Several ioctls intentionally invalidate or synchronize transient state. Setting immutable flushes regular-file direct I/O and dirty pages before setting the flag. DAX flag changes can mark an inode as not cacheable in dcache. Extent-status cache queries expose in-memory extent cache state through fiemap formatting, and `EXT4_IOC_CLEAR_ES_CACHE` drops that cache for an owner-capable caller.

## Dependencies and Integration Points

The file integrates with VFS ioctl dispatch, fileattr APIs, idmapped mounts, user-copy helpers, Linux capability checks, quota initialization and transfer, JBD2 journaling, fscrypt, fsverity, fsmap, fiemap, FITRIM/discard, block-device freeze/thaw, ext4 online resize, extent migration and move-extents, delayed allocation, extent-status cache, fast commit eligibility tracking, lazy inode-table initialization, ext4 tracing, and filesystem error reporting.

Header dependencies include `ext4_jbd2.h`, `ext4.h`, `fsmap.h`, `trace/events/ext4.h`, and Linux core headers for capabilities, compat ioctls, mount writes, quota operations, UUIDs, file attributes, and userspace access. User-visible ABI compatibility depends on command numbers and structures defined outside this file.

## Risks and Edge Cases

The highest-risk paths combine userspace ABI parsing, permissions, journaling, and persistent metadata updates. Superblock tuning can enable selected features online; validation must prevent unsupported feature clearing, incompatible encoding changes, excessive reserved blocks, invalid default hash algorithms, missing checksum seed support for UUID changes, and stable-inode UUID mutation. Backup superblock updates tolerate bad backup checksums but still require careful journal and buffer lifetime handling.

`swap_inode_boot_loader()` is particularly sensitive because it swaps inode data, sizes, quota usage, block counts, generation numbers, and checksum seeds while juggling page-cache invalidation and rollback. Incomplete rollback after one inode is dirtied could leave quota or boot-loader inode state inconsistent.

Flag mutation has subtle compatibility constraints: immutable files can only change in narrow ways, journal-data changes are capability-gated and rejected for active DAX inodes, casefold can only be toggled on empty directories with filesystem support, and DAX is mutually exclusive with verity-in-progress and inline/journal-data/encrypted semantics. Project quota transfer must account for xattr inode references under `xattr_sem`.

Resize and trim paths must reject unsupported bigalloc or noload+journal combinations. Compat ioctl translation is another ABI risk: command remapping must preserve pointer width and structure layout expectations. User-copy failure paths throughout the file return `-EFAULT` and must avoid partially committed changes before validation is complete.

## Test Signals

Useful coverage includes xfstests for `chattr`/fileattr flags, project quotas, immutable/append-only behavior, DAX flag interactions, casefold enablement, online grow/group add/group extend, `EXT4_IOC_MOVE_EXT`, `EXT4_IOC_SWAP_BOOT`, FITRIM, delayed-allocation block allocation, fscrypt policy/key ioctls, fsverity ioctls, forced shutdown modes, journal checkpoint flags, filesystem label and UUID get/set, and tune-superblock feature toggling.

Important negative tests should inject bad userspace pointers, unsupported feature masks, missing capabilities, readonly mounts, quota files, bigalloc resize attempts, metadata checksum generation changes, stable-inode UUID mutation, invalid fsmap keys, invalid checkpoint flag combinations, zeroout checkpoint warnings, and journal or buffer I/O errors. Runtime signals include `trace_ext4_update_sb`, `trace_ext4_shutdown`, `trace_ext4_getfsmap_*`, `ext4_msg()` errors, `ext4_warning()` messages, and `ext4_std_error()` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mballoc-test.c -->
# sources/distributed-fs/ceph-client/fs/ext4/mballoc-test.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/mballoc-test.c` is a KUnit test module for ext4 multiblock allocation internals. It builds a synthetic ext4 superblock, stubs the block bitmap and group descriptor accessors used by mballoc, initializes the real mballoc backend, and verifies allocation, freeing, bitmap marking, buddy generation, and buddy mutation behavior over several block-size and cluster-layout configurations. The source was read as a complete 1003-line file.

## Important APIs, Types, and Functions

The local test harness types are `struct mbt_grp_ctx`, which owns a fake block bitmap buffer head, fake group descriptor, and descriptor buffer head for one block group; `struct mbt_ctx`, which holds an array of group contexts; `struct mbt_ext4_super_block`, which embeds a fake on-disk superblock, `struct ext4_sb_info`, and test context; and `struct mbt_ext4_block_layout`, which parameterizes block size, cluster bits, blocks per group, group count, and descriptor size.

Harness setup and teardown functions include `mbt_alloc_inode()`, `mbt_free_inode()`, `mbt_kill_sb()`, `mbt_mb_init()`, `mbt_mb_release()`, `mbt_ext4_alloc_super_block()`, `mbt_ext4_free_super_block()`, `mbt_init_sb_layout()`, `mbt_grp_ctx_init()`, `mbt_grp_ctx_release()`, `mbt_ctx_init()`, `mbt_ctx_release()`, `mbt_kunit_init()`, and `mbt_kunit_exit()`.

Static-stub replacements are `ext4_read_block_bitmap_nowait_stub()`, `ext4_wait_block_bitmap_stub()`, `ext4_get_group_desc_stub()`, and `ext4_mb_mark_context_stub()`. They redirect mballoc internals to the synthetic bitmaps and descriptors.

Test helpers include `mbt_ctx_mark_used()`, `mbt_ctx_bitmap()`, `mbt_generate_test_ranges()`, `validate_free_blocks_simple()`, `test_free_blocks_simple_range()`, `test_mark_diskspace_used_range()`, `mbt_generate_buddy()`, `mbt_validate_group_info()`, `do_test_generate_buddy()`, `test_mb_mark_used_range()`, and `test_mb_free_blocks_range()`. KUnit cases are `test_new_blocks_simple()`, `test_free_blocks_simple()`, `test_mb_generate_buddy()`, `test_mb_mark_used()`, `test_mb_free_blocks()`, `test_mark_diskspace_used()`, and slow case `test_mb_mark_used_cost()`.

## Control Flow

KUnit enters through `mbt_test_suite`, which names the suite `ext4_mballoc_test`, supplies `mbt_kunit_init()` and `mbt_kunit_exit()`, and registers parameterized test cases across `mbt_test_layouts`. `KUNIT_ARRAY_PARAM()` creates layout parameters for 1 KiB, 4 KiB, and 64 KiB block sizes, all with `cluster_bits = 3`, four groups, 8192 blocks per group, and 64-byte group descriptors.

`mbt_kunit_init()` allocates a superblock through `sget()`, embeds ext4 private state in `struct mbt_ext4_super_block`, initializes blockgroup locks and layout fields, allocates per-group fake bitmaps/descriptors, activates KUnit static stubs for bitmap and descriptor access, calls `mbt_mb_init()` to run the real `ext4_mb_init()`, initializes free and dirty cluster counters, and stores the superblock in `test->priv`.

`mbt_ctx_init()` sets each fake group bitmap to contain all valid clusters free and all beyond-end bits used, initializes free-cluster counts in the fake descriptor, and marks the first cluster of group zero used so simple allocation does not choose a block that fails ext4 superblock block-validity checks. `mbt_kunit_exit()` reverses setup by releasing counters, mballoc state, fake block device and queue, per-group bitmap memory, blockgroup lock state, and the synthetic superblock.

The simple allocation test calls `ext4_mb_new_blocks_simple_test()` repeatedly: first expecting the goal block, then the next cluster after the goal, then the first cluster in a later group after the goal group is full, then an earlier group after later groups are full, and finally an allocation failure after all groups are full.

Freeing and marking tests generate random non-overlapping ranges within equal slices of a group. `test_free_blocks_simple()` first marks every cluster used, frees a range through `ext4_free_blocks_simple_test()`, and validates only that range became free in the goal group. `test_mark_diskspace_used()` calls `ext4_mb_mark_diskspace_used_test()` for each generated range and checks the fake bitmap has exactly that contiguous used range.

Buddy tests construct expected buddy and group-info state independently with `mbt_generate_buddy()`, then compare it with ext4 internals. `test_mb_generate_buddy()` checks `ext4_mb_generate_buddy_test()` from arbitrary bitmap ranges. `test_mb_mark_used()` loads a real `struct ext4_buddy`, applies `mb_mark_used_test()`, updates the independent bitmap, regenerates expected buddy data, and compares both buddy bytes and group counters. `test_mb_free_blocks()` starts from a fully used group, frees ranges with `mb_free_blocks_test()`, and performs the same comparison. `test_mb_mark_used_cost()` repeats random mark/free cycles 100000 times and logs elapsed jiffies for a slow performance signal.

## State and Persistence Behavior

All state is in-memory KUnit fixture state; the module does not mount or write a real filesystem. The synthetic `struct super_block` has enough fields populated for ext4 mballoc to operate: block size, group geometry, cluster ratio, descriptor sizing, `s_es`, blockgroup lock, inode list, super operations, fake block device, request queue, buddy cache, and percpu counters.

Fake persistent metadata is represented by in-memory block bitmaps and group descriptors in `mbt_grp_ctx`. Stubs return these objects to real ext4 mballoc code, so tests observe mutations through bitmap bits, descriptor free-cluster counts, and `struct ext4_group_info` buddy counters. `mbt_mb_init()` and `mbt_mb_release()` create and destroy real mballoc backend state, including the buddy cache inode and counters.

Random test ranges are transient and generated separately per test iteration. Several helper paths explicitly skip zero-length ranges because the tested production functions warn or BUG on zero lengths, so the test avoids invalid inputs rather than asserting their handling.

## Dependencies and Integration Points

The file depends on KUnit, KUnit static stubs, Linux random helpers, ext4 core declarations from `ext4.h`, and mballoc declarations from `mballoc.h`. It is tightly integrated with test-only symbols exposed by the mballoc implementation, including `ext4_mb_new_blocks_simple_test()`, `ext4_free_blocks_simple_test()`, `ext4_mb_mark_diskspace_used_test()`, `ext4_mb_generate_buddy_test()`, `ext4_mb_load_buddy_test()`, `ext4_mb_unload_buddy_test()`, `mb_mark_used_test()`, `mb_free_blocks_test()`, `mb_find_next_zero_bit_test()`, `mb_find_next_bit_test()`, and bit manipulation helpers.

Static stubbing lets the suite reuse production mballoc behavior while replacing filesystem I/O dependencies. `ext4_read_block_bitmap_nowait_stub()` hands out a referenced fake buffer head, `ext4_wait_block_bitmap_stub()` marks it uptodate and verified, `ext4_get_group_desc_stub()` exposes the fake descriptor, and `ext4_mb_mark_context_stub()` applies direct bitmap mutations for mark-context calls.

The test module registers with `kunit_test_suites()` and declares `MODULE_LICENSE("GPL")`, so it is built and run as a kernel KUnit suite when the relevant ext4 test configuration is enabled.

## Risks and Edge Cases

The harness deliberately models only the subset of ext4 state needed by mballoc. That keeps the tests fast, but it risks diverging from real mount-time state if mballoc starts depending on additional superblock, block-device, journal, or group-descriptor fields. Stub behavior must stay aligned with production helper side effects, especially buffer-head reference ownership, uptodate/verified flags, and group descriptor updates.

Random range generation increases coverage but can reduce reproducibility unless the KUnit random seed is captured by the broader test runner. Zero-length ranges are skipped because production helpers expect non-zero lengths in some paths; this means invalid-length handling is not tested here. Tests that compare raw buddy memory depend on stable buddy layout and offsets for each block size and cluster geometry.

The 64 KiB block-size layout is skipped for buddy-cache load/mutation tests when block size exceeds `PAGE_SIZE`, because the buddy cache assumes a page contains at least one block. That skip is intentional but leaves those paths covered only for smaller layouts on systems with smaller page sizes. The slow cost test loops 100000 times and logs timing rather than asserting a threshold, so it is a performance observation rather than a regression gate.

## Test Signals

Primary success signals are KUnit assertions comparing expected block numbers, allocation errors, exact bitmap transitions, buddy-buffer byte equality, and `struct ext4_group_info` counters such as `bb_first_free`, `bb_fragments`, `bb_free`, `bb_largest_free_order`, and `bb_counters[]`. The suite covers allocation preference around goal groups, fallback before and after a goal group, no-space failure, freeing exact ranges, diskspace marking, buddy generation, mark-used mutation, free-block mutation, and a slow mark-used cost path.

Useful failure diagnostics come from assertion messages that print expected and found blocks or counter indexes. Additional validation should run the suite under different page sizes and with KASAN/KCSAN or fault injection for allocation failures in setup paths, because this file has detailed cleanup paths for partial superblock, group-context, mballoc, and percpu-counter initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mballoc-test.c -->
