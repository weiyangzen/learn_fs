# Group Research: group_957_linux_stable_sources_os_linux_linux_stable_fs_btrfs_sysfs_c_sources__3f1a086e64a4

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`, Btrfs sysfs and self-test files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/sysfs.c

## Role
Implements Btrfs' sysfs surface under `/sys/fs/btrfs`: global feature reporting, per-filesystem feature state, mounted filesystem attributes, allocation and RAID profile stats, discard tunables, per-device information, qgroup state, kobject lifecycle, and sysfs updates after runtime state changes.

## Main Interfaces and Data
- Defines local sysfs wrapper types: `struct btrfs_feature_attr` for feature-bit attributes and `struct raid_kobject` for allocation profile directories.
- Uses attribute macros (`BTRFS_ATTR`, `BTRFS_ATTR_RW`, `BTRFS_FEAT_ATTR_*`) to declare many `struct kobj_attribute` instances and feature attributes.
- Exports the public helpers declared in `sysfs.h`: `btrfs_init_sysfs`, `btrfs_exit_sysfs`, `btrfs_sysfs_add_fsid`, `btrfs_sysfs_remove_fsid`, `btrfs_sysfs_add_mounted`, `btrfs_sysfs_remove_mounted`, device helpers, qgroup helpers, feature helpers, and read-policy parsing.
- Maintains the module-level `btrfs_kset` for `/sys/fs/btrfs` and uses `btrfs_ktype` to tie an fsid kobject back to `struct btrfs_fs_devices`.

## Behavior
- Feature handling reads and mutates superblock compat, compat-ro, and incompat flags through `get_features` and `set_features`. Mounted-filesystem writes are allowed only for feature bits present in the safe set/clear masks, reject read-only mounts, update the in-memory superblock under `super_lock`, set `BTRFS_FS_NEED_TRANS_COMMIT`, and wake the transaction thread.
- Global `/sys/fs/btrfs/features` combines supported feature-bit attributes with static capabilities such as ACL support, supported checksums, send stream version, rescue options, supported sectorsizes, and `temp_fsid` support. Per-filesystem `features` visibility hides unsupported unset bits but exposes enabled or mutable bits.
- Unknown feature bits are represented through generated names like `<feature_set>:<bit>` and merged into per-filesystem feature groups by `addrm_unknown_feature_attrs`.
- Mounted filesystem attributes include `label`, `nodesize`, `sectorsize`, `clone_alignment`, `quota_override`, `metadata_uuid`, `checksum`, `exclusive_operation`, `generation`, `read_policy`, `bg_reclaim_threshold`, `commit_stats`, and `temp_fsid`.
- Read policy supports the stable `pid` mode and, under `CONFIG_BTRFS_EXPERIMENTAL`, `round-robin[:value]` and `devid[:value]`, with value parsing, sectorsize alignment for round-robin minimum contiguous reads, device-id validation for devid mode, and logging when policy changes.
- Discard sysfs exposes async discard counters and tunables: discardable bytes/extents, bitmap/extent bytes, bytes saved, IOPS limit, KB/s limit, and max discard size. Stores update `discard_ctl` with `WRITE_ONCE` and reschedule discard work where needed.
- Allocation sysfs exposes global block reserve size/reserved bytes, space-info counters, chunk size, size-class counts, reclaim counters, dynamic/periodic reclaim flags, and per-RAID profile total/used byte aggregation from block group lists.
- Chunk-size writes require `CAP_SYS_ADMIN`, reject zoned and system-space changes, parse memparse values, clamp to max data chunk size and 10 percent of total writable bytes, enforce 256 MiB alignment/minimum, and update the space-info chunk size.
- Device sysfs creates `/devices` links to block-device kobjects and `/devinfo/<devid>` directories with `error_stats`, `fsid`, `in_fs_metadata`, `missing`, `replace_target`, `scrub_speed_max`, and `writeable`.
- Qgroup sysfs creates `/qgroups` global status (`enabled`, `inconsistent`, `drop_subtree_threshold`, `mode`) and one directory per qgroup with referenced/exclusive/limit/reservation counters.

## Lifecycle and Error Handling
- `btrfs_init_sysfs` creates the global `btrfs` kset, initializes known and unknown feature attributes, creates feature groups, merges static feature attributes, and conditionally creates debug groups. `btrfs_exit_sysfs` reverses those operations.
- `btrfs_sysfs_add_fsid` creates the fsid kobject plus `devices` and `devinfo` subdirectories; failure tears down previously created objects.
- `btrfs_sysfs_add_mounted` adds device sysfs entries, per-fs attributes, features, optional debug directory, discard directory, unknown feature attrs, `bdi` link, and allocation directory. A single failure path calls `btrfs_sysfs_remove_mounted`.
- Kobject release callbacks zero embedded kobject fields and complete unregister completions for fsid and devid objects; dynamically allocated raid, space-info, and qgroups kobjects are freed by release callbacks.
- Several allocation paths enter a NOFS context before kobject creation to avoid reclaim recursion while Btrfs transaction or allocation locks may be held.

## Dependencies
This file is tightly coupled to Btrfs superblock feature definitions, fs/device structs, block group and space-info accounting, discard scheduling, qgroup state, transaction commit signaling, and Linux kobject/sysfs APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/sysfs.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/sysfs.h

## Role
Public header for Btrfs sysfs integration. It defines the feature-set enum and exposes sysfs setup, teardown, mounted filesystem, device, space-info, qgroup, feature, uevent, and read-policy helpers to the rest of Btrfs.

## Main Interfaces
- Defines `enum btrfs_feature_set` with `FEAT_COMPAT`, `FEAT_COMPAT_RO`, `FEAT_INCOMPAT`, and `FEAT_MAX`, matching the three superblock feature flag classes.
- Declares feature formatting helpers: `btrfs_printable_features` and `btrfs_feature_set_name`.
- Declares kobject/sysfs lifecycle functions: global init/exit, fsid add/remove, mounted add/remove, sprout fsid rename, feature update, devid rename, and block device uevent helper.
- Declares allocation sysfs helpers for block group profile directories and space-info directories.
- Declares qgroup sysfs add/remove helpers for the qgroups container and individual qgroups.
- Declares `btrfs_read_policy_to_enum` unconditionally and experimental module read-policy helpers only under `CONFIG_BTRFS_EXPERIMENTAL`.

## Dependencies
Uses forward declarations for Btrfs structures and includes Linux type, compiler, and kobject declarations. The header is intentionally declaration-only and contains no inline sysfs behavior except conditional prototypes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.c

## Role
Provides the common in-kernel Btrfs self-test harness. It creates a pseudo filesystem mount for test inodes, allocates and frees dummy Btrfs objects, initializes dummy transactions, and orchestrates the complete sanity-test suite.

## Main Interfaces and Data
- Defines `test_mnt`, the pseudo filesystem type `btrfs_test_fs`, and `btrfs_test_super_ops`.
- Defines `test_error[]`, a shared allocation-error message table used by `test_std_err`.
- Exports helpers: `btrfs_new_test_inode`, `btrfs_alloc_dummy_fs_info`, `btrfs_free_dummy_fs_info`, `btrfs_alloc_dummy_device`, `btrfs_free_dummy_root`, `btrfs_alloc_dummy_block_group`, `btrfs_free_dummy_block_group`, `btrfs_init_dummy_transaction`, and `btrfs_init_dummy_trans`.
- Exports `btrfs_run_sanity_tests`, the top-level test runner.

## Behavior
- `btrfs_init_test_fs` registers and mounts a pseudo filesystem using Btrfs inode allocation/destruction so tests can allocate real VFS inodes without a mounted Btrfs filesystem.
- Dummy fs_info allocation creates `struct btrfs_fs_info`, `struct btrfs_fs_devices`, and a superblock copy, calls `btrfs_init_fs_info`, sets nodesize/sectorsize/checksum parameters, marks the fs as dummy/testing, and attaches it to the pseudo superblock.
- Dummy cleanup releases extent buffers held in `buffer_tree`, frees mapping tree state, dummy devices, qgroup config, roots, superblock copy, and fs_devices, while also running root and extent-buffer leak debug checks.
- Dummy devices are linked into `fs_info->fs_devices->devices` and initialize their allocation extent I/O tree.
- Dummy block groups allocate a free-space control structure, initialize lists and the free-space cache, and set basic geometry.
- The sanity runner tests each supported nodesize for `PAGE_SIZE` sectorsize, running free-space cache, extent-buffer, extent I/O, inode, qgroup, free-space-tree, raid-stripe-tree, delayed-ref, and chunk-allocation tests, then runs extent-map and zoned tests.

## Dependencies
This harness depends on VFS pseudo filesystems, Btrfs inode lifecycle, fs_info initialization, free-space cache, free-space tree, transactions, volumes, disk I/O, qgroups, block groups, and root tracking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.h

## Role
Shared header for Btrfs in-kernel self-tests. It declares the test runner, logging macros, allocation-error indexes, individual test entry points, and dummy object helpers when sanity tests are enabled.

## Main Interfaces
- Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, declares `btrfs_run_sanity_tests` and all test entry points for extent buffers, free-space cache, extent I/O, inodes, qgroups, free-space tree, raid stripe tree, extent maps, delayed refs, chunk allocation, and zoned testing.
- Defines `test_msg` and `test_err` logging macros with consistent `BTRFS: selftest` prefixes and file/line context for errors.
- Defines allocation-error enum values consumed by `test_error[]`.
- Declares dummy allocation/free helpers for inodes, fs_info, roots, block groups, transactions, and devices.
- Uses `DEFINE_FREE` wrappers for dummy fs_info and block groups to support kernel cleanup-attribute style automatic cleanup.
- Provides a no-op `btrfs_test_zoned` when zoned block device support is disabled, and a no-op `btrfs_run_sanity_tests` when the whole self-test config is disabled.

## Dependencies
Includes Linux types and cleanup helpers, and forward-declares Btrfs structures to keep test source files loosely coupled to the common harness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/btrfs-tests.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/chunk-allocation-tests.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/chunk-allocation-tests.c

## Role
Unit tests the pending extent internals used by Btrfs chunk allocation. The tested behavior is limited and precise: finding the first pending allocation in a range and finding a usable hole after excluding pending allocations.

## Main Tests
- `find_hole_tests` describes input search ranges, required minimum hole sizes, up to two pending extents, and expected hole discovery results for `btrfs_find_hole_in_pending_extents`.
- `test_find_hole_in_pending` allocates dummy fs_info/device state, marks pending extents with `CHUNK_ALLOCATED` in the device allocation state tree, calls the function under `chunk_mutex`, validates found/start/length outputs, and clears pending state between cases.
- `first_pending_tests` describes ranges and a single pending extent for `btrfs_first_pending_extent`.
- `test_first_pending_extent` validates no-pending, pending-at-start, overlap-at-start, inside-range, outside-range, and overlap-at-end cases.
- `btrfs_test_chunk_allocation` runs first-pending tests followed by find-hole tests.

## Coverage Notes
The test vectors cover empty ranges, zero-length input, pending allocations at boundaries, overlaps with the searched range, three-hole selection, holes smaller than the requested minimum, and reporting of the largest insufficient hole when no acceptable hole exists.

## Dependencies
Depends on the common Btrfs self-test harness, dummy devices, volume allocation-state trees, disk I/O initialization, and extent I/O tree bit operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/chunk-allocation-tests.c -->