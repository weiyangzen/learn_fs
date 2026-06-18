# Group Research: group_742_linux_sources_os_linux_linux_fs_ext4_ioctl_c_sources_os_linux_linux__ef510fabe210

Scope checked against `Docs/research_subset_a.md`: both files are under `sources/os/linux/linux`, which is included in subset A. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/ioctl.c -->
# File Research: sources/os/linux/linux/fs/ext4/ioctl.c

## Purpose

`ioctl.c` implements ext4's ioctl and file attribute control plane. It exposes administrative operations for inode generation numbers, flags, project IDs, online resize, extent migration/move, delayed allocation flushing, boot-loader inode swapping, filesystem trim, encryption and verity ioctls, extent status cache inspection, forced shutdown, journal checkpointing, filesystem label/UUID updates, online superblock tuning, and overhead-cluster persistence.

## Main Entry Points

- `ext4_ioctl()` forwards all native ioctl handling into `__ext4_ioctl()`.
- `ext4_compat_ioctl()` maps selected 32-bit compat ioctl command numbers and argument layouts to the native implementation.
- `ext4_fileattr_get()` and `ext4_fileattr_set()` implement VFS file-attribute integration for ext4 flags and project IDs.
- `ext4_force_shutdown()` performs the forced shutdown operation used by `EXT4_IOC_SHUTDOWN`.
- `ext4_update_overhead()` persists recalculated filesystem overhead cluster counts through the shared superblock update helper.
- `ext4_reset_inode_seed()` recomputes per-inode metadata checksum seeds after inode generation changes.

## Superblock Update Helpers

- `ext4_update_primary_sb()` journals and synchronously writes the primary superblock after invoking a caller-supplied callback.
- `ext4_update_backup_sb()` updates backup superblocks, optionally under a journal handle, and validates metadata checksums before modifying checksum-protected backups.
- `ext4_update_superblocks_fn()` serializes against online resize with `EXT4_FLAGS_RESIZING`, journals the primary superblock and at most two backups, then updates remaining backups without journaling.
- Callback helpers include `ext4_sb_setlabel()`, `ext4_sb_setuuid()`, `ext4_sb_setparams()`, and `set_overhead()`.

These helpers centralize checksum recalculation, buffer locking, dirty metadata handling, writeback, and backup-superblock iteration for ioctl paths that mutate superblock fields.

## Inode Data Swapping

- `memswap()` provides a bytewise swap utility.
- `swap_inode_data()` swaps `i_data`, selected ext4 flags, disk size, VFS size, timestamps, version, and extent status cache state between two inodes.
- `swap_inode_boot_loader()` implements `EXT4_IOC_SWAP_BOOT` by swapping a regular user file with `EXT4_BOOT_LOADER_INO`.

The boot-loader swap path performs strong validation before modifying metadata: the source must be a single-link regular file, not a swapfile, encrypted file, journal-data file, or inline-data file. It requires ownership/capability checks, `CAP_SYS_ADMIN`, write access, page writeback completion, DIO quiescence, page-cache truncation, a journal transaction, fast-commit exclusion, and double `i_data_sem` write locking.

## Flag and File Attribute Handling

- `ext4_ioctl_check_immutable()` prevents changing anything except the immutable bit itself while an inode is already immutable.
- `ext4_dax_dontcache()` marks non-directory dentries uncached when the persistent DAX flag changes outside forced DAX mount modes.
- `dax_compatible()` rejects DAX flag changes that conflict with mutually exclusive inode flags or verity setup.
- `ext4_ioctl_setflags()` applies user-modifiable ext4 inode flags under a journal transaction, handles DAX cache effects, ctime/version updates, journal-data flag transitions, and extents/indirect format migration.
- `ext4_ioctl_setproject()` changes project IDs when project quota support and inode extra size allow it, transferring quota usage under `xattr_sem`.

`ext4_fileattr_set()` is the VFS-facing wrapper. It masks user-visible-but-not-settable bits for compatibility with `chattr`, validates mode-specific flags, enforces immutable rules, then delegates to flag and project-ID setters.

## Filesystem Map, Extent Cache, and State Queries

- `ext4_ioc_getfsmap()` validates `FS_IOC_GETFSMAP` keys, translates external `fsmap` records to ext4 internal records, streams mappings via `ext4_getfsmap()`, and marks the final returned record with `FMR_OF_LAST`.
- `ext4_getfsmap_format()` copies one translated mapping record to userspace and tracks last-record flags.
- `ext4_ioctl_get_es_cache()` exposes the inode extent-status cache through a fiemap-shaped userspace interface while guarding against extent-count overflow.
- `EXT4_IOC_CLEAR_ES_CACHE` clears an inode's extent status cache after owner/capability checks.
- `EXT4_IOC_GETSTATE` reports selected internal inode state bits such as extent precache, new inode, new directory entry, and delayed-allocation-close state.

## Resize and Allocation Control

Handled ioctl cases include `EXT4_IOC_GROUP_EXTEND`, `EXT4_IOC_GROUP_ADD`, `EXT4_IOC_RESIZE_FS`, `EXT4_IOC_MIGRATE`, `EXT4_IOC_ALLOC_DA_BLKS`, `EXT4_IOC_MOVE_EXT`, `EXT4_IOC_PRECACHE_EXTENTS`, and `FITRIM`.

Resize operations reject bigalloc online resize, use `ext4_resize_begin()` / `ext4_resize_end()`, take write access with `mnt_want_write_file()`, mark fast commit ineligible, flush the journal when present, and register lazy inode-table initialization after successful group growth when applicable.

## Shutdown and Journal Checkpointing

- `ext4_ioctl_shutdown()` requires `CAP_SYS_ADMIN`, copies shutdown flags from userspace, and delegates to `ext4_force_shutdown()`.
- `ext4_force_shutdown()` supports default freeze/thaw shutdown, shutdown with journal commit/abort, and shutdown with journal abort but no log flush. It sets `EXT4_FLAGS_SHUTDOWN`, clears discard, traces the event, and reports shutdown through `fserror_report_shutdown()`.
- `ext4_ioctl_checkpoint()` requires `CAP_SYS_ADMIN`, validates checkpoint flags, rejects discard when the journal device cannot discard, supports dry-run mode, and calls `jbd2_journal_flush()` under the journal update lock.

## Label, UUID, and Tune-Superblock Ioctls

- `ext4_ioctl_setlabel()` copies a null-terminated label with `EXT4_LABEL_MAX` enforcement, clears trailing bytes, and updates primary and backup superblocks.
- `ext4_ioctl_getlabel()` returns the current label as a padded null-terminated userspace string.
- `ext4_ioctl_getuuid()` implements length-probing and UUID retrieval through `struct fsuuid`.
- `ext4_ioctl_setuuid()` requires `CAP_SYS_ADMIN`, rejects filesystems where UUID changes would break checksum or stable-inode guarantees, validates `struct fsuuid`, then updates superblocks.
- `ext4_ioctl_get_tune_sb()` reports supported online tune operations, current tunable values, current feature flags, and masks describing which feature bits can be set or cleared online.
- `ext4_ioctl_set_tune_sb()` validates requested tune changes, translates whole-feature-set requests into set/clear masks, restricts online feature edits to supported additions, handles casefold encoding defaults, initializes directory-index hash seed defaults, and persists the changes through superblock update callbacks.

## Ioctl Dispatch Coverage

`__ext4_ioctl()` dispatches ext4-private and generic filesystem ioctls: version/generation get/set, online resize/group operations, extent move and migration, delayed allocation, boot-loader swap, trim, extent precache, fscrypt, fsverity, extent status cache operations, shutdown, checkpoint, label, UUID, tune-superblock operations, and `FS_IOC_GETFSMAP`.

Most mutating cases explicitly acquire mount write access and perform owner/capability checks before journaling or invoking lower ext4 subsystems.

## Compat Handling

`ext4_compat_ioctl()` remaps legacy 32-bit command numbers for generation, resize reservation, and group operations. `EXT4_IOC32_GROUP_ADD` manually copies the compat structure field by field into `struct ext4_new_group_data`; other compatible pointer-based ioctls are forwarded through `compat_ptr()`. Unknown compat commands return `-ENOIOCTLCMD`.

## Dependencies

This file depends on VFS inode/file/dentry infrastructure, mount write accounting, buffer heads, block-device freeze/thaw/discard capabilities, JBD2 journaling, quota transfer, fscrypt, fsverity, fsmap translation, ext4 resize, extents, fast commit ineligibility tracking, DAX state, usercopy helpers, capability checks, and ext4 tracing/error reporting.

## Research Notes

`ioctl.c` is a high-risk administrative boundary because it accepts userspace-controlled operations that can mutate persistent metadata. Its dominant invariants are permission gating, feature gating, mount write acquisition, resize serialization, journal transaction ordering, checksum preservation, and careful rollback for boot-loader inode swapping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/mballoc-test.c -->
# File Research: sources/os/linux/linux/fs/ext4/mballoc-test.c

## Purpose

`mballoc-test.c` is a KUnit test module for ext4 multiblock allocation internals. It builds a lightweight synthetic ext4 superblock, group descriptors, and block bitmaps, stubs selected ext4 metadata accessors, and verifies allocator behavior for simple allocation/free paths, buddy generation, buddy mark/free operations, diskspace marking, and a slow-path cost measurement.

## Test Harness Structures

- `struct mbt_grp_ctx` stores one synthetic group context: bitmap buffer head, placeholder ext4 group descriptor, and placeholder descriptor buffer head.
- `struct mbt_ctx` owns the array of group contexts.
- `struct mbt_ext4_super_block` embeds an on-disk ext4 superblock, in-memory ext4 superblock info, and test-only group context.
- `struct mbt_ext4_block_layout` parameterizes block size, cluster bits, blocks per group, group count, and descriptor size.
- `struct test_range` represents a generated group-local start/length pair.

The `MBT_SB`, `MBT_CTX`, and `MBT_GRP_CTX` macros recover test harness state from a kernel `struct super_block`.

## Synthetic Superblock and mballoc Setup

- `mbt_alloc_inode()` allocates `struct ext4_inode_info`, initializes ext4 inode locks/state, and returns its VFS inode.
- `mbt_free_inode()` frees the ext4 inode wrapper.
- `mbt_sops`, `mbt_kill_sb()`, `mbt_init_fs_context()`, `mbt_fs_type`, and `mbt_set()` provide enough filesystem scaffolding for `sget_fc()` and `generic_shutdown_super()`.
- `mbt_ext4_alloc_super_block()` allocates the combined test superblock object, obtains a kernel `super_block`, initializes the ext4 blockgroup lock, wires `s_fs_info`, and releases the mount semaphore.
- `mbt_ext4_free_super_block()` frees the blockgroup lock, deactivates the superblock, and releases the wrapper object.
- `mbt_init_sb_layout()` fills ext4 geometry fields from the current test parameter.
- `mbt_mb_init()` allocates a fake block device and request queue, initializes `s_inodes` and super operations, calls `ext4_mb_init()`, and initializes free/dirty cluster percpu counters.
- `mbt_mb_release()` tears down percpu counters, mballoc state, and fake block-device memory.

## Group Bitmap Context

- `mbt_grp_ctx_init()` allocates a zeroed block bitmap, marks bits beyond the valid cluster count as used, and initializes the descriptor free-cluster count.
- `mbt_ctx_init()` allocates all group contexts after layout setup, initializes every group bitmap, and marks the first data cluster in group 0 as used so allocator tests do not select an invalid first filesystem block.
- `mbt_ctx_release()` releases all synthetic group bitmaps.
- `mbt_ctx_mark_used()` marks a range used in a chosen group bitmap.
- `mbt_ctx_bitmap()` returns a raw bitmap pointer for assertions and expected-state generation.

## Static Stubs

KUnit static stubs replace selected ext4 functions while tests run:

- `ext4_read_block_bitmap_nowait_stub()` returns the synthetic group bitmap buffer and increments its buffer-head reference count.
- `ext4_wait_block_bitmap_stub()` marks the synthetic bitmap buffer as uptodate, bitmap-uptodate, and verified.
- `ext4_get_group_desc_stub()` returns the synthetic group descriptor and optional descriptor buffer head.
- `ext4_mb_mark_context_stub()` mutates the synthetic bitmap for mark/free calls without doing real journal or metadata IO.

`mbt_kunit_init()` allocates the synthetic superblock, applies the current layout parameter, initializes group contexts, activates these static stubs, initializes mballoc, and stores the superblock in `test->priv`. `mbt_kunit_exit()` releases mballoc state, group contexts, and the superblock.

## Allocation and Free Tests

- `test_new_blocks_simple()` validates allocation exactly at a free goal, next allocation after the same goal, fallback to the next group, fallback to an earlier group, and error reporting when no blocks are available.
- `mbt_generate_test_ranges()` creates per-test ranges spread across a group.
- `validate_free_blocks_simple()` verifies that only the expected group and expected range became free.
- `test_free_blocks_simple_range()` frees one range through `ext4_free_blocks_simple_test()` and validates bitmap state.
- `test_free_blocks_simple()` fills all groups, generates ranges, and tests simple free behavior in the goal group.
- `test_mark_diskspace_used_range()` validates that `ext4_mb_mark_diskspace_used_test()` marks exactly the requested range.
- `test_mark_diskspace_used()` runs diskspace marking across generated ranges.

## Buddy Generation and Mutation Tests

- `mbt_generate_buddy()` independently builds the expected mballoc buddy bitmap and group statistics from a raw block bitmap.
- `mbt_validate_group_info()` compares key `struct ext4_group_info` fields and buddy counters.
- `do_test_generate_buddy()` compares independently generated buddy state against `ext4_mb_generate_buddy_test()`.
- `test_mb_generate_buddy()` progressively marks generated used ranges and validates ext4 buddy generation after each change.
- `test_mb_mark_used_range()` calls `mb_mark_used_test()` under the group lock, updates an independent bitmap, regenerates expected buddy state, and compares it with the loaded ext4 buddy.
- `test_mb_mark_used()` loads a buddy for the goal group and validates repeated mark-used operations.
- `test_mb_free_blocks_range()` calls `mb_free_blocks_test()` under the group lock, updates an independent bitmap, regenerates expected buddy state, and compares it with the loaded ext4 buddy.
- `test_mb_free_blocks()` first marks the entire group used, then validates repeated free operations against expected buddy state.

Buddy-cache tests skip layouts where the filesystem block size exceeds `PAGE_SIZE`, because the buddy cache assumes each page contains at least one block.

## Cost Measurement

`test_mb_mark_used_cost()` is marked `KUNIT_SPEED_SLOW`. It repeatedly generates ranges, times `mb_mark_used_test()` loops using `jiffies`, frees the same ranges, totals elapsed jiffies across `COUNT_FOR_ESTIMATE` iterations, and reports the cost with `kunit_info()`.

## Test Parameters and Suite Registration

`mbt_test_layouts` defines three layouts: 1 KiB, 4 KiB, and 64 KiB block sizes, all with cluster bits 3, 8192 blocks per group, 4 groups, and 64-byte descriptors.

`KUNIT_ARRAY_PARAM()` exposes these layouts to every test case. `mbt_test_cases` registers parameterized correctness tests plus the slow cost test. `mbt_test_suite` names the suite `ext4_mballoc_test`, attaches init/exit hooks, and `kunit_test_suites()` registers it as a GPL module.

## Dependencies

This file depends on KUnit, KUnit static stubs, Linux filesystem context helpers, random number generation, ext4 core definitions, and `mballoc.h` internals. It intentionally calls test-visible ext4 allocator functions such as `ext4_mb_new_blocks_simple_test()`, `ext4_free_blocks_simple_test()`, `ext4_mb_mark_diskspace_used_test()`, `ext4_mb_generate_buddy_test()`, `mb_mark_used_test()`, `mb_free_blocks_test()`, `ext4_mb_load_buddy_test()`, and `ext4_mb_unload_buddy_test()`.

## Research Notes

The test design avoids real disk IO by replacing bitmap and group-descriptor access with synthetic in-memory state, while still exercising ext4's actual mballoc logic. The strongest correctness pattern is dual implementation: tests build expected buddy/bitmap/group-info state independently and then compare it against ext4-generated state. The random range generator broadens coverage within each layout, but the suite remains deterministic only to the extent that KUnit/kernel random behavior is controlled by the test environment.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/mballoc-test.c -->