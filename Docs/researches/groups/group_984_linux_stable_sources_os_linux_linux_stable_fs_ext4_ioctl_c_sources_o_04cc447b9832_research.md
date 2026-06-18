# Group Research: group_984_linux_stable_sources_os_linux_linux_stable_fs_ext4_ioctl_c_sources_o_04cc447b9832

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/ioctl.c

## Summary
Implements ext4's ioctl and file-attribute control plane. This file handles user-visible administrative operations for inode versions, extent migration, online resize, extent movement, delayed allocation flushing, boot-loader inode swapping, trim/discard, encryption and verity ioctls, extent-status cache inspection, forced shutdown, journal checkpointing, filesystem label/UUID mutation, tune-superblock parameters, and persistent overhead updates.

## Main Responsibilities
- Dispatches ext4-specific and generic filesystem ioctls through `__ext4_ioctl()`.
- Provides 32-bit compatibility translation in `ext4_compat_ioctl()`.
- Updates primary and backup superblocks through a callback-based helper used for label, UUID, tune parameters, and overhead-cluster changes.
- Implements file attribute get/set integration for VFS `fileattr` APIs, including ext4 user-visible flags and project IDs.
- Enforces capability, ownership, write-mount, feature, immutable, DAX, quota-file, journaling, and readonly constraints before mutating filesystem state.
- Wraps online resize operations and ensures journal flushing / fast-commit ineligibility after resize.
- Routes fscrypt and fsverity ioctl requests only when corresponding ext4 features are enabled.

## Superblock Update Path
`ext4_update_primary_sb()` journals and updates the mounted primary superblock buffer, calls a caller-supplied `ext4_update_sb_callback`, recomputes the primary checksum, handles previous write I/O errors, dirties metadata, and synchronously writes the buffer.

`ext4_update_backup_sb()` updates one backup superblock if the target group has one. It handles group-0 offset rules, validates metadata checksums before modification, optionally journals the buffer, recomputes backup checksums when enabled, marks or journals the buffer dirty, and synchronously writes it.

`ext4_update_superblocks_fn()` serializes against online resize with `EXT4_FLAGS_RESIZING`, starts a journal transaction for the primary superblock plus at most two backups, then walks sparse-super backup groups via `ext4_list_backups()`. After two successful backup updates, remaining backups are written without a journal. The file explicitly relies on fsck being able to repair backup-superblock divergence if a late non-journaled backup update is interrupted.

Callback users include:
- `ext4_sb_setlabel()` for volume labels.
- `ext4_sb_setuuid()` for filesystem UUID.
- `ext4_sb_setparams()` for tune-superblock parameters.
- `set_overhead()` for `s_overhead_clusters`.

## Inode and File Attribute Mutation
`ext4_fileattr_get()` reports ext4 visible flags and project ID through `struct file_kattr`, masking `FS_PROJINHERIT_FL` for regular files.

`ext4_fileattr_set()` validates requested flags against `EXT4_FL_USER_VISIBLE`, masks to `EXT4_FL_USER_MODIFIABLE`, applies mode-specific flag masking, checks immutable-file restrictions, then calls `ext4_ioctl_setflags()` and `ext4_ioctl_setproject()`.

`ext4_ioctl_setflags()` protects quota files, requires `CAP_SYS_RESOURCE` for journal-data mode changes, validates DAX mutual exclusions, validates casefold enablement only for empty directories on casefold-capable filesystems, flushes regular-file pages before setting immutable, journals inode flag updates, updates ctime and inode version, drops DAX inode cache state when needed, and performs post-transaction journal-mode or extents/indirect-format migration.

`ext4_ioctl_setproject()` exists in a quota-enabled and quota-disabled form. With quotas enabled, it requires project feature support and large-enough inodes, expands extra inode size if needed, initializes quotas, transfers project quota accounting under `xattr_sem`, updates `i_projid`, and journals the inode. Without quota support, only the default project ID is accepted.

`ext4_ioctl_check_immutable()` prevents changing any inode state other than setting immutable itself while immutable is already set, including project ID changes.

## Boot Loader Inode Swap
`swap_inode_boot_loader()` swaps a regular file with `EXT4_BOOT_LOADER_INO`. It:
- Loads the special inode with `EXT4_IGET_SPECIAL | EXT4_IGET_BAD`.
- Locks both inodes and rejects multi-link, non-regular, swapfile, encrypted, journal-data, and inline-data files.
- Requires owner/capability permission plus `CAP_SYS_ADMIN`.
- Flushes and invalidates page cache, waits for direct I/O, and truncates cached pages.
- Starts a move-extents journal transaction and marks fast commit ineligible.
- Initializes the boot-loader inode if it has never been a regular file.
- Swaps extent/inline `i_data`, selected ext4 flags, timestamps, inode version, sizes, and disk sizes through `swap_inode_data()`.
- Regenerates inode generations and metadata checksum seeds via `ext4_reset_inode_seed()`.
- Marks both inodes dirty and adjusts quota accounting so the boot-loader inode is not charged.
- Reverts the swap on inode dirtying or quota-transfer failure.

This path is heavily ordered around page-cache invalidation, direct-I/O drain, `i_data_sem`, journaling, and quota updates.

## Online Resize and Allocation-Related Ioctls
`EXT4_IOC_GROUP_EXTEND`, `EXT4_IOC_GROUP_ADD`, and `EXT4_IOC_RESIZE_FS` all enter `ext4_resize_begin()` / `ext4_resize_end()`, reject bigalloc where unsupported, require write access, call the appropriate resize helper, mark fast commit ineligible, flush the journal when present, and register lazy inode-table initialization when a new group is added on group-descriptor-checksummed filesystems.

`EXT4_IOC_MOVE_EXT` validates read/write access on the original file, writable donor fd, copies `struct move_extent`, calls `ext4_move_extents()`, and copies back `moved_len`.

`EXT4_IOC_MIGRATE` requires inode ownership/capability, write access, inode lock, and calls `ext4_ext_migrate()`.

`EXT4_IOC_ALLOC_DA_BLKS` forces delayed allocation blocks through `ext4_alloc_da_blocks()`.

`EXT4_IOC_PRECACHE_EXTENTS` takes a shared inode lock and calls `ext4_ext_precache()`.

## Mapping, Cache, Trim, Shutdown, and Checkpoint
`FS_IOC_GETFSMAP` is handled by `ext4_ioc_getfsmap()`, which validates reserved fields and allowed file-offset sentinel values, converts external keys to internal ext4 fsmap keys, invokes `ext4_getfsmap()`, copies records through `ext4_getfsmap_format()`, and marks the last record with `FMR_OF_LAST` when appropriate.

`EXT4_IOC_GET_ES_CACHE` copies a `struct fiemap`, validates extent count against `FIEMAP_MAX_EXTENTS`, calls `ext4_get_es_cache()`, and copies mapped extent counts and flags back to userspace. `EXT4_IOC_CLEAR_ES_CACHE` requires ownership/capability and clears the inode extent-status cache.

`FITRIM` requires `CAP_SYS_ADMIN`, discard support, and a journal-replayed filesystem. It rejects `NOLOAD` journaled mounts, calls `ext4_trim_fs()`, and returns the updated trim range.

`EXT4_IOC_SHUTDOWN` requires `CAP_SYS_ADMIN` and calls `ext4_force_shutdown()`. Shutdown supports default freeze/thaw, journal flush+abort, and no-flush abort modes, sets `EXT4_FLAGS_SHUTDOWN`, disables discard, traces the event, and reports filesystem shutdown to `fserror`.

`EXT4_IOC_CHECKPOINT` requires `CAP_SYS_ADMIN`, validates dry-run/discard/zeroout flags, requires a journal, checks discard support for journal-device discard, optionally returns early for dry run, and flushes the JBD2 journal under update lock. Zeroout emits a ratelimited warning because it can be slow.

`EXT4_IOC_GETSTATE` returns selected transient inode state bits such as extent precached, new inode, new directory entry, and delayed-allocation-on-close.

## Label, UUID, and Tune-Superblock Ioctls
`FS_IOC_GETFSLABEL` reads `s_volume_name` under the superblock buffer lock and returns a NUL-padded label. `FS_IOC_SETFSLABEL` requires `CAP_SYS_ADMIN`, copies at most `EXT4_LABEL_MAX + 1`, rejects overlong labels, zero-fills unused bytes, obtains write access, and updates primary/backups through the superblock callback path.

`EXT4_IOC_GETFSUUID` implements the `struct fsuuid` length-query convention. If `fsu_len` is zero, it writes back the required UUID size. Otherwise it requires length at least `UUID_SIZE`, zero flags, copies the UUID under the superblock buffer lock, and returns both header and UUID bytes.

`EXT4_IOC_SETFSUUID` requires `CAP_SYS_ADMIN`, rejects UUID changes when checksummed descriptors/metadata lack `csum_seed`, and rejects `stable_inodes`. It validates `struct fsuuid`, copies the UUID, obtains write access, and updates all relevant superblocks.

`EXT4_IOC_GET_TUNE_SB_PARAM` returns supported tune flags, current error behavior, mount counts, check interval/time, reserved blocks and IDs, default mount options, hash algorithm, RAID stride/stripe width, encoding fields, mount option string, feature masks, and masks describing which features can be set or cleared online.

`EXT4_IOC_SET_TUNE_SB_PARAM` validates capability, mount option string termination, supported operation flags, error behavior range, reserved-block limit, hash algorithm, mutually exclusive absolute-feature and edit-feature modes, and supported set/clear feature masks. It can translate absolute feature masks into set/clear operations. Supported online feature enabling includes dir_index, stable_inodes, extents, ea_inode, encrypt, csum_seed, largedir, casefold, large_file, dir_nlink, extra_isize, project, and verity; clearing feature bits is not supported. Enabling casefold auto-fills UTF-8 encoding defaults, validates encoding flags, and enabling dir_index initializes hash seed/default hash metadata if needed.

## Ioctl Dispatch
`__ext4_ioctl()` handles:
- `FS_IOC_GETFSMAP`.
- `EXT4_IOC_GETVERSION` / old variant.
- `EXT4_IOC_SETVERSION` / old variant, rejected when `metadata_csum` is enabled.
- Online resize ioctls: group extend, group add, resize fs.
- `EXT4_IOC_MOVE_EXT`, `EXT4_IOC_MIGRATE`, `EXT4_IOC_ALLOC_DA_BLKS`, `EXT4_IOC_SWAP_BOOT`.
- `FITRIM`.
- Extent precache and extent-status cache ioctls.
- fscrypt policy/key/nonce ioctls gated by `encrypt`.
- shutdown, checkpoint, label, UUID, tune-superblock ioctls.
- fsverity enable/measure/read-metadata ioctls gated by `verity`.

Unrecognized commands return `-ENOTTY`.

`ext4_ioctl()` is the thin public wrapper. `ext4_compat_ioctl()` remaps legacy 32-bit command numbers and handles compat group-add structure unpacking before delegating to `ext4_ioctl()` with a compat pointer.

## Synchronization and Lifetime
- Superblock mutations use buffer locks and journal write access where available.
- `EXT4_FLAGS_RESIZING` serializes superblock-wide updates against online resize.
- Write-intent operations use `mnt_want_write_file()` / `mnt_drop_write_file()`.
- Inode mutations use inode locks, quota initialization, `xattr_sem`, `i_data_sem`, direct-I/O waits, and page-cache writeback/invalidation depending on operation.
- Journal-sensitive operations mark fast commit ineligible for resize and boot-loader swap.
- Forced shutdown interacts with block-device freeze/thaw and JBD2 abort/flush semantics.

## Dependencies
Depends on ext4 core headers, JBD2 wrappers, resize, extents, mballoc-adjacent allocation state, fsmap conversion helpers, VFS ioctl/fileattr APIs, fscrypt, fsverity, quota APIs, buffer-head operations, block-device discard/freeze APIs, tracepoints, usercopy helpers, and filesystem error reporting.

## Risks
This file exposes high-privilege mutation paths directly to userspace, so validation is central. Risk areas include superblock backup update ordering, non-journaled backup writes, online feature enabling, UUID changes under checksum/stable-inode constraints, DAX flag interactions, immutable-file semantics, quota transfer during project-ID and boot-loader swap operations, resize journal flushing, and forced shutdown races with in-flight filesystem activity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mballoc-test.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/mballoc-test.c

## Summary
KUnit test suite for ext4 multiblock allocation internals. It builds a synthetic ext4 superblock and per-group bitmap/descriptor context, stubs selected ext4 bitmap and group-descriptor functions, initializes the real mballoc backend, and tests allocation, freeing, buddy generation, buddy mutation, diskspace marking, and mark-used cost behavior across several block and cluster layouts.

## Main Responsibilities
- Creates a minimal ext4 mount environment sufficient for `ext4_mb_init()` and mballoc test helpers.
- Provides synthetic per-group bitmap buffers and group descriptors.
- Stubs block bitmap reads, bitmap wait/verification, group descriptor lookup, and bitmap-marking context updates.
- Runs parameterized KUnit tests over multiple block-size layouts.
- Validates mballoc bitmap and buddy-cache state against independently generated expected state.
- Includes a slow cost-estimation test for repeated `mb_mark_used()` / `mb_free_blocks()` cycles.

## Test Fixture and Synthetic Filesystem
The fixture wraps ext4 state in:
- `struct mbt_ext4_super_block`, containing an on-disk superblock image, `struct ext4_sb_info`, and private test context.
- `struct mbt_ctx`, holding an array of per-group contexts.
- `struct mbt_grp_ctx`, holding a bitmap buffer head, group descriptor, and placeholder descriptor buffer head.

`mbt_ext4_alloc_super_block()` allocates this wrapper, obtains a VFS superblock with `sget()`, allocates and initializes ext4 block-group locking, wires `s_es`, `s_sb`, and `s_fs_info`, and drops the superblock umount lock. `mbt_ext4_free_super_block()` frees the block-group lock, deactivates the superblock, and frees the wrapper.

`mbt_init_sb_layout()` configures VFS block size, ext4 group count, blocks per group, cluster bits/ratio, clusters per group, descriptor size, descriptor-per-block values, first data block, and total block count from a parameterized layout.

`mbt_ctx_init()` allocates one group context per group, initializes each bitmap to free clusters plus any out-of-range bits marked used, sets group free-cluster counts, and marks the first cluster of group 0 used to avoid allocating the filesystem's first data block in ways that would fail block-validity checks.

`mbt_mb_init()` creates a fake block device and request queue, initializes `s_inodes` and `s_op`, calls real `ext4_mb_init()`, initializes free and dirty cluster percpu counters, and unwinds all resources on failure. `mbt_mb_release()` destroys counters, releases mballoc state, and frees fake block-device objects.

## Static Stubs
The suite uses KUnit static stubs for controlled I/O-free behavior:
- `ext4_read_block_bitmap_nowait_stub()` returns the synthetic group bitmap buffer and increments its buffer-head refcount to match caller expectations.
- `ext4_wait_block_bitmap_stub()` marks the bitmap buffer uptodate, bitmap-uptodate, and verified.
- `ext4_get_group_desc_stub()` returns the synthetic descriptor and optional placeholder descriptor buffer.
- `ext4_mb_mark_context_stub()` applies set/clear operations directly to the synthetic bitmap.

These stubs let real mballoc helper code run without disk I/O or real group descriptor blocks.

## Test Cases
`test_new_blocks_simple()` verifies `ext4_mb_new_blocks_simple_test()`:
- Allocates at the requested goal block.
- Allocates the next cluster after the goal when the goal is already used.
- Falls forward to the next group when the goal group is full.
- Falls back to earlier groups when later groups are full.
- Fails when no clusters remain available.

`test_free_blocks_simple()` marks all groups used, generates random non-overlapping-ish test ranges, frees ranges in the goal group through `ext4_free_blocks_simple_test()`, then validates that only the expected goal-group range is free and all other groups remain fully used.

`test_mark_diskspace_used()` builds an `ext4_allocation_context`, runs `ext4_mb_mark_diskspace_used_test()` for generated ranges, and checks that the bitmap contains exactly one used range at the expected start and length.

`test_mb_generate_buddy()` compares ext4's `ext4_mb_generate_buddy_test()` output against an independent local buddy generator. It validates both the raw buddy bitmap memory and `struct ext4_group_info` fields such as first free cluster, fragment count, free count, largest free order, and per-order counters.

`test_mb_mark_used()` loads a real ext4 buddy for the goal group, applies generated ranges through `mb_mark_used_test()` under the group lock, mirrors the same changes into an expected bitmap, regenerates the expected buddy, and compares the resulting buddy memory and group info.

`test_mb_free_blocks()` first marks an entire buddy group used, then frees generated ranges through `mb_free_blocks_test()` under the group lock, mirrors the clear operations into an expected bitmap, regenerates the expected buddy, and compares state.

`test_mb_mark_used_cost()` is marked slow. It loads a buddy, repeatedly generates ranges for `COUNT_FOR_ESTIMATE` iterations, measures jiffies spent marking ranges used, frees them again each iteration, and emits the accumulated cost with `kunit_info()`.

## Independent Buddy Generator
`mbt_generate_buddy()` derives expected buddy-cache state from a bitmap:
- Starts with all buddy bits set.
- Finds free bits in the original bitmap and records order-0 counters and free count.
- Coalesces adjacent free pairs into higher-order buddy levels by clearing bits in higher-level buddy maps and adjusting per-order counters.
- Tracks largest free order.
- Counts free fragments by scanning transitions from free to used and back.

`mbt_validate_group_info()` compares generated and ext4-produced group-info metadata. `do_test_generate_buddy()` runs both the local generator and ext4 generator and asserts exact memory equality for the buddy buffer.

## Parameterization
The suite defines three layouts:
- 1 KiB block size, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.
- 4 KiB block size, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.
- 64 KiB block size, cluster bits 3, 8192 blocks per group, 4 groups, 64-byte descriptors.

`mbt_show_layout()` formats these parameters for KUnit output. Tests that rely on buddy pages skip when filesystem block size exceeds `PAGE_SIZE`, because the buddy cache assumes each page contains at least one block.

## Dependencies
Depends on KUnit, KUnit static stubs, Linux random helpers, ext4 core definitions, and `mballoc.h` test-visible helper symbols such as `ext4_mb_new_blocks_simple_test()`, `ext4_free_blocks_simple_test()`, `ext4_mb_mark_diskspace_used_test()`, `ext4_mb_generate_buddy_test()`, `ext4_mb_load_buddy_test()`, `ext4_mb_unload_buddy_test()`, `mb_mark_used_test()`, and `mb_free_blocks_test()`.

## Risks and Test Limitations
The suite exercises allocator internals without real disk I/O, journal transactions, real block devices, or full mount setup. Random range generation broadens coverage but can make exact scenario reproduction depend on KUnit/random state. The independent buddy generator is useful as an oracle, but it must remain semantically aligned with ext4's buddy invariants. The 64 KiB layout is included, but buddy-cache mutation tests skip when block size exceeds page size.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mballoc-test.c -->