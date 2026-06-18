# Group Research: group_654_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_sysfs_c_sources_lo_f8eede3c14cc

Scope confirmed against `Docs/research_subset_a.md`. All 12 listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/sysfs.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/sysfs.c

This file implements Btrfs' sysfs interface under `/sys/fs/btrfs`, covering global feature discovery, per-filesystem attributes, device info, allocation/space-info trees, discard tunables, read policy, qgroup reporting, and module init/exit registration.

Key structures are `struct btrfs_feature_attr` for feature-bit attributes and `struct raid_kobject` for per-RAID-profile allocation directories. Attribute construction is centralized through `BTRFS_ATTR*` and `BTRFS_FEAT_ATTR*` macros, which bind sysfs names, permissions, show handlers, and store handlers.

Feature handling reads and updates compat, compat_ro, and incompat superblock flags via `get_features()` and `set_features()`. `btrfs_feature_attr_store()` permits mounted-filesystem feature changes only when the bit is listed in the safe set/clear masks, rejects read-only filesystems, updates the superblock copy under `super_lock`, and wakes the transaction thread instead of committing directly from sysfs.

The global `/sys/fs/btrfs/features` directory exposes supported feature bits plus static capability attributes such as ACL support, checksum algorithms, send stream version, rescue options, supported sector sizes, and temp-fsid support. Mounted filesystems also get a UUID-specific `features` group whose visibility depends on the filesystem’s enabled feature bits and safe modification status.

Discard sysfs attributes under `<uuid>/discard` expose async discard counters and tunables: discardable bytes/extents, bitmap/extent bytes, saved bytes, IOPS limit, KB/s limit, and max discard size. Store handlers validate numeric input, update `discard_ctl`, and reschedule discard work where appropriate.

Allocation sysfs is split into `<uuid>/allocation`, per-space-info directories such as `data`, `metadata`, `system`, `mixed`, and per-RAID-profile directories. Space-info attributes expose accounting fields, reclaim counters, size-class counts, chunk size, reclaim thresholds, and optional debug-only forced chunk allocation.

Per-filesystem attributes include label, node/sector size, clone alignment, quota override, metadata UUID, checksum name, exclusive operation state, generation, read policy, background reclaim threshold, commit stats, and temp fsid. Writable attributes perform capability checks where needed and use `READ_ONCE`/`WRITE_ONCE` or locks for shared state.

Device sysfs creates `<uuid>/devices` links to block devices and `<uuid>/devinfo/<devid>` kobjects. Per-device attributes expose error stats, fsid, in-metadata/missing/replace-target/writeable state, and scrub speed limit.

Qgroup sysfs creates `<uuid>/qgroups`, reports global qgroup enabled/inconsistent/mode/drop-subtree-threshold state, and creates one kobject per qgroup with referenced, exclusive, max, limit, and reservation counters. Testing filesystems skip qgroup sysfs creation.

Lifecycle code creates and tears down kobjects carefully: `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_add_mounted()`, `btrfs_sysfs_remove_mounted()`, and `btrfs_sysfs_remove_fsid()` handle partial failure cleanup, device removal, unknown feature attributes, bdi links, discard/allocation/debug directories, and completion-based kobject release waits.

Important integration points include `btrfs_sysfs_add_block_group_type()`, `btrfs_sysfs_add_space_info_type()`, `btrfs_sysfs_update_sprout_fsid()`, `btrfs_sysfs_update_devid()`, `btrfs_sysfs_feature_update()`, `btrfs_kobject_uevent()`, `btrfs_init_sysfs()`, and `btrfs_exit_sysfs()`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/sysfs.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/sysfs.h

This header declares Btrfs sysfs types and entry points used outside `sysfs.c`.

It defines `enum btrfs_feature_set` with `FEAT_COMPAT`, `FEAT_COMPAT_RO`, `FEAT_INCOMPAT`, and `FEAT_MAX`, matching the three feature flag sets stored in the superblock.

Public declarations cover printable feature names, feature set names, sysfs fsid/device add/remove/update, mounted filesystem add/remove, block group and space-info sysfs registration, qgroup sysfs registration/deletion, feature group updates, and block-device uevents.

It also declares read-policy parsing via `btrfs_read_policy_to_enum()`. Under `CONFIG_BTRFS_EXPERIMENTAL`, it exposes read-policy module initialization and access to the module parameter string.

The header intentionally uses forward declarations for Btrfs core structures to avoid pulling large implementation headers into users of the sysfs interface.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.c

This file is the Btrfs in-kernel selftest harness. It registers a pseudo filesystem, mounts it internally, allocates dummy filesystem state, and runs the configured suite of Btrfs sanity tests.

`btrfs_test_init_fs_context()`, `test_type`, `btrfs_init_test_fs()`, and `btrfs_destroy_test_fs()` create and destroy the pseudo mount used for test inodes. The test superblock uses `btrfs_alloc_inode` and `btrfs_test_destroy_inode`.

Dummy helpers include `btrfs_new_test_inode()`, `btrfs_alloc_dummy_fs_info()`, `btrfs_free_dummy_fs_info()`, `btrfs_alloc_dummy_device()`, `btrfs_alloc_dummy_block_group()`, `btrfs_free_dummy_block_group()`, `btrfs_init_dummy_trans()`, and `btrfs_init_dummy_transaction()`.

`btrfs_alloc_dummy_fs_info()` initializes minimal `fs_info`, `fs_devices`, superblock copy, nodesize/sectorsize fields, checksum sizing, dummy-state flags, and the pseudo superblock’s `s_fs_info`.

`btrfs_free_dummy_fs_info()` performs broad cleanup: buffer tree extent buffers, mapping tree, dummy devices, qgroup config, roots, leak checks, super copy, fs_devices, and `fs_info`.

`btrfs_run_sanity_tests()` is the suite entry point. It initializes the pseudo filesystem, iterates over PAGE_SIZE sector size and nodesizes up to `BTRFS_MAX_METADATA_BLOCKSIZE`, and runs free-space-cache, extent-buffer, extent-io, inode, qgroup, free-space-tree, raid-stripe-tree, delayed-ref, and chunk-allocation tests. It then runs extent-map and zoned tests.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.h

This header gates the Btrfs selftest API behind `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.

When selftests are enabled, it declares `btrfs_run_sanity_tests()`, logging helpers `test_msg()` and `test_err()`, standard allocation error indexes, the shared `test_error[]` table, all individual test entry points, and dummy allocation/cleanup helpers.

It declares test functions for extent buffers, free-space cache, extent I/O, inodes, qgroups, free-space tree, raid stripe tree, extent map, delayed refs, chunk allocation, and zoned mode.

It provides cleanup helpers through `DEFINE_FREE` for dummy fs info and dummy block groups, allowing local automatic cleanup in tests that use kernel cleanup annotations.

When selftests are disabled, `btrfs_run_sanity_tests()` is a no-op returning 0. When zoned support is disabled, `btrfs_test_zoned()` is also a no-op.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/btrfs-tests.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/chunk-allocation-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/chunk-allocation-tests.c

This file tests chunk allocator pending-extent helpers that operate on the device allocation-state bitmap.

`struct pending_extent_test_case` defines scenarios for `btrfs_find_hole_in_pending_extents()`: input hole range, minimum hole size, up to two pending extents, and expected hole result.

`find_hole_tests[]` covers no pending extents, pending extents at/overlapping range boundaries, multiple holes, exact-sized holes, too-small holes, fully allocated ranges, pending extents at the end, and zero-length input.

`test_find_hole_in_pending()` creates dummy fs/device state, marks pending extents with `CHUNK_ALLOCATED`, calls the helper under `chunk_mutex`, validates found/start/len outputs, and clears pending bits between cases.

`struct first_pending_test_case` and `first_pending_tests[]` cover `btrfs_first_pending_extent()`, including no match, match at search start, overlapping start, inside range, outside range, and overlapping search end.

`test_first_pending_extent()` validates returned pending start/end ranges and clears allocation-state bits between cases.

`btrfs_test_chunk_allocation()` runs first-pending tests and then hole-finding tests for each sectorsize/nodesize combination supplied by the main harness.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/chunk-allocation-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/delayed-refs-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/delayed-refs-tests.c

This file validates Btrfs delayed-reference construction, merging, selection order, and cleanup behavior using dummy transactions.

It defines expected-state structs `ref_head_check` and `ref_node_check`, plus validators for delayed ref heads and nodes. Checks cover bytenr, num_bytes, ref modifiers, total ref modifiers, must-insert state, action, ref type, parent/root/owner/offset identity, and delayed-ref owner/offset accessors.

`simple_test()` converts a `struct btrfs_ref` into either a tree or data delayed ref, selects the resulting delayed-ref head and node, and validates both. `simple_tests()` exercises single add/drop operations for tree block refs, extent data refs, shared block refs, and shared data refs.

`merge_tests()` tests delayed-ref merging for metadata and data refs. It verifies add+drop cancellation, double adds, double drops, positive/negative net transitions after many operations, and complete cancellation across many distinct roots/parents.

`select_delayed_refs_test()` ensures delayed ref selection prioritizes add operations before drop operations, even when insertion order and rbtree ordering could otherwise expose drops first. It also tests a case where one add is merged away while another add remains selectable.

Helper deletion functions remove delayed ref heads and nodes from their trees/lists while managing refcounts and locks in the same style as core delayed-ref code.

`btrfs_test_delayed_refs()` allocates dummy fs info and a dummy transaction, runs simple tests, metadata merge tests, data merge tests, and selection-order tests, then frees all dummy state.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/delayed-refs-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-buffer-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-buffer-tests.c

This file tests extent-buffer item splitting, specifically `btrfs_split_item()`.

`test_btrfs_split_item()` creates dummy fs/root/path state and a dummy leaf extent buffer, inserts one checksum item containing `"mary had a little lamb"`, and then splits it twice.

The first split creates two items: the original key at offset 0 with `"mary had a little"` and a new key at offset 3 with `" lamb"`.

The second split splits the first item again, validating memmove behavior in a leaf with existing following items. Expected final chunks are `"mary"`, `" had a little"`, and `" lamb"` with correct keys, sizes, and stored data.

The test intentionally passes NULL transaction handles because it uses a dummy single-level leaf and has enough space to avoid leaf splitting.

`btrfs_test_extent_buffer_operations()` is the file’s public entry point and delegates to `test_btrfs_split_item()`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-buffer-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-io-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-io-tests.c

This file tests extent I/O tree behavior, delalloc range discovery, extent-buffer bitmap helpers, clear-bit search, and extent-buffer memory copy/move operations.

`process_page_range()` walks contiguous folios in an inode mapping and can verify locked state, unlock pages, and release folios. It supports the delalloc tests by checking page-lock behavior across ranges.

`test_find_delalloc()` builds a dummy inode with dirty pages and an initialized `extent_io_tree`, then validates `find_lock_delalloc_range()` across delalloc ranges aligned with the search, overlapping the search start, outside the search, spanning large max extent ranges, and interrupted by a page that is no longer dirty.

The file includes debug helpers to stringify and dump extent state flags when tests fail.

`test_find_first_clear_extent_bit()` validates empty-tree behavior, holes before/between/after set ranges, searching from inside set ranges, partial flag searches, and beyond-last-range behavior for `btrfs_find_first_clear_extent_bit()`.

Extent-buffer bitmap tests use a parallel kernel bitmap as oracle. They validate full clear/set, same-byte operations, cross-byte operations, cross-page operations when nodesize exceeds PAGE_SIZE, and a deterministic pseudo-random bit pattern.

`test_eb_mem_ops()` compares extent-buffer contents to normal memory after write, memcpy, and memmove operations. It covers same-page non-overlap, same-page overlap, and cross-page non-overlap/overlap cases.

`btrfs_test_extent_io()` runs delalloc, clear-bit, bitmap, and memory-operation tests in sequence.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-io-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-map-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-map-tests.c

This file tests the inode extent-map tree, especially concurrent-style `btrfs_add_extent_mapping()` EEXIST handling, range dropping/splitting, pinned/compressed map regressions, and reverse mapping from physical to logical addresses.

`free_extent_map_tree()` removes and frees all extent maps from an inode, with debug refcount validation under `CONFIG_BTRFS_DEBUG`.

Test cases 1 through 4 simulate races where one path has already inserted a larger or split extent map and a second path attempts to add an overlapping map. They validate that the existing or adjusted map returned covers the requested range correctly for normal, inline, buffered-write, and direct-write split scenarios.

`test_case_5()` creates compressed maps over adjacent file ranges and then drops front, back, middle, and whole ranges using `btrfs_drop_extent_map_range()`. It validates the exact remaining extent map tree after each drop.

`test_case_6()` validates that `btrfs_add_extent_mapping()` does not incorrectly synthesize a gap map between two adjacent but intentionally unmerged compressed extents.

`test_case_7()` is a pinned-map regression test. It drops a range with `skip_pinned` true and checks that a pinned compressed map remains intact while a later non-pinned map is split with correct start, length, and block start.

`test_case_8()` validates compressed extent-map adjustment when inserting a larger compressed map partially overlapped by an existing map. Expected result is an adjusted `[128K, 144K)` map with length 16K and offset 20K.

Reverse mapping tests construct dummy chunk maps and devices, call `btrfs_rmap_block()`, and validate whether physical superblock addresses map to expected logical addresses and stripe length.

`btrfs_test_extent_map()` allocates a dummy 4K filesystem/inode/root, runs all extent-map cases, then runs rmap vectors before cleanup.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-map-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tests.c

This file tests the in-memory free-space cache for block groups, including extent entries, bitmap entries, mixed extent/bitmap removals, bitmap-to-extent stealing, and the bytes index.

`test_extents()` validates basic extent-entry add/remove behavior: full removal, tail removal, front removal, middle removal, and absence checks for removed ranges.

`test_bitmaps()` forces bitmap entries and validates full bitmap removal, middle removal, and removal across two bitmap entries near the bitmap boundary.

`test_bitmaps_and_extents()` exercises mixed free-space representation: removing from extents while bitmaps exist, removing from bitmaps while extent entries exist, overlapping extent/bitmap removals, extent entries offset into bitmap coverage, and historical `-EAGAIN` style overlap regressions.

`test_steal_space_from_bitmap_to_extent()` replaces the free-space ops with a test `use_bitmap` policy to force bitmap creation. It validates that contiguous free space can be stolen from a bitmap into an adjacent extent entry so a large allocation can be satisfied by one entry. It tests both extent-left/bitmap-right and bitmap-left/extent-right layouts and ensures unrelated small bitmap regions are not stolen.

`check_num_extents_and_bitmaps()` and `check_cache_empty()` verify internal counters, remaining free space, allocation failure, and empty-cache state.

`test_bytes_index()` validates ordering of the free-space bytes index for extents and bitmaps, including bitmap `bytes` versus `max_extent_size` behavior after allocation searches recalculate the index.

`btrfs_test_free_space_cache()` builds dummy fs/root/block-group state large enough to cross bitmap boundaries, registers an extent-tree dummy root, and runs all free-space cache tests.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tree-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tree-tests.c

This file tests the on-disk-style free-space tree operations using dummy Btrfs tree state.

`__check_free_space_extents()` validates the free-space tree against an expected list of free ranges. It supports both extent-item format and bitmap format, reading `BTRFS_FREE_SPACE_EXTENT_KEY` items or walking bitmap bits with `btrfs_free_space_test_bit()`.

`check_free_space_extents()` first checks the current representation, then converts to the opposite representation with `btrfs_convert_free_space_to_extents()` or `btrfs_convert_free_space_to_bitmaps()` and checks again.

Individual test functions cover an empty block group, removing all free space, removing from the beginning, removing from the end, removing from the middle, merging left, merging right, merging both sides, and intentionally not merging separated ranges.

`run_test()` builds dummy fs/root/block-group state, enables the free-space-tree compat_ro feature, creates a single-level root node, adds initial block-group free space, optionally converts it to bitmaps, runs one test, removes block-group free space, and verifies no tree items remain.

`run_test_both_formats()` runs each operation starting from extent format and bitmap format.

`btrfs_test_free_space_tree()` runs all operations at sectorsize alignment and at a bitmap/page-derived alignment intended to flush out highmem/bitmap extent-buffer issues.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/free-space-tree-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/inode-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/inode-tests.c

This file tests inode extent lookup and outstanding extent accounting.

`insert_extent()` inserts synthetic file extent items into a dummy leaf. It can create inline, regular, preallocated, hole, compressed, and split file extents by setting all relevant `btrfs_file_extent_item` fields.

`setup_file_extents()` creates a deliberately complex file layout: inline data, implied hole, regular extents, explicit hole, split regular extents, prealloc extents, partially written prealloc extents, compressed extents, split compressed extents, regular extents, a larger implied hole with no file extent item, and a final regular extent.

`test_btrfs_get_extent()` first validates an empty inode returns a hole. It then uses the synthetic layout and repeatedly calls `btrfs_get_extent()` to verify returned `extent_map` start, length, disk bytenr, block start, offset, flags, compression type, prealloc state, compressed state, inline rounding, explicit holes, and implied holes.

`test_hole_first()` validates a file whose first file extent starts after offset 0. It expects `btrfs_get_extent()` to return a leading hole followed by the real extent.

`test_extent_accounting()` validates `BTRFS_I(inode)->outstanding_extents` accounting as delalloc ranges are added, split by clearing sectorsize holes, merged by refilling holes, expanded across `BTRFS_MAX_EXTENT_SIZE`, and finally fully cleared.

Global expected flag masks are initialized in `btrfs_test_inodes()`: compressed extents expect `EXTENT_FLAG_COMPRESS_ZLIB`, and prealloc extents expect `EXTENT_FLAG_PREALLOC`.

`btrfs_test_inodes()` runs extent lookup, hole-first lookup, and outstanding extent accounting for each sectorsize/nodesize combination supplied by the main harness.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/inode-tests.c -->