# Group Research: group_715_linux_sources_os_linux_linux_fs_btrfs_sysfs_c_sources_os_linux_linux_944feba77cf9

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/sysfs.c -->
# File Research: sources/os/linux/linux/fs/btrfs/sysfs.c

Read completely: 2702 lines.

This file implements the Btrfs sysfs surface under `/sys/fs/btrfs`, including module-wide feature discovery, per-filesystem attributes, allocation/space-info directories, device directories and links, qgroup directories, read-policy tuning, and sysfs init/exit.

Major sysfs layout implemented here:
- `/sys/fs/btrfs/features`: supported feature-bit attributes plus static capability attributes.
- `/sys/fs/btrfs/<uuid>`: mounted filesystem attributes such as label, nodesize, sectorsize, checksum, generation, read policy, commit stats, quota override, temp fsid, and exclusive operation.
- `/sys/fs/btrfs/<uuid>/features`: currently enabled or modifiable per-filesystem feature bits.
- `/sys/fs/btrfs/<uuid>/allocation`: global reservation stats and per-space-info children.
- `/sys/fs/btrfs/<uuid>/allocation/<bg-type>`: space-info accounting, reclaim tunables, chunk-size control, and per-RAID-profile children.
- `/sys/fs/btrfs/<uuid>/discard`: async discard stats and limits.
- `/sys/fs/btrfs/<uuid>/devices` and `/devinfo/<devid>`: block-device links plus per-device state and error counters.
- `/sys/fs/btrfs/<uuid>/qgroups` and qgroup children: qgroup mode/status and per-qgroup accounting.

Feature handling:
- `struct btrfs_feature_attr` wraps a kobject attribute with feature set and bit.
- `get_features()` and `set_features()` access compat, compat_ro, or incompat flags from the superblock copy.
- `can_modify_feature()` gates mounted-filesystem feature changes through `*_SAFE_SET` and `*_SAFE_CLEAR` masks.
- `btrfs_feature_attr_show()` reports either per-filesystem state or global modifiability.
- `btrfs_feature_attr_store()` validates mounted writable filesystems, applies safe feature set/clear operations under `super_lock`, sets `BTRFS_FS_NEED_TRANS_COMMIT`, and wakes the transaction thread instead of committing directly from sysfs.
- Unknown feature bits are exposed with generated names like `compat_ro:12` through `addrm_unknown_feature_attrs()`.

Static capability attributes report POSIX ACL support, supported checksums, send stream version, rescue options, supported sectorsizes, `rmdir_subvol`, and temp-fsid support.

Discard attributes expose counters from `fs_info->discard_ctl` and writable tunables for `iops_limit`, `kbps_limit`, and `max_discard_size`. Store paths parse numeric input, update values with `WRITE_ONCE()` where appropriate, and reschedule discard work when limits change.

Allocation and space-info handling:
- Global reservation size/reserved are shown under the allocation directory.
- Per-RAID-profile kobjects report total and used bytes by iterating block groups under `groups_sem`.
- `SPACE_INFO_ATTR()` generates locked readers for core space-info accounting fields.
- `chunk_size` is writable by `CAP_SYS_ADMIN`, forbidden for system space and zoned filesystems, capped by max data chunk size and 10% of writable device bytes, and aligned to 256 MiB.
- Reclaim tunables include global and per-space-info thresholds plus dynamic/periodic reclaim switches.
- Debug builds expose `force_chunk_alloc`, which starts a transaction and requests chunk allocation from sysfs context with explicit warnings in comments.

Per-filesystem attributes:
- `label` is writable on read-write filesystems and updates the superblock label under `super_lock`, then schedules a transaction commit.
- `commit_stats` reports commit counts and durations; writing `0` as `CAP_SYS_RESOURCE` resets max commit duration.
- `quota_override` is controlled by `CAP_SYS_RESOURCE`.
- `read_policy` supports `pid`, and under experimental builds `round-robin[:value]` and `devid[:value]`. Parsing is shared with module parameter initialization through `btrfs_read_policy_to_enum()`.
- `exclusive_operation` maps the current exclusive operation enum to a readable string.

Kobject lifecycle:
- `btrfs_init_sysfs()` creates the top-level `btrfs` kset under `fs_kobj`, initializes feature attributes, and creates/merges global feature groups.
- `btrfs_exit_sysfs()` removes groups and unregisters the kset.
- `btrfs_sysfs_add_fsid()` creates the per-fsid directory plus `devices` and `devinfo` children.
- `btrfs_sysfs_add_mounted()` adds per-device entries, filesystem files, feature groups, discard directory, `bdi` link, and allocation directory; failure unwinds through `btrfs_sysfs_remove_mounted()`.
- `btrfs_sysfs_remove_mounted()` removes mounted-only files/directories but leaves fsid-level teardown to `btrfs_sysfs_remove_fsid()`.
- Device kobjects use completions so removal can wait for release callbacks.
- Space-info and RAID kobjects own their release/free paths.

Device handling:
- `btrfs_sysfs_add_device()` creates a block-device symlink and `/devinfo/<devid>` kobject.
- Device attributes expose in-filesystem-metadata, missing, replace-target, writable, fsid, scrub speed limit, and error stats.
- `btrfs_sysfs_update_sprout_fsid()` and `btrfs_sysfs_update_devid()` rename kobjects after fsid/devid changes.
- `btrfs_kobject_uevent()` sends block-device uevents and logs failures.

Qgroup handling:
- Global qgroup attributes expose enabled, mode (`qgroup` or `squota`), inconsistent, and drop-subtree threshold.
- Per-qgroup attributes expose referenced/exclusive limits and reservation buckets.
- Testing filesystems skip qgroup sysfs operations.
- Add/delete paths use qgroup kobjects under `fs_info->qgroups_kobj` and clean up on failure.

Concurrency and correctness notes:
- Superblock feature/label access uses `super_lock`.
- Space-info accounting readers use `space_info->lock`; block-group iteration uses `groups_sem`.
- Qgroup readers use `qgroup_lock`.
- Sysfs kobject creation can allocate with `GFP_KERNEL`; block-group sysfs add wraps allocation in a NOFS context to avoid reclaim deadlocks while transaction-related locks may be held.
- Feature updates avoid direct transaction commits in sysfs context.
- Store paths carefully reject readonly filesystems, missing fs devices, invalid values, unsupported operations, and insufficient capabilities.

Main risks:
- Sysfs lifecycle ordering is delicate: mounted-only teardown, fsid teardown, seeded devices, and kobject release completions must stay paired.
- Feature mutability must remain synchronized with safe set/clear masks or sysfs could expose unsafe mounted feature changes.
- New space-info subgroups, RAID profiles, qgroup fields, device states, or feature bits need matching sysfs naming and removal paths.
- Read-policy parsing differs between experimental and non-experimental builds; callers must handle unavailable policy names.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/sysfs.h -->
# File Research: sources/os/linux/linux/fs/btrfs/sysfs.h

Read completely: 57 lines.

This header declares the public Btrfs sysfs interface used by the rest of the filesystem.

It defines `enum btrfs_feature_set` with the three superblock feature namespaces:
- `FEAT_COMPAT`
- `FEAT_COMPAT_RO`
- `FEAT_INCOMPAT`

Exports include:
- Feature formatting helpers: `btrfs_printable_features()` and `btrfs_feature_set_name()`.
- Top-level sysfs lifecycle: `btrfs_init_sysfs()` and `btrfs_exit_sysfs()`.
- Fsid and mounted-filesystem lifecycle: `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, and `btrfs_sysfs_remove_mounted()`.
- Device lifecycle and rename/update helpers: `btrfs_sysfs_add_device()`, `btrfs_sysfs_remove_device()`, `btrfs_sysfs_update_devid()`, and `btrfs_sysfs_update_sprout_fsid()`.
- Allocation sysfs helpers for block groups and space info.
- Qgroup sysfs add/delete helpers.
- Read policy parser `btrfs_read_policy_to_enum()`.
- Experimental read-policy module-parameter helpers when `CONFIG_BTRFS_EXPERIMENTAL` is enabled.

The header intentionally forward-declares Btrfs structures so sysfs users do not need to include the implementation-heavy headers directly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.c

Read completely: 313 lines.

This file implements the common in-kernel Btrfs selftest harness and dummy object allocation helpers.

Core harness:
- Registers a pseudo filesystem named `btrfs_test_fs` using `init_pseudo()` and `BTRFS_TEST_MAGIC`.
- Mounts it through `kern_mount()` so tests can allocate real VFS inodes.
- Provides `btrfs_new_test_inode()` to create regular-file test inodes backed by the pseudo superblock.
- `btrfs_run_sanity_tests()` initializes the pseudo filesystem, runs all configured Btrfs sanity tests over PAGE_SIZE sectorsize and every nodesize from sectorsize through `BTRFS_MAX_METADATA_BLOCKSIZE`, then runs extent-map and zoned tests.

Shared error strings:
- `test_error[]` maps common allocation failure categories to messages used by `test_std_err()`.

Dummy object helpers:
- `btrfs_alloc_dummy_fs_info()` allocates `fs_info`, `fs_devices`, and `super_copy`, initializes core Btrfs state, sets nodesize/sectorsize/csum fields, marks the fs as dummy/testing, and installs it in the pseudo superblock.
- `btrfs_free_dummy_fs_info()` frees extent buffers from `buffer_tree`, mapping tree state, dummy devices, qgroup config, roots, superblock copy, fs_devices, and leak-checks roots/extent buffers.
- `btrfs_alloc_dummy_device()` initializes a dummy device allocation-state extent tree and links it into `fs_devices->devices`.
- `btrfs_alloc_dummy_block_group()` creates a block group with free-space control, lists, mutex, full stripe length, and free-space cache initialization.
- `btrfs_init_dummy_transaction()` and `btrfs_init_dummy_trans()` create minimal transaction and transaction-handle structures for tests.

The runner calls, in order:
- free-space cache tests
- extent-buffer operation tests
- extent I/O tests
- inode tests
- qgroup tests
- free-space tree tests
- raid-stripe-tree tests
- delayed-ref tests
- chunk-allocation tests
- extent-map tests
- zoned tests, when enabled

Correctness notes:
- Dummy fs_info teardown refuses non-testing fs_info objects.
- Dummy roots that were inserted into the global root radix are expected to be freed through `btrfs_free_fs_roots`; non-radix roots are explicitly deleted/put.
- The pseudo mount is global to the selftest run, so tests share the same synthetic VFS substrate but allocate their own Btrfs state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.h -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.h

Read completely: 83 lines.

This header exposes the Btrfs selftest API when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.

It defines:
- `test_msg()` and `test_err()` logging macros with consistent `BTRFS: selftest:` prefixes.
- `test_std_err()` for common allocation failures.
- Allocation error enum values used as indices into `test_error[]`.
- Prototypes for all Btrfs selftest entry points.
- Prototypes for dummy fs_info, root, block-group, transaction, inode, and device helpers.
- `DEFINE_FREE()` cleanup helpers for dummy fs_info and dummy block groups.
- A zoned-test stub returning `0` when `CONFIG_BLK_DEV_ZONED` is disabled.
- A stub `btrfs_run_sanity_tests()` returning `0` when sanity tests are not compiled.

The header is the shared contract between the selftest runner and each individual test file.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/btrfs-tests.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/chunk-allocation-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/chunk-allocation-tests.c

Read completely: 476 lines.

This file unit-tests chunk allocator pending-extent search helpers:
- `btrfs_find_hole_in_pending_extents()`
- `btrfs_first_pending_extent()`

The tests create dummy fs_info and a dummy device, mark pending chunk-allocation ranges in the device `alloc_state` extent tree with `CHUNK_ALLOCATED`, and validate search results under `fs_info->chunk_mutex`.

`find_hole_tests[]` covers:
- no pending extents
- pending extent at or overlapping the search start
- first, second, or third hole satisfying minimum size
- all holes too small, with expected largest-hole reporting
- full search range consumed by pending allocation
- pending extent at the end of the range
- zero-length input

`test_find_hole_in_pending()` validates both the boolean found result and adjusted `hole_start`/`hole_len`, then clears all pending bits after each case.

`first_pending_tests[]` covers:
- no pending extent
- pending extent at search start
- pending extent overlapping search start
- pending extent inside the search range
- pending extent outside the search range
- pending extent overlapping the end of the search range

`test_first_pending_extent()` validates found status plus returned pending start/end.

`btrfs_test_chunk_allocation()` runs first-pending tests before hole-finding tests.

Correctness focus:
- Pending extent searches must correctly clip and report ranges around already-reserved chunk-allocation spans.
- The helpers are tested with large GiB-scale ranges to exercise boundary arithmetic.
- Extent-state cleanup after each case prevents one table row from contaminating the next.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/chunk-allocation-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/delayed-refs-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/delayed-refs-tests.c

Read completely: 1016 lines.

This file tests delayed-reference creation, selection, ordering, and merge behavior for metadata and data refs.

Validation helpers:
- `ref_head_check` and `ref_node_check` describe expected delayed-ref head/node fields.
- `validate_ref_head()` checks bytenr, num_bytes, `ref_mod`, `total_ref_mod`, and `must_insert_reserved`.
- `validate_ref_node()` checks bytenr, num_bytes, ref_mod, action, parent, root, disk ref type, owner, and offset.
- `delete_delayed_ref_head()` and `delete_delayed_ref_node()` manually remove selected test refs and drop references.

`simple_test()` converts a prepared `btrfs_ref` into a delayed tree/data ref, selects the head and first delayed-ref node, and validates both.

`simple_tests()` covers single add and single drop cases for:
- tree block refs
- extent data refs
- shared block refs
- shared data refs

`merge_tests()` runs for both `BTRFS_REF_METADATA` and `BTRFS_REF_DATA`. It validates:
- add followed by drop collapses to a head with zero total mod and no nodes.
- two adds merge into one add node with `ref_mod == 2`.
- two drops merge into one drop node with `ref_mod == -2`.
- many adds then more drops produce the expected negative merged node.
- many drops then more adds produce the expected positive merged node.
- many refs across alternating roots/parents followed by matching drops collapse to no nodes.

`select_delayed_refs_test()` validates delayed-ref selection priority:
- Add operations are selected before drop operations even if insertion order or rb-tree order would otherwise differ.
- If an add is merged away, a remaining add is still selected before drops.

`btrfs_test_delayed_refs()` creates dummy fs_info, dummy transaction, and dummy transaction handle, then runs simple tests, metadata merge tests, data merge tests, and selection-order tests.

Correctness focus:
- Delayed refs must preserve correct aggregate reference deltas while merging equivalent operations.
- Selection order matters because extent processing depends on adds being handled before drops.
- Data and metadata refs share many mechanics but differ in ref type, owner, and offset semantics, so both are exercised.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/delayed-refs-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/extent-buffer-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/extent-buffer-tests.c

Read completely: 223 lines.

This file tests `btrfs_split_item()` on a dummy leaf extent buffer.

`test_btrfs_split_item()`:
- Allocates dummy fs_info, root, path, and extent buffer.
- Inserts one item with key `(0, BTRFS_EXTENT_CSUM_KEY, 0)` and payload `"mary had a little lamb"`.
- Splits the item at offset 17 with new key offset 3, expecting:
  - slot 0: original key, payload `"mary had a little"`
  - slot 1: key offset 3, payload `" lamb"`
- Splits the first item again at offset 4 with new key offset 1, expecting:
  - slot 0: `"mary"`
  - slot 1: `" had a little"`
  - slot 2: `" lamb"`

The test verifies keys, item sizes, and copied payload contents after each split.

`btrfs_test_extent_buffer_operations()` is the file entry point and runs the split-item test.

Correctness focus:
- Splitting an item must preserve original key/payload prefixes, create the right new key and suffix, and memmove later items correctly.
- The test intentionally uses a single dummy level-0 leaf and NULL transaction handle because no tree split is needed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/extent-buffer-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/extent-io-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/extent-io-tests.c

Read completely: 830 lines.

This file tests selected extent I/O tree, folio locking, extent-buffer bitmap, clear-range, and extent-buffer memory operations.

`test_find_delalloc()`:
- Creates dummy fs_info/root/inode and an inode io-tree.
- Allocates and dirties pages covering two `BTRFS_MAX_EXTENT_SIZE` ranges.
- Exercises `find_lock_delalloc_range()` over scenarios where the search matches the whole delalloc range, starts inside it, starts after it, spans a later range, and encounters a dirty-page gap.
- Uses `process_page_range()` to verify pages in returned ranges are locked, then unlocks/releases them.
- Dumps the extent I/O tree on failure.

Extent-state diagnostics:
- `extent_flag_to_str()` and `dump_extent_io_tree()` format extent-state flags for test failures.

Extent-buffer bitmap tests:
- `check_eb_bitmap()` compares an ordinary Linux bitmap with bits read through `extent_buffer_test_bit()`.
- `test_bitmap_set()` and `test_bitmap_clear()` mirror operations into both representations.
- `__test_eb_bitmaps()` covers full clear/set, same-byte partial operations, cross-byte operations, cross-page operations when nodesize exceeds PAGE_SIZE, and a pseudo-random bit pattern.
- `test_eb_bitmaps()` runs the bitmap suite on dummy extent buffers starting at both 0 and a sectorsize-aligned nonzero bytenr.

`test_find_first_clear_extent_bit()`:
- Tests `btrfs_find_first_clear_extent_bit()` on an empty tree, beginning holes, holes between allocated/trimmed ranges, ranges missing only one requested flag, and searches beyond the last known range.

Extent-buffer memory operations:
- `test_eb_mem_ops()` initializes an extent buffer and memory buffer with random bytes, then mirrors `memcpy_extent_buffer()` and `memmove_extent_buffer()` against normal `memcpy()`/`memmove()`.
- It covers same-page non-overlapping copies, same-page overlapping moves, and cross-page cases for larger nodesizes.

`btrfs_test_extent_io()` runs delalloc discovery, clear-bit search, bitmap tests, and memory-operation tests.

Correctness focus:
- Delalloc range discovery must return correct byte ranges and lock all corresponding pages.
- Extent-buffer bitmap helpers must be byte/bit correct across unaligned and page-spanning ranges.
- Extent-buffer copy/move helpers must match normal memory semantics even when the buffer spans folios.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/extent-io-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/extent-map-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/extent-map-tests.c

Read completely: 1202 lines.

This file tests extent-map tree insertion, overlap handling, dropping/splitting, compressed extent adjustment, pinned extent behavior, and reverse physical-to-logical mapping.

Shared cleanup:
- `free_extent_map_tree()` removes all mappings from an inode extent-map tree and, in debug builds, reports leaked references.

Extent-map insertion/overlap cases:
- `test_case_1()` simulates concurrent reads where a larger `[0,16K)` map already exists and adding `[0,8K)` should return the existing covering map.
- `test_case_2()` tests repeated inline extent insertion after page-cache discard, expecting the existing inline map.
- `test_case_3()` simulates a buffered write inserting `[4K,8K)` before direct reads add a larger `[0,16K)` map; subcases search before, after, and near the end of the existing map.
- `test_case_4()` simulates direct write splitting `[0,32K)` into `[0,8K)` and `[8K,32K)` while another direct read tries to add the original larger extent.

Drop/split cases:
- `add_compressed_extent()` inserts compressed maps to prevent merging.
- `test_case_5()` creates ranges `[0,12K)`, `[12K,24K)`, `[24K,36K)`, `[36K,40K)`, and `[40K,64K)`, then drops:
  - `[8K,12K)` for front split
  - `[12K,20K)` for back split
  - `[28K,32K)` for double split
  - `[32K,64K)` for whole-map dropping
- `validate_range()` checks the exact tree layout after each drop.

Additional regression cases:
- `test_case_6()` ensures `btrfs_add_extent_mapping()` does not synthesize a bridge extent between two adjacent but unmerged compressed maps.
- `test_case_7()` tests `btrfs_drop_extent_map_range(..., skip_pinned=true)` with a pinned compressed `[0,16K)` map and an unpinned `[32K,48K)` map, ensuring the pinned range survives and the later map is split correctly.
- `test_case_8()` checks compressed map adjustment when an added `[108K,144K)` map overlaps an existing `[120K,128K)` map and the search range is `[140K,144K)`. Expected result is adjusted `[128K,144K)` with offset `20K`.

Reverse mapping:
- `rmap_test_vector` describes chunk layout and expected logical results.
- `test_rmap_block()` builds dummy chunk maps/devices, adds them to the mapping tree, and calls `btrfs_rmap_block()`.
- Cases include a RAID1 chunk intersecting the superblock physical address and a single-profile chunk where the physical address is out of range.

`btrfs_test_extent_map()` creates a dummy 4K fs_info/inode/root, runs cases 1-8, then rmap tests.

Correctness focus:
- Concurrent insertion paths must handle `-EEXIST` by returning useful covering maps.
- Extent-map splitting must preserve logical length, disk bytenr, disk length, offsets, compression flags, and pinned status.
- Compressed extent overlap adjustment is especially sensitive because logical offsets and physical storage lengths differ.
- Reverse mapping must avoid false positives for unrelated physical ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/extent-map-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/free-space-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/free-space-tests.c

Read completely: 1063 lines.

This file tests the in-memory free-space cache used by block groups.

`test_extents()` covers extent-entry-only behavior:
- Add and remove an entire extent.
- Remove from tail, front, and middle.
- Verify removed ranges no longer exist.

`test_bitmaps()` covers bitmap-entry-only behavior:
- Add bitmap free space and remove it entirely.
- Remove a middle chunk.
- Add a free range straddling two bitmap regions and remove an overlapping portion.

`test_bitmaps_and_extents()` covers mixed representation:
- Extent and bitmap entries at related offsets.
- Removing from extent while bitmap remains.
- Removing from bitmap while extent remains.
- Removing overlapping ranges represented by both extent and bitmap entries.
- Cases where an extent starts before a bitmap and deletion falls inside both.
- A regression where removal spanning bitmap plus extent should not leak `-EAGAIN`.

Bitmap-to-extent stealing:
- `test_steal_space_from_bitmap_to_extent()` temporarily overrides `free_space_ctl->op->use_bitmap` to force bitmap use after an extent exists.
- It constructs adjacent extent/bitmap representations that together form a larger free range.
- It verifies that contiguous bitmap free space can be stolen into an extent entry so a 1 MiB allocation can be satisfied from a single entry.
- It tests both directions: extent on the left of bitmap and extent on the right of bitmap.
- It verifies unrelated small bitmap free ranges are not accidentally stolen.
- `check_cache_empty()` ensures allocation drains all free space and leaves no entries.

Bytes index:
- `test_bytes_index()` validates `free_space_bytes` ordering by descending bytes for extent entries and bitmap entries.
- It tests bitmap entries where total bytes and `max_extent_size` differ, forcing `btrfs_find_space_for_alloc()` to recalculate and reorder the bytes index.
- It verifies later additions reindex by total bytes and allocation selects the expected bitmap.

`btrfs_test_free_space_cache()` creates dummy fs_info, a block group large enough to cross bitmap boundaries even on large-page systems, inserts an extent-tree root, and runs all free-space-cache suites.

Correctness focus:
- Free-space cache operations must remove exactly the requested ranges across extent and bitmap representations.
- Mixed representation must not leave duplicate or stale free ranges.
- Large allocations must not fail just because contiguous free space is split between bitmap and extent entries.
- The bytes index must reflect either total bytes or max contiguous extent size at the correct times.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/free-space-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/free-space-tree-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/free-space-tree-tests.c

Read completely: 586 lines.

This file tests the on-disk free-space tree update logic using dummy roots, block groups, and transactions.

Validation:
- `__check_free_space_extents()` reads the free-space info item and verifies expected extents in either extent-item format or bitmap format.
- For bitmap format, it walks bitmap keys and tests each sectorsize-aligned bit with `btrfs_free_space_test_bit()`.
- For extent format, it verifies item count and each `BTRFS_FREE_SPACE_EXTENT_KEY`.
- `check_free_space_extents()` validates the current format, converts to the opposite format, and validates again.

Test scenarios:
- `test_empty_block_group()` expects the whole block group to be free.
- `test_remove_all()` removes all free space.
- `test_remove_beginning()` removes the first aligned unit.
- `test_remove_end()` removes the last aligned unit.
- `test_remove_middle()` creates two free extents around a removed middle range.
- `test_merge_left()` adds adjacent space to the right of an existing range and expects merge.
- `test_merge_right()` adds adjacent space to the left and expects merge.
- `test_merge_both()` fills a gap between two ranges and expects one merged range.
- `test_merge_none()` adds separated ranges and expects no merge.

`run_test()` creates a dummy free-space-tree root, dummy block group, dummy transaction handle, path, and initial free-space tree entry. It optionally converts initial representation to bitmaps, runs a test, removes the block group free-space items, and verifies the root leaf has no leftover items.

`run_test_both_formats()` runs each scenario starting from extent format and bitmap format.

`btrfs_test_free_space_tree()` runs all scenarios with two alignments:
- sectorsize alignment
- `BTRFS_FREE_SPACE_BITMAP_BITS * PAGE_SIZE`, chosen to exercise extent-buffer bitmap handling around page boundaries and highmem-sensitive paths

Correctness focus:
- Free-space tree add/remove operations must produce identical logical free extents in extent and bitmap formats.
- Conversion between formats must preserve exact free-space state.
- Block-group free-space teardown must remove all items from the free-space tree.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/free-space-tree-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/inode-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/inode-tests.c

Read completely: 1095 lines.

This file tests inode extent lookup and outstanding extent accounting.

Tree setup helpers:
- `insert_extent()` inserts a synthetic `BTRFS_EXTENT_DATA_KEY` item into a dummy level-0 root leaf, supporting inline, regular, prealloc, compressed, and explicit-hole file extent items.
- `insert_inode_item_key()` inserts a minimal inode item key used by the hole-first test.
- `setup_file_extents()` builds a dense synthetic file layout covering inline extents, implied holes, explicit holes, regular extents, split regular extents, prealloc extents, partially written prealloc extents, compressed extents, split compressed extents, and a final regular extent after a no-item hole.

`test_btrfs_get_extent()`:
- First verifies an empty tree returns `EXTENT_MAP_HOLE`.
- Then loads the complex extent layout and walks it with `btrfs_get_extent()`.
- It validates for each returned extent map:
  - `disk_bytenr` kind: inline, hole, or real physical extent
  - logical start and length
  - flags for prealloc and compressed extents
  - offset handling for split extents
  - physical block start adjustments
  - compression type for zlib compressed extents
- It specifically checks inline extent rounding to sectorsize, explicit holes, implied holes between extents, prealloc flags, compressed flags, and split compressed extent offsets.

`test_hole_first()`:
- Builds a tree where the first file range is a hole and a regular extent starts at sectorsize.
- Verifies `btrfs_get_extent()` returns a sectorsize-sized hole for `[0,sectorsize)` and then the expected real extent.

`test_extent_accounting()`:
- Exercises `btrfs_set_extent_delalloc()` and `btrfs_clear_extent_bit()` over large delalloc regions split around `BTRFS_MAX_EXTENT_SIZE`.
- Validates `BTRFS_I(inode)->outstanding_extents` as regions are added, split by holes, rejoined, split again, refilled, and finally cleared.
- Ensures large delalloc ranges are counted as the correct number of extent-sized units.

`btrfs_test_inodes()` sets expected flag masks for compressed and prealloc extents, then runs:
- `test_btrfs_get_extent()`
- `test_hole_first()`
- `test_extent_accounting()`

Correctness focus:
- `btrfs_get_extent()` must correctly translate on-disk file extent items into in-memory extent maps across inline, hole, regular, prealloc, and compressed cases.
- Offset and block-start math for split extents is heavily validated.
- Delalloc outstanding extent accounting must track logical splits and merges rather than just raw byte presence.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/inode-tests.c -->