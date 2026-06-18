# Group Research: group_258_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_sysfs_c_sources_lo_2f3b96e9b549

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/btrfs-linux`.

Read completely:
- `sources/local-fs/btrfs-linux/fs/btrfs/sysfs.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/sysfs.h`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.h`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/chunk-allocation-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/delayed-refs-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-buffer-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-io-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-map-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tree-tests.c`
- `sources/local-fs/btrfs-linux/fs/btrfs/tests/inode-tests.c`

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.c

This file implements Btrfs' `/sys/fs/btrfs` interface. It creates global feature advertisement, per-filesystem UUID directories, mounted filesystem attributes, device and devid directories, allocation and raid-profile statistics, discard statistics and tunables, qgroup directories, and runtime feature visibility updates.

The file defines local wrappers around `struct kobj_attribute` and `struct kobject` ownership: `struct btrfs_feature_attr` couples a sysfs file to a feature-set bit, and `struct raid_kobject` stores a raid profile flag plus a kobject. The `BTRFS_ATTR*` and `BTRFS_FEAT_ATTR*` macros build the concrete read-only, write-only, read-write, and feature-bit attributes.

Feature handling is centered on `get_features()`, `set_features()`, `can_modify_feature()`, `btrfs_feature_attr_show()`, `btrfs_feature_attr_store()`, and `btrfs_feature_visible()`. Mounted filesystems expose only enabled or safely mutable features, while the global `/sys/fs/btrfs/features` directory advertises supported feature bits. Writable feature changes are limited by the safe set/clear masks, reject read-only superblocks, update the in-memory superblock under `super_lock`, and wake the transaction thread by setting `BTRFS_FS_NEED_TRANS_COMMIT`.

The static feature group reports kernel-version capabilities independent of a mounted filesystem: ACL support, `rmdir_subvol`, supported checksums, send-stream version, rescue options, supported sector sizes, and `temp_fsid`. Unknown on-disk feature bits are represented by generated names like `compat_ro:NN` via `init_feature_attrs()` and `addrm_unknown_feature_attrs()` so mounted filesystems remain inspectable even with unsupported bits present.

Discard sysfs support uses a `discard` subdirectory and exposes `discardable_bytes`, `discardable_extents`, bitmap/extent accounting, saved bytes, and tunables for IOPS, KB/s, and maximum discard size. Store paths parse numeric input, update `fs_info->discard_ctl` with `WRITE_ONCE()` where needed, recalculate delay for IOPS, and reschedule async discard work.

Allocation sysfs support has an `allocation` directory with global reserve counters, per-space-info directories, and per-raid-profile directories. Space-info files expose bytes counters, flags, chunk size, size-class counts, reclaim stats, dynamic/periodic reclaim knobs, and optional debug-only forced chunk allocation. Chunk-size writes require `CAP_SYS_ADMIN`, reject zoned and system spaces, clamp to Btrfs limits and 10% of writable bytes, and align to 256 MiB.

The mounted filesystem root attributes include label, nodesize, sectorsize, clone alignment, quota override, metadata UUID, checksum type, exclusive operation, generation, read policy, block-group reclaim threshold, commit stats, and temporary-fsid state. Label and feature writes intentionally defer persistence through normal transaction commit rather than committing directly from sysfs context.

Read-policy support always includes `pid` and conditionally includes experimental `round-robin[:value]` and `devid[:value]`. `btrfs_read_policy_to_enum()` parses optional values; `btrfs_read_policy_store()` validates alignment and device IDs, toggles round-robin stats collection, and updates `fs_devices` policy fields with `WRITE_ONCE()`.

Device sysfs support creates `devices` links to block-device kobjects and `devinfo/<devid>` directories with state and statistics files: metadata membership, missing, replace-target, scrub speed limit, writeable, fsid, and error stats. Add/remove paths use NOFS context to avoid reclaim deadlocks and wait on completion when kobjects are torn down.

Filesystem and mount lifecycle functions are the public surface used elsewhere: `btrfs_init_sysfs()`, `btrfs_exit_sysfs()`, `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, and `btrfs_sysfs_remove_mounted()`. They carefully build and dismantle the UUID directory, devices/devinfo subtrees, feature groups, debug groups, discard directory, BDI link, allocation directory, and per-device entries.

Qgroup sysfs support adds global `qgroups` attributes for enabled state, mode, inconsistency, and drop-subtree threshold, plus per-qgroup directories named `<level>_<subvolid>` with referenced/exclusive counts, limits, and reservation counters. Testing filesystems bypass qgroup sysfs creation/deletion through `btrfs_is_testing()`.

Key dependencies include `ctree.h`, `discard.h`, `disk-io.h`, `transaction.h`, `volumes.h`, `space-info.h`, `block-group.h`, `qgroup.h`, `fs.h`, and `accessors.h`. The file is mostly glue between core Btrfs state and Linux kobject/sysfs APIs, with important locking on superblock, qgroup, block reserve, space-info, and block-group list state.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.h

This header declares the public sysfs interface implemented by `sysfs.c`. It forward-declares the Btrfs core types needed by callers and defines `enum btrfs_feature_set` with `FEAT_COMPAT`, `FEAT_COMPAT_RO`, `FEAT_INCOMPAT`, and `FEAT_MAX`.

The exported feature helpers are `btrfs_printable_features()` and `btrfs_feature_set_name()`. They let other code format feature-bit sets consistently with the sysfs naming table, including generated names for unknown bits.

The exported lifecycle API covers global sysfs setup/teardown, filesystem UUID kobject creation/removal, mounted filesystem sysfs setup/removal, sprout-fsid renaming, feature-group refresh, block-device uevents, and devid renaming. It also exposes allocation-space operations for adding/removing space-info and raid-profile kobjects.

The qgroup API exports add/delete functions for the global qgroups kobject and individual qgroup kobjects. These are no-ops for testing filesystems in the implementation.

`btrfs_read_policy_to_enum()` is always declared. Under `CONFIG_BTRFS_EXPERIMENTAL`, the header also declares module-parameter initialization and access for the global read-policy string.

The header is intentionally narrow: it does not expose sysfs attribute structures or kobject internals, only Btrfs-level operations used by mount, device, allocation, qgroup, and module init/exit paths.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.c

This file is the shared selftest harness for Btrfs in-kernel sanity tests. It provides the pseudo filesystem mount used for test inodes, shared dummy object allocation helpers, and the top-level `btrfs_run_sanity_tests()` dispatcher.

The pseudo filesystem is registered as `btrfs_test_fs` with `BTRFS_TEST_MAGIC`. Its super operations use `btrfs_alloc_inode` and `btrfs_test_destroy_inode`, allowing tests to allocate normal Btrfs inodes without mounting a real filesystem. `btrfs_init_test_fs()` registers and kernel-mounts it; `btrfs_destroy_test_fs()` unmounts and unregisters it.

`btrfs_new_test_inode()` creates a regular inode from the test mount, assigns `BTRFS_FIRST_FREE_OBJECTID`, and initializes ownership. This is the common inode source for extent, extent-map, and inode tests.

`btrfs_alloc_dummy_fs_info()` creates a minimal `btrfs_fs_info`, `btrfs_fs_devices`, and superblock copy, initializes Btrfs fs-info internals, sets nodesize/sectorsize/checksum parameters, marks the fs as dummy/testing, and attaches it to the test superblock. `btrfs_free_dummy_fs_info()` performs broad cleanup: buffer tree extent buffers, mapping tree, dummy devices, qgroup config, fs roots, super copy, leak checks, fs devices, and the fs_info itself.

Device and block-group helpers create enough state for allocation tests. `btrfs_alloc_dummy_device()` initializes an allocation extent-io tree and links the device into `fs_devices->devices`; `btrfs_alloc_dummy_block_group()` allocates a block group plus free-space control and initializes list heads, free-space state, and locking.

Transaction helpers initialize dummy transaction handles and transaction objects for code paths that need delayed refs or free-space-tree transactions without a real running transaction.

`btrfs_run_sanity_tests()` runs the selected selftests for each nodesize from `PAGE_SIZE` up to `BTRFS_MAX_METADATA_BLOCKSIZE`, currently with sectorsize `PAGE_SIZE`. It runs free-space cache, extent-buffer operations, extent I/O, inode, qgroup, free-space tree, raid-stripe tree, delayed refs, and chunk allocation tests, then runs extent-map tests and zoned tests once. It stops at the first failure and always destroys the test filesystem.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.h

This header is the shared contract for Btrfs selftests. Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, it declares `btrfs_run_sanity_tests()`, the `test_msg()` and `test_err()` logging macros, standard allocation-error indexes, and `extern const char *test_error[]`.

It declares all major test entry points: extent-buffer operations, free-space cache, extent I/O, inode behavior, qgroups, free-space tree, raid-stripe tree, extent map, delayed refs, and chunk allocation. It also declares helper constructors and destructors for test inodes, dummy fs_info, dummy roots, dummy block groups, dummy devices, and dummy transactions.

The header uses `DEFINE_FREE()` cleanup helpers for dummy fs_info and block groups, matching the kernel cleanup attribute pattern used elsewhere.

Zoned tests are conditionally declared under `CONFIG_BLK_DEV_ZONED`; otherwise `btrfs_test_zoned()` is an inline success. If sanity tests are disabled entirely, `btrfs_run_sanity_tests()` becomes an inline no-op returning success.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/btrfs-tests.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/chunk-allocation-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/chunk-allocation-tests.c

This file tests chunk allocator pending-extent helpers, specifically `btrfs_find_hole_in_pending_extents()` and `btrfs_first_pending_extent()`. These helpers operate on a device allocation-state extent-io tree and are central to avoiding overlap with chunk allocations already pending.

`find_hole_tests[]` defines table-driven scenarios for searching holes inside a candidate range while some ranges are marked `CHUNK_ALLOCATED`. It covers no pending extents, pending extents at or overlapping the start/end, two-hole and three-hole layouts, cases where the first/second/third hole is the first acceptable result, all holes too small while still returning the largest candidate, fully allocated ranges, and zero-length input.

`test_find_hole_in_pending()` builds a dummy fs_info and dummy device, marks each test case's pending extents in `device->alloc_state`, calls `btrfs_find_hole_in_pending_extents()` under `fs_info->chunk_mutex`, validates both the found boolean and adjusted start/length, then clears all pending bits before the next case.

`first_pending_tests[]` covers direct lookup of the first pending extent overlapping a search range. It includes no pending extent, pending at search start, overlap with search start, pending inside the search range, outside the range, and overlap with the end.

`test_first_pending_extent()` mirrors the table-driven setup, marks one pending extent if present, calls `btrfs_first_pending_extent()` under `chunk_mutex`, and validates returned start/end only when a pending extent is expected.

`btrfs_test_chunk_allocation()` runs the first-pending tests before the hole-search tests. The file uses dummy fs/device helpers from `btrfs-tests.c` and intentionally validates exact range transformations, not just success/failure.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/chunk-allocation-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/delayed-refs-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/delayed-refs-tests.c

This file tests delayed-reference insertion, merging, selection order, and cleanup. It uses fake constants for root objectid, bytenr, tree level, inode, file offset, and shared parent so that metadata and data ref cases can share validation logic.

`struct ref_head_check` and `struct ref_node_check` encode expected delayed-ref-head and delayed-ref-node fields. `validate_ref_head()` checks bytenr, num_bytes, ref_mod, total_ref_mod, and reserved-insert state. `validate_ref_node()` checks bytenr, num_bytes, ref_mod, action, parent, root, type, owner, and offset.

`simple_test()` creates a `struct btrfs_ref`, initializes it as metadata or data depending on the disk ref key type, adds it through the real delayed-ref add helpers, selects the ref head, selects one node, validates both, then destroys delayed refs. `simple_tests()` runs this for add/drop variants of tree-block, extent-data, shared-block, and shared-data refs.

`merge_tests()` validates ref merging for metadata and data refs. It covers add followed by drop producing a zero-ref-mod head with no nodes; double add producing one merged add node; double drop producing one merged drop node; positive-to-negative and negative-to-positive transitions after many adds/drops; and a 50-ref mixed root/parent workload that should cancel cleanly to a zero-mod head with no nodes.

`select_delayed_refs_test()` checks delayed-ref selection order. It verifies that add operations are selected before drops even when the drop was inserted first and even when one add is canceled by merging, leaving another add that still must be selected before the drop.

The file includes local delete helpers that erase selected nodes/heads from delayed-ref trees and drop references in the same style expected by the delayed-ref implementation. `btrfs_test_delayed_refs()` allocates a dummy fs_info and transaction, initializes dummy transaction state, runs simple tests, metadata merge tests, data merge tests, and selection-order tests, then frees all resources.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/delayed-refs-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-buffer-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-buffer-tests.c

This file currently tests extent-buffer item splitting through `btrfs_split_item()`. It constructs a dummy fs_info, dummy root, path, and dummy leaf extent buffer, inserts one checksum item containing `"mary had a little lamb"`, then splits it twice.

The first split uses key offset `3` and split length `17`, expecting slot 0 to keep the original key and contain `"mary had a little"`, while slot 1 receives key offset `3` and contains `" lamb"`.

The second split uses key offset `1` and split length `4`, testing memmove of existing items inside the same leaf. It expects three slots: `"mary"` at key offset 0, `" had a little"` at key offset 1, and `" lamb"` at key offset 3.

The test validates item keys, item sizes, and bytes read back from the extent buffer. It deliberately passes a `NULL` transaction handle because the test uses a single dummy leaf with enough room and does not need real tree updates.

`btrfs_test_extent_buffer_operations()` is the public entry point and currently delegates entirely to `test_btrfs_split_item()`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-buffer-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-io-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-io-tests.c

This file tests extent I/O tree behavior, delalloc range finding, extent-buffer bitmap operations, clear-bit search behavior, and extent-buffer memory copy/move operations.

`test_find_delalloc()` creates a dummy root and test inode, initializes the inode's `io_tree`, creates dirty pages covering two maximum-sized file extents, and probes `find_lock_delalloc_range()`. It tests delalloc fully covering the search, delalloc overlapping the search start, no delalloc after the range, delalloc spanning from `max_bytes` to the end, and the fallback behavior when a page in the delalloc range is no longer dirty. It checks returned ranges and verifies pages in selected ranges are locked.

The file includes `extent_flag_to_str()` and `dump_extent_io_tree()` diagnostics used when delalloc/clear-bit checks fail.

`test_eb_bitmaps()` compares Linux bitmap operations against `extent_buffer_bitmap_set()`, `extent_buffer_bitmap_clear()`, and `extent_buffer_test_bit()`. It tests full set/clear, same-byte and cross-byte operations, multi-byte operations, cross-page operations when nodesize exceeds `PAGE_SIZE`, and a deterministic pseudo-random bit pattern. It runs against dummy extent buffers at offset 0 and at a sectorsize-aligned but not nodesize-aligned offset.

`test_find_first_clear_extent_bit()` validates `btrfs_find_first_clear_extent_bit()` on an empty tree, before a set range, between set ranges, while starting inside a set range, when searching for only one unset bit among mixed flags, and beyond the last known range.

`test_eb_mem_ops()` creates random memory and an extent buffer with identical contents, then compares `memcpy_extent_buffer()` and `memmove_extent_buffer()` against regular `memcpy()`/`memmove()` for same-page non-overlap, same-page overlap, and cross-page non-overlap/overlap when nodesize is larger than a page.

`btrfs_test_extent_io()` runs delalloc, first-clear-bit, bitmap, and memory-operation tests in order, stopping at the first failure.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-io-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-map-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-map-tests.c

This file tests extent-map tree insertion, EEXIST conflict handling, extent-map dropping/splitting, pinned extent behavior, compressed overlap adjustment, and reverse physical-to-logical mapping.

`free_extent_map_tree()` removes all extent maps from an inode tree and, under debug builds, detects leaked references before force-resetting refs for cleanup.

Test cases 1 through 4 model races where concurrent reads/writes add overlapping or broader extent maps. They validate that `btrfs_add_extent_mapping()` returns the correct existing or adjusted extent map rather than failing incorrectly when the desired range is already covered. These include regular extents, inline extents, buffered write overlap, and DIO split overlap scenarios.

`test_case_5()` builds adjacent compressed extent maps and exercises `btrfs_drop_extent_map_range()` for front split, back split, double split, and whole-map dropping. `valid_ranges[][]` and `validate_range()` assert the exact tree layout after each drop.

`test_case_6()` checks that `btrfs_add_extent_mapping()` does not incorrectly synthesize a gap mapping when two unmerged compressed extent maps sit side by side.

`test_case_7()` is a regression test for `btrfs_drop_extent_map_range(..., skip_pinned=true)`. It ensures a pinned compressed extent is preserved, an unpinned following extent is split correctly, the block start is adjusted, and no unexpected mappings remain.

`test_case_8()` tests compressed extent-map adjustment when adding a large compressed extent that partially overlaps an existing compressed map. It expects the resulting returned map to be trimmed to `[128K, 144K)`, length 16K, with offset 20K.

The reverse-map section defines `struct rmap_test_vector` and `test_rmap_block()`, builds dummy chunk maps/devices, adds them to the mapping tree, and calls `btrfs_rmap_block()` for superblock physical addresses. It validates both a RAID1 chunk that should map to a logical address and an out-of-range single chunk that should not map.

`btrfs_test_extent_map()` uses a 4K dummy fs_info regardless of host page size because its immediate constants assume 4K block size. It allocates a test inode/root, runs all eight extent-map cases, then runs the rmap vectors.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-map-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tests.c

This file tests the in-memory free-space cache for block groups. It covers extent-only free space, bitmap-only free space, mixed bitmap/extent operations, stealing contiguous bitmap space into extent entries, and the bytes-index ordering used for allocation search.

`test_extents()` adds and removes extent entries, checking complete removal plus front, tail, and middle removal cases. It uses `test_check_exists()` to ensure removed regions are actually gone.

`test_bitmaps()` forces bitmap entries and tests full removal, middle removal, and removal spanning two bitmap entries. Bitmap span uses `BITS_PER_BITMAP * sectorsize` to calculate the next bitmap boundary.

`test_bitmaps_and_extents()` covers mixed representation edge cases: extents and bitmaps at the same offset, removal fully in one representation, overlapping removal across both, an extent starting before a bitmap while deletion falls inside both, and a previous regression where removing a range split across bitmap and extent returned `-EAGAIN`.

`test_steal_space_from_bitmap_to_extent()` uses a custom `use_bitmap` operation to force bitmap use after at least one extent exists. It builds scenarios where an extent and bitmap represent adjacent free ranges, then verifies bitmap free space is stolen into the extent entry so a single large allocation can succeed. It tests both directions: extent on the left of a bitmap and extent on the right of a bitmap. It also ensures unrelated small bitmap free ranges are not stolen incorrectly and that the cache becomes empty after expected allocations.

`test_bytes_index()` validates the `free_space_bytes` rb-tree ordering. It first checks extent entries are sorted by descending byte size, then bitmap entries by byte size, then forces all new free space into bitmaps and validates the transition between indexing by total bytes and `max_extent_size` after failed allocation searches.

`btrfs_test_free_space_cache()` allocates a dummy fs_info and block group sized to cross bitmap boundaries even on large-page systems, inserts a dummy extent-tree root, then runs extent, bitmap, mixed, stealing, and bytes-index tests.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tree-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tree-tests.c

This file tests the on-disk free-space tree representation using dummy roots, dummy transactions, and synthetic block groups. It verifies both extent-item and bitmap-item formats and converts between them during validation.

`__check_free_space_extents()` reads the free-space info item for a block group and validates expected free-space extents. If the tree uses bitmaps, it walks bitmap items sector by sector and reconstructs free ranges from set bits. If it uses extent items, it checks item count, key type, objectid, and length directly.

`check_free_space_extents()` first validates the current representation, then flips to the other representation with `btrfs_convert_free_space_to_extents()` or `btrfs_convert_free_space_to_bitmaps()` and validates again. This means each functional test checks both encodings.

The individual test functions cover an empty block group, removing all free space, removing from the beginning, removing from the end, removing the middle, merging with a left neighbor, merging with a right neighbor, merging both neighbors, and adding non-adjacent extents without merging.

`run_test()` creates a dummy fs_info/root, enables the free-space-tree compat-ro flag, initializes a leaf root node, creates a dummy block group with a length of eight alignment units, marks it as needing free-space setup, adds its free space to the tree, optionally converts to bitmap format, runs one test, removes the block group free-space items, and asserts the root leaf has no leftover items.

`run_test_both_formats()` executes each test starting from extent format and bitmap format. `btrfs_test_free_space_tree()` runs all scenarios twice per format: once aligned to sectorsize and once aligned to `BTRFS_FREE_SPACE_BITMAP_BITS * PAGE_SIZE` to exercise extent-buffer bitmap handling around page boundaries.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/free-space-tree-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/inode-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/inode-tests.c

This file tests inode extent lookup and outstanding-delalloc extent accounting. It builds synthetic subvolume-tree leaves directly and validates `btrfs_get_extent()` across inline, hole, regular, preallocated, compressed, split, and implied-hole ranges.

`insert_extent()` inserts a `BTRFS_EXTENT_DATA_KEY` file extent item into a dummy leaf and fills all relevant file-extent fields: type, disk bytenr, disk length, offset, num bytes, ram bytes, compression, encryption, and encoding. Inline extents include inline data length in the item size. `insert_inode_item_key()` inserts a blank inode item so searches beginning with a hole behave like real tree searches.

`setup_file_extents()` creates a deliberately complex layout scaled by sectorsize: an inline extent, implied hole, regular extents, split regular extents with explicit hole, prealloc extents, partially written prealloc extents, compressed extents, split compressed extents, a hole with no extent item, and a final regular extent.

`test_btrfs_get_extent()` first verifies an empty tree returns a hole. It then installs the synthetic layout and walks through it in order, checking each returned extent map's start, length, disk mapping, offset, flags, and compression type. It verifies inline extent rounding to sectorsize, regular mappings, explicit and implied holes, prealloc flags, compressed flags and compression IDs, offset adjustment for split extents, and returned hole length behavior.

`test_hole_first()` handles the specific case where the first file range is a hole before the first real extent. It inserts an inode item and a regular extent starting at sectorsize, then checks `btrfs_get_extent()` returns a leading hole followed by the real extent.

`test_extent_accounting()` validates `BTRFS_I(inode)->outstanding_extents` as delalloc ranges are added, split by clearing a sector-sized hole, merged again, extended beyond `BTRFS_MAX_EXTENT_SIZE`, split again, refilled, and finally cleared completely. It checks accounting stays aligned to Btrfs maximum extent segmentation rules.

`btrfs_test_inodes()` sets expected flag masks for compressed and prealloc extent maps, then runs `test_btrfs_get_extent()`, `test_hole_first()`, and `test_extent_accounting()`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/inode-tests.c -->