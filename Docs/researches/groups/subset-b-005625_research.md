# subset-b-005625 Research

Grouped research for Btrfs sysfs support and the Btrfs in-kernel selftest files listed in work item `subset-b-005625`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/sysfs.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/sysfs.c

## Purpose

`sysfs.c` is the Btrfs sysfs surface. It creates the global `/sys/fs/btrfs` kset, publishes kernel-supported feature files, and adds per-filesystem, per-device, per-allocation, discard, and qgroup kobjects under `/sys/fs/btrfs/<uuid>`. It is runtime integration code rather than an algorithm module: it turns `btrfs_fs_info`, `btrfs_fs_devices`, `btrfs_device`, `btrfs_space_info`, block group profile, and qgroup state into sysfs attributes and accepts a small set of privileged tunables.

## Important APIs, Types, And Functions

- `struct btrfs_feature_attr` wraps `struct kobj_attribute` with a feature set and bit. `BTRFS_FEAT_ATTR_*` instantiate known feature files.
- `struct raid_kobject` stores a RAID profile flag plus a `kobject` for `/allocation/<space>/<profile>`.
- Attribute macros `BTRFS_ATTR`, `BTRFS_ATTR_RW`, `BTRFS_ATTR_W`, and `BTRFS_ATTR_PTR` centralize kobj attribute creation.
- Feature helpers: `get_features()`, `set_features()`, `can_modify_feature()`, `btrfs_feature_attr_show()`, `btrfs_feature_attr_store()`, `btrfs_feature_visible()`, `init_feature_attrs()`, `addrm_unknown_feature_attrs()`, `btrfs_printable_features()`, and `btrfs_feature_set_name()`.
- Lifecycle APIs exported through `sysfs.h`: `btrfs_init_sysfs()`, `btrfs_exit_sysfs()`, `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, `btrfs_sysfs_remove_mounted()`, `btrfs_sysfs_add_device()`, `btrfs_sysfs_remove_device()`, `btrfs_sysfs_add_space_info_type()`, `btrfs_sysfs_remove_space_info()`, `btrfs_sysfs_add_block_group_type()`, qgroup add/remove helpers, and rename/update helpers for fsid/devid.
- Tunable show/store handlers cover filesystem label, feature bits, discard limits, space-info chunk size and reclaim thresholds, global read policy, quota override, commit stats reset, device scrub speed limit, and qgroup subtree drop threshold.

## Control Flow

Module initialization calls `btrfs_init_sysfs()`, creates the `btrfs` kset under `fs_kobj`, initializes printable/unknown feature metadata, creates the dynamic feature group, merges static feature files, and optionally creates a debug group. Shutdown reverses those groups and unregisters the kset.

Device discovery can call `btrfs_sysfs_add_fsid()` before mount. It initializes the fsid kobject named by UUID and creates child `devices` and `devinfo` directories. Mount completion calls `btrfs_sysfs_add_mounted()`, which adds device links and devinfo entries, per-fs attributes, feature group, optional debug directory, discard directory, unknown feature files, the `bdi` link, and the top-level `allocation` directory.

Space information is added after allocation state exists. `btrfs_sysfs_add_space_info_type()` creates `/allocation/<type>` from `alloc_name()`. `btrfs_sysfs_add_block_group_type()` creates one child kobject per RAID profile under a space-info kobject, using `memalloc_nofs_save()` to avoid reclaim recursion during transaction or lock contexts. Removal walks RAID profile kobjects and then drops the space-info kobject.

Unmount uses `btrfs_sysfs_remove_mounted()` to remove links, files, child kobjects, unknown feature attributes, feature group, mounted attributes, and all device entries. `btrfs_sysfs_remove_fsid()` removes the base fsid tree for one filesystem or all known fsids.

Qgroup sysfs integration is lazy around qgroup initialization. `btrfs_sysfs_add_qgroups()` creates `/qgroups`, then adds one kobject per qgroup from `fs_info->qgroup_tree`; deletion walks the tree and drops children before the parent.

## State And Persistence Behavior

Sysfs files mostly reflect in-memory kernel state. Some store paths mutate persistent filesystem-superblock-related state indirectly:

- Feature bit and label changes update `fs_info->super_copy` under `super_lock`, set `BTRFS_FS_NEED_TRANS_COMMIT`, and wake `transaction_kthread`; the sysfs write itself does not commit a transaction.
- Read policy and discard limits update live `fs_devices` or `discard_ctl` fields with `READ_ONCE`/`WRITE_ONCE`; discard writes may reschedule discard work.
- Chunk size and reclaim thresholds update live `btrfs_space_info`/`fs_info` policy fields.
- Qgroup show/store handlers read or update qgroup flags/thresholds under `qgroup_lock`.
- Kobject state is embedded in long-lived Btrfs structures. Release callbacks zero embedded kobject storage and complete unregister completions so callers can wait for sysfs teardown.

## Dependencies And Integration Points

This file depends heavily on Linux kobject/sysfs APIs, Btrfs feature flag accessors, the transaction subsystem, discard work scheduling, space-info/block-group state, device-volume structures, qgroups, and superblock accessors. It is called from mount, unmount, device discovery, device add/remove/replace, chunk allocation, qgroup initialization, and module init/exit paths.

External observability is the sysfs ABI under `/sys/fs/btrfs`. It also sends block device uevents through `btrfs_kobject_uevent()` and maintains user-visible links to block devices and BDI state.

## Risks

The highest risk is lifetime ordering: sysfs kobjects expose embedded structures while mount/unmount, device removal, qgroup deletion, and seed-device teardown are possible. The code mitigates this with `state_initialized`, release callbacks, completions, and paired `kobject_del()`/`kobject_put()`, but double-add/double-remove and missing parent kobjects would still be dangerous.

Store methods need privilege and input validation discipline. Some paths require `CAP_SYS_ADMIN` or `CAP_SYS_RESOURCE`, reject read-only filesystems, parse with `kstrto*()` or `memparse()`, and bound values such as chunk size, thresholds, and read-policy parameters. Any new tunable should follow the same pattern and consider whether it can safely run in sysfs context.

Feature writes are intentionally limited to safe set/clear masks. Unknown feature files are dynamically added for unsupported bits so users can observe them but not mutate them. This avoids hiding important compatibility state.

## Test Signals

There is no direct unit test in this subset for sysfs. Test signals are integration-style: mount/unmount should create and remove the expected sysfs tree; feature visibility should match superblock flags; store handlers should reject invalid input, readonly filesystems, and missing capabilities; qgroup and device directories should appear and disappear with qgroup/device lifecycle. The selftests in this subset exercise many underlying data structures but not kobject/sysfs behavior directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/sysfs.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/sysfs.h

## Purpose

`sysfs.h` declares the Btrfs sysfs API used by mount, unmount, device, allocation, qgroup, and module lifecycle code. It also defines the public enum used to classify compatibility feature sets.

## Important APIs, Types, And Functions

- `enum btrfs_feature_set` identifies `FEAT_COMPAT`, `FEAT_COMPAT_RO`, and `FEAT_INCOMPAT`, with `FEAT_MAX` as the array bound.
- Feature reporting: `btrfs_printable_features()` and `btrfs_feature_set_name()`.
- Global lifecycle: `btrfs_init_sysfs()` and `btrfs_exit_sysfs()`.
- Fsid and mount lifecycle: `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, `btrfs_sysfs_remove_mounted()`, and `btrfs_sysfs_update_sprout_fsid()`.
- Device lifecycle: `btrfs_sysfs_add_device()`, `btrfs_sysfs_remove_device()`, `btrfs_sysfs_update_devid()`, and `btrfs_kobject_uevent()`.
- Allocation lifecycle: `btrfs_sysfs_add_block_group_type()`, `btrfs_sysfs_add_space_info_type()`, and `btrfs_sysfs_remove_space_info()`.
- Qgroup lifecycle: `btrfs_sysfs_add_qgroups()`, `btrfs_sysfs_del_qgroups()`, `btrfs_sysfs_add_one_qgroup()`, and `btrfs_sysfs_del_one_qgroup()`.
- Read policy parsing: `btrfs_read_policy_to_enum()`, plus experimental module-parameter helpers under `CONFIG_BTRFS_EXPERIMENTAL`.

## Control Flow

The header does not implement behavior, but its API grouping mirrors the expected flow: initialize global sysfs during module setup, add an fsid directory during device discovery, enrich it on mount, add/remove device and allocation children as runtime state changes, expose qgroups when initialized, and tear down mounted and base fsid state during unmount or module exit.

## State And Persistence Behavior

The declarations expose functions that mutate kobject state embedded in `btrfs_fs_devices`, `btrfs_device`, `btrfs_space_info`, and `btrfs_qgroup`. Some sysfs store handlers behind these declarations can update superblock-derived state through transaction commit scheduling, but the header itself only defines the interface contract.

## Dependencies And Integration Points

The file forward-declares Btrfs and block-layer structures to keep include coupling low and includes only basic kernel types, compiler annotations, and kobject definitions. It is the integration boundary between `sysfs.c` and other Btrfs modules such as volumes, disk-io, qgroups, block groups, and mount lifecycle code.

## Risks

Because kobjects are embedded in long-lived Btrfs structures, callers must respect add/remove pairing and avoid using sysfs helpers on partially initialized objects. The conditional experimental read-policy declarations also require call sites to be guarded consistently by `CONFIG_BTRFS_EXPERIMENTAL`.

## Test Signals

Compile-time coverage verifies prototypes and configuration guards. Runtime signals are expected sysfs directory creation/removal for fsid, devices, allocation types, qgroups, and mounted attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.c

## Purpose

`btrfs-tests.c` is the shared harness for Btrfs in-kernel sanity tests enabled by `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`. It provides a pseudo filesystem mount, dummy Btrfs allocation helpers, transaction initializers, and the top-level `btrfs_run_sanity_tests()` dispatcher.

## Important APIs, Types, And Functions

- `test_mnt` stores the pseudo filesystem mount used for test inode allocation.
- `test_error[]` maps shared allocation failure indexes from `btrfs-tests.h` to log strings.
- `btrfs_test_init_fs_context()`, `test_type`, `btrfs_init_test_fs()`, and `btrfs_destroy_test_fs()` register, mount, unmount, and unregister the pseudo filesystem.
- `btrfs_new_test_inode()` allocates a regular inode from `test_mnt` and initializes Btrfs inode number and ownership.
- `btrfs_alloc_dummy_fs_info()` and `btrfs_free_dummy_fs_info()` build and tear down a minimal `btrfs_fs_info` with `fs_devices`, `super_copy`, buffer tree, checksum sizing, and dummy state.
- `btrfs_alloc_dummy_device()` creates a `btrfs_device`, initializes its `alloc_state`, and links it to `fs_info->fs_devices->devices`.
- `btrfs_alloc_dummy_block_group()` and `btrfs_free_dummy_block_group()` create block group/free-space-control scaffolding.
- `btrfs_init_dummy_transaction()` and `btrfs_init_dummy_trans()` initialize enough delayed-ref and transaction handle state for tests.
- `btrfs_run_sanity_tests()` runs all registered sanity tests across supported sectorsize/nodesize combinations, then extent-map and zoned tests.

## Control Flow

`btrfs_run_sanity_tests()` registers and mounts the pseudo filesystem first. It then loops through `test_sectorsize[]` and powers-of-two nodesizes up to `BTRFS_MAX_METADATA_BLOCKSIZE`, running free-space cache, extent buffer, extent I/O, inode, qgroup, free-space tree, raid-stripe-tree, delayed-ref, and chunk-allocation tests. After the nodesize loop, it runs extent-map tests and zoned tests, then unmounts and unregisters the pseudo filesystem.

Dummy allocators are intentionally minimal but initialize the fields used by production helpers. Cleanup releases extent buffers from `fs_info->buffer_tree`, mapping trees, devices, qgroup config, fs roots, superblock copy, and leak debug checks.

## State And Persistence Behavior

All state is in-memory test state. `btrfs_alloc_dummy_fs_info()` sets `BTRFS_FS_STATE_DUMMY_FS_INFO`, installs the dummy `fs_info` into the pseudo superblock, and configures sizes and checksum metadata. No disk persistence occurs. Cleanup is strict because production helpers may populate xarrays, mapping trees, roots, qgroups, and extent buffers.

## Dependencies And Integration Points

This harness integrates with Linux pseudo filesystems, VFS inode allocation, Btrfs inode allocation/destruction, free-space cache/tree, transactions, volumes, qgroups, block groups, and disk-io helpers. Every test file in this subset depends on these helpers through `btrfs-tests.h`.

## Risks

The dummy objects are intentionally incomplete, so tests must only call production paths whose dependencies are initialized. Missing cleanup can leak extent buffers, roots, devices, or qgroup config and make later tests unreliable. The harness stops on first failure inside the sectorsize/nodesize loop, so one failing test can hide later failures.

## Test Signals

The top-level test signal is a zero return from `btrfs_run_sanity_tests()`. Each subtest logs its name through `test_msg()` and returns negative errno-like failures. Allocation failures use shared `test_std_err()` messages to identify the missing dummy object class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.h

## Purpose

`btrfs-tests.h` is the shared declaration and logging header for Btrfs sanity tests. It exposes the top-level test runner, individual test entry points, dummy object helpers, and no-op fallbacks when sanity tests are disabled.

## Important APIs, Types, And Functions

- `btrfs_run_sanity_tests()` is declared as a real runner when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled and as an inline zero-return no-op otherwise.
- `test_msg()` and `test_err()` wrap `pr_info()`/`pr_err()` with a Btrfs selftest prefix; `test_err()` includes file and line.
- Allocation error enum values identify shared failure classes such as fs_info, root, extent buffer, path, inode, block group, extent map, chunk map, I/O context, and transaction.
- Individual entry points include extent buffer, free-space cache, extent I/O, inode, qgroup, free-space tree, raid stripe tree, extent map, delayed refs, chunk allocation, and zoned tests.
- Dummy helpers allocate/free inodes, `fs_info`, roots, block groups, transactions, and devices.
- `DEFINE_FREE()` wrappers provide cleanup support for dummy `fs_info` and block groups.

## Control Flow

The header uses `#ifdef CONFIG_BTRFS_FS_RUN_SANITY_TESTS` as its main switch. Enabled builds get declarations for test code compiled elsewhere; disabled builds get only a stub runner. Zoned tests have a second configuration split: `btrfs_test_zoned()` is real only under `CONFIG_BLK_DEV_ZONED`, otherwise it returns success.

## State And Persistence Behavior

The header declares helpers that manage in-memory dummy state. It contains no persistent state, but its cleanup wrappers encode ownership expectations for dummy `fs_info` and block groups.

## Dependencies And Integration Points

It depends on basic kernel types and cleanup helpers, forward declares Btrfs transaction/root types, and is included by all Btrfs test files in this subset. It is also the ABI between normal Btrfs initialization code and the optional sanity-test runner.

## Risks

Configuration guards must match the compilation of the test implementation files. Adding a new test requires adding a prototype here and wiring it into `btrfs_run_sanity_tests()`. Incorrect dummy helper ownership can cause leaks or double frees across test files.

## Test Signals

The header defines the common logging and error vocabulary used by all selftests, so consistent `test_msg()`, `test_err()`, and `test_std_err()` output is the main diagnostic signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/chunk-allocation-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/chunk-allocation-tests.c

## Purpose

`chunk-allocation-tests.c` tests pending extent helper behavior in the Btrfs chunk allocator. The target production functions search the per-device `alloc_state` extent I/O tree for pending chunk allocations and holes that are still available.

## Important APIs, Types, And Functions

- `struct pending_extent_test_case` describes a search range, minimum hole size, up to two pending extents, and expected `btrfs_find_hole_in_pending_extents()` output.
- `find_hole_tests[]` covers empty pending state, overlaps at range start/end, multiple holes, holes too small, fully allocated ranges, and zero-length search input.
- `test_find_hole_in_pending()` builds dummy `fs_info` and device state, sets `CHUNK_ALLOCATED` bits, calls `btrfs_find_hole_in_pending_extents()` under `chunk_mutex`, validates returned range/found state, and clears pending bits each iteration.
- `struct first_pending_test_case` and `first_pending_tests[]` describe expected output from `btrfs_first_pending_extent()`.
- `test_first_pending_extent()` validates first-pending lookup for absent, exact, overlapping, inside, outside, and end-overlapping ranges.
- `btrfs_test_chunk_allocation()` runs both helper test groups.

## Control Flow

Each test allocates a dummy filesystem and dummy device, then iterates a static table. For non-empty pending extents it marks `device->alloc_state` with `CHUNK_ALLOCATED`. The production helper is called while holding `fs_info->chunk_mutex`, mirroring allocator locking. On mismatch, the test logs the named case, clears the extent tree state, and exits with `-EINVAL`.

## State And Persistence Behavior

State is entirely in memory in `device->alloc_state`. The tests use byte ranges at GiB-scale boundaries but only manipulate extent-state metadata, not real storage. Cleanup clears all `CHUNK_ALLOCATED` bits and frees the dummy `fs_info`, which frees the dummy device.

## Dependencies And Integration Points

The tests depend on `btrfs_alloc_dummy_fs_info()`, `btrfs_alloc_dummy_device()`, extent I/O tree bit helpers, `fs_info->chunk_mutex`, and production chunk allocation helpers in `volumes.c`/related code.

## Risks

The table assumes at most two pending extents, enough to produce up to three holes. If production behavior changes to prefer a different “best” hole when no hole meets the minimum size, the expected start/len for `expected_found=false` cases may need updates. Locking is represented only by a mutex around the helper call, not by concurrent allocator threads.

## Test Signals

Success is zero from `btrfs_test_chunk_allocation()`. Failures name the table case and print expected versus actual found state or range. Coverage is strong for range-boundary semantics and weak for real chunk allocation side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/chunk-allocation-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/delayed-refs-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/delayed-refs-tests.c

## Purpose

`delayed-refs-tests.c` validates Btrfs delayed reference node/head creation, merging, cancellation, and selection ordering. It exercises production delayed-ref insertion and selection helpers against a dummy transaction.

## Important APIs, Types, And Functions

- `struct ref_head_check` and `struct ref_node_check` encode expected delayed-ref head and node fields.
- `ref_type_from_disk_ref_type()` maps disk ref item types to metadata or data reference categories.
- `validate_ref_head()` checks bytenr, num_bytes, `ref_mod`, `total_ref_mod`, and `must_insert_reserved`.
- `validate_ref_node()` checks bytenr, num_bytes, action, ref type, parent, root, owner, and offset.
- `simple_test()` converts a `ref_node_check` into a `struct btrfs_ref`, inserts one delayed ref, selects the head and node, validates both, and destroys delayed refs.
- `simple_tests()` covers add/drop operations for tree block, data, shared block, and shared data references.
- `merge_tests()` stresses add/drop cancellation and merging for metadata and data refs, including double adds/drops, positive/negative transitions, and many refs with different roots/parents.
- `select_delayed_refs_test()` validates that add operations are selected before delete operations, even when rb-tree ordering differs and when one add is removed by merging.
- `btrfs_test_delayed_refs()` builds dummy `fs_info`, transaction, and handle, then runs all groups.

## Control Flow

Tests allocate a dummy `fs_info`, allocate and initialize a dummy `btrfs_transaction`, attach it to a dummy transaction handle, then run simple, merge, and selection tests. The helper functions call production `btrfs_add_delayed_tree_ref()` and `btrfs_add_delayed_data_ref()`, then use `btrfs_select_ref_head()` and `btrfs_select_delayed_ref()` to inspect the resulting structures.

When a selected node/head is consumed manually, helpers erase rb-tree nodes, drop add-list entries, unselect heads, call `btrfs_delete_ref_head()`, unlock delayed-ref heads, and release references. Each subcase destroys delayed refs to reset transaction state.

## State And Persistence Behavior

The persistent model under test is transaction-local delayed-ref state: rb-trees, ref heads, ref nodes, counters, and selection state. There is no disk persistence. Correct cleanup is important because delayed refs carry reference counts and selected-head state.

## Dependencies And Integration Points

The file integrates with transaction setup from `btrfs-tests.c`, delayed-ref internals, extent-tree reference types, rb-tree/list manipulation, and delayed-ref locking. It validates behavior that later extent-tree update and qgroup accounting paths depend on.

## Risks

Because the tests inspect internal fields directly, they are sensitive to delayed-ref representation changes. They validate deterministic single-threaded outcomes, not concurrent insertion/selection races. Manual deletion helpers must mirror production ownership rules; stale selected heads or leaked refs would poison later cases.

## Test Signals

Failure messages report exact field mismatches for heads or nodes. The merge tests specifically signal regressions in cancellation, net ref counts, empty-node cases, and add-before-drop selection order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/delayed-refs-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-buffer-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-buffer-tests.c

## Purpose

`extent-buffer-tests.c` validates item splitting inside a Btrfs leaf extent buffer. It focuses on `btrfs_split_item()` preserving keys, item sizes, data contents, and slot ordering when a leaf item is split once and then split again with item movement.

## Important APIs, Types, And Functions

- `test_btrfs_split_item()` builds a dummy root, path, and extent buffer, inserts a checksum item containing `"mary had a little lamb"`, then splits it into expected string fragments.
- `btrfs_setup_item_for_insert()`, `write_extent_buffer()`, `read_extent_buffer()`, `btrfs_split_item()`, `btrfs_item_key_to_cpu()`, `btrfs_item_size()`, and `btrfs_item_ptr_offset()` are the production helpers under inspection.
- `btrfs_test_extent_buffer_operations()` is the exported selftest entry point.

## Control Flow

The test creates a single-node dummy tree with one item at slot 0. It splits the item at offset 17 with a new key offset of 3 and verifies two slots. It then splits slot 0 again at offset 4 with a new key offset of 1 and verifies three slots, including the item movement of the prior second fragment.

## State And Persistence Behavior

All state is in a dummy extent buffer and dummy root. Passing a `NULL` transaction handle is valid here because the tree is a single test leaf with enough room and no real persistence or COW path is needed.

## Dependencies And Integration Points

The test depends on dummy fs/root/path allocation, extent buffer allocation, Btrfs item layout accessors, and core ctree item manipulation. It indirectly protects code used by metadata updates that split leaf items.

## Risks

The test uses fixed string data and one item type, so it checks byte movement and slot metadata but not all item sizes or leaf-boundary conditions. It assumes `btrfs_split_item()` can safely run with `NULL` transaction in this constrained dummy setup.

## Test Signals

Failures report invalid keys, lengths, split return codes, or mismatched data fragments. A zero return from `btrfs_test_extent_buffer_operations()` means the split scenarios passed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-buffer-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-io-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-io-tests.c

## Purpose

`extent-io-tests.c` tests several Btrfs extent I/O primitives: delalloc range discovery and page locking, extent-buffer bitmap operations, clear-range search in an extent-state tree, and extent-buffer memory copy/move behavior across pages.

## Important APIs, Types, And Functions

- `process_page_range()` walks contiguous folios in an inode mapping, optionally checks locking, unlocks, and releases them.
- `extent_flag_to_str()` and `dump_extent_io_tree()` provide failure diagnostics for extent-state trees.
- `test_find_delalloc()` exercises `find_lock_delalloc_range()` against dirty page cache and `EXTENT_DELALLOC` ranges.
- `check_eb_bitmap()`, `test_bitmap_set()`, `test_bitmap_clear()`, `__test_eb_bitmaps()`, and `test_eb_bitmaps()` compare extent-buffer bitmap helpers against a normal bitmap.
- `test_find_first_clear_extent_bit()` checks `btrfs_find_first_clear_extent_bit()` on empty trees, holes between set ranges, partial flag matches, and beyond-end searches.
- `dump_eb_and_memory_contents()`, `verify_eb_and_memory()`, `init_eb_and_memory()`, and `test_eb_mem_ops()` compare extent-buffer memory operations with normal `memcpy()`/`memmove()`.
- `btrfs_test_extent_io()` runs all groups.

## Control Flow

`test_find_delalloc()` allocates a dummy inode/root/fs_info, creates and dirties enough pages for two max-size extents, pins the first locked page, sets delalloc ranges, and checks that `find_lock_delalloc_range()` returns expected start/end and locks all pages in the returned range. It also checks behavior when no matching range exists and when a page inside the delalloc span is no longer dirty.

Bitmap tests allocate an extent buffer at offset 0 and again at a sectorsize offset, then run full clear/set, same-byte, cross-byte, cross-page, and pseudo-random bit patterns. Clear-range tests mutate an `extent_io_tree` with `CHUNK_TRIMMED`/`CHUNK_ALLOCATED` flags and validate returned holes. Memory operation tests initialize an extent buffer and mirror memory with random bytes, then compare normal memory operations to `memcpy_extent_buffer()` and `memmove_extent_buffer()`.

## State And Persistence Behavior

State is in page cache folios, Btrfs inode `io_tree`, dummy extent buffers, and local bitmaps/memory buffers. No disk persistence occurs. Cleanup unlocks/releases pages, clears extent bits, frees extent buffers, and frees dummy roots/fs_info.

## Dependencies And Integration Points

The file integrates with Linux page cache/folio APIs, Btrfs extent I/O trees, extent buffer accessors, dummy inode/root setup, and memory helpers. It protects behavior used by writeback/delalloc, metadata bitmap manipulation, and metadata buffer copies.

## Risks

`test_find_delalloc()` is sensitive to page size, dirty page state, and lock cleanup; a missed unlock or put can destabilize later tests. It validates representative page/extent layouts but not true concurrent writeback races. Bitmap and memory tests provide broad boundary coverage but are limited to dummy buffers.

## Test Signals

Failures report missing delalloc ranges, wrong start/end, unlocked pages, bitmap mismatches with byte dumps, wrong clear-range results, or extent-buffer/memory divergence. `dump_extent_io_tree()` is used on extent-tree failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-io-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-map-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-map-tests.c

## Purpose

`extent-map-tests.c` validates the Btrfs in-memory extent map tree. It covers overlap handling in `btrfs_add_extent_mapping()`, dropping/splitting ranges, pinned compressed extents, compressed offset adjustment, reverse physical-to-logical mapping, and extent-map reference cleanup.

## Important APIs, Types, And Functions

- `free_extent_map_tree()` removes all mappings from a Btrfs inode and, under debug builds, checks extent-map reference counts.
- `test_case_1()` through `test_case_4()` simulate concurrent buffered/direct I/O races where adding an extent map collides with an existing broader or split mapping and should return a usable existing/adjusted map rather than fail.
- `add_compressed_extent()` inserts compressed mappings that do not merge.
- `valid_ranges[][]` and `validate_range()` define expected extent-map tree state after range drops.
- `test_case_5()` validates `btrfs_drop_extent_map_range()` front, back, double split, and full-drop behavior.
- `test_case_6()` checks that add-gap logic does not create an unwanted bridging map when adjacent unmerged maps exist.
- `test_case_7()` is a regression test for `skip_pinned=true` drop logic.
- `test_case_8()` is a regression test for compressed extent offset adjustment after partial overlap.
- `struct rmap_test_vector`, `test_rmap_block()`, and `btrfs_test_extent_map()` validate `btrfs_rmap_block()` using dummy chunk maps/devices.

## Control Flow

The entry point allocates a dummy 4 KiB `fs_info`, dummy inode, and dummy root, assigns the root to the inode, and runs eight extent-map cases. Each case builds a specific map layout, calls the production operation, inspects returned maps or rb-tree contents, and then frees the tree. After extent-map cases, it runs reverse mapping vectors by building chunk maps with dummy devices, adding them to the mapping tree, calling `btrfs_rmap_block()` for a superblock physical offset, and checking logical outputs.

## State And Persistence Behavior

State is in `BTRFS_I(inode)->extent_tree`, chunk mapping trees, and dummy device lists. No disk is touched. Extent maps use reference counting, pinned flags, compressed flags, offsets, disk byte ranges, and rb-tree nodes, so cleanup is part of the correctness check.

## Dependencies And Integration Points

The tests depend on Btrfs inode extent-map APIs, chunk map allocation and mapping-tree insertion/removal, dummy device allocation, block-group/volume definitions, and rb-tree locking around extent-map operations. They protect behavior used by buffered reads, direct I/O, encoded writes, compressed extents, and device superblock scanning.

## Risks

Many cases encode historical race/regression scenarios. They are single-threaded simulations of concurrent outcomes, so they validate final-state logic but not locking races themselves. Fixed 4 KiB assumptions in the extent-map runner are intentional because the hard-coded extents are based on 4 KiB units.

## Test Signals

Failures report unexpected return codes, wrong returned extent map ranges, missing or extra rb-tree entries, wrong block starts/offsets, leaked refs under debug, or incorrect reverse-mapped logical addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-map-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tests.c

## Purpose

`free-space-tests.c` validates the in-memory free-space cache for block groups. It tests extent-only entries, bitmap-only entries, mixed extent/bitmap removal, stealing contiguous free space from bitmap entries into extent entries, and the free-space bytes index.

## Important APIs, Types, And Functions

- `test_extents()` checks full, front, tail, and middle removal from extent entries.
- `test_bitmaps()` checks full and middle removal from bitmap entries and removal across two bitmap regions.
- `test_bitmaps_and_extents()` checks overlapping removals when free space is represented by both extents and bitmaps.
- `test_use_bitmap()` and `test_steal_space_from_bitmap_to_extent()` force bitmap selection to build targeted layouts, then validate coalescing/stealing behavior around adjacent extent/bitmap free ranges.
- `check_num_extents_and_bitmaps()` and `check_cache_empty()` assert free-space-control counters and allocation behavior.
- `bytes_index_use_bitmap()` and `test_bytes_index()` validate ordering and recalculation of `free_space_bytes` for extents and bitmaps.
- `btrfs_test_free_space_cache()` builds dummy fs/block group/root state and runs all groups.

## Control Flow

The entry point creates a dummy fs_info, a block group large enough to cross bitmap boundaries, and a dummy extent-tree root, then inserts the root globally. It runs simple extent tests, bitmap tests, mixed tests, bitmap-to-extent stealing tests, and bytes-index tests. Each subtest adds free-space entries, removes or allocates ranges with production cache helpers, and checks existence/counters.

The stealing test temporarily replaces `cache->free_space_ctl->op` with a test policy that forces bitmap use after at least one extent exists. It constructs adjacent extent/bitmap ranges on both sides, leaves small non-contiguous bitmap ranges behind, then verifies that large contiguous ranges can be allocated as one extent and that only the small bitmap ranges remain.

The bytes-index test validates descending order by bytes, bitmap entry ordering, max-extent-size recalculation after failed searches, and reordering after later additions.

## State And Persistence Behavior

State is entirely in `cache->free_space_ctl`: rb-trees, bitmap entries, extent entries, free-space counters, bitmap counts, and bytes-index ordering. The dummy root is registered because production free-space helpers expect global root context, but no persistent free-space tree is written here.

## Dependencies And Integration Points

This file depends on free-space-cache internals, block group scaffolding, dummy root/fs helpers, extent-tree root registration, and allocation helpers such as `btrfs_find_space_for_alloc()`, `btrfs_add_free_space()`, `btrfs_remove_free_space()`, `test_add_free_space_entry()`, and `test_check_exists()`.

## Risks

The test temporarily overrides free-space operations; failing before restoration would leave test-local state corrupted, though the final test restores before returning on the normal path. The scenarios are deterministic but do not model concurrent allocation/free. Some expectations depend on current bitmap threshold and bytes-index semantics.

## Test Signals

Failures report leftover free ranges, missing ranges, unexpected counters, wrong allocation offsets, wrong max extent sizes, or bytes-index misordering. A zero return from `btrfs_test_free_space_cache()` means the in-memory free-space cache scenarios passed for the requested sectorsize/nodesize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tree-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tree-tests.c

## Purpose

`free-space-tree-tests.c` validates the on-tree free-space representation used by Btrfs free-space-tree support. It tests adding, removing, merging, format conversion between extent items and bitmap items, and complete cleanup for a dummy block group.

## Important APIs, Types, And Functions

- `struct free_space_extent` encodes expected free ranges.
- `__check_free_space_extents()` inspects the free-space tree item layout directly, handling both extent-item and bitmap formats.
- `check_free_space_extents()` checks current format, converts to the opposite format with `btrfs_convert_free_space_to_extents()` or `btrfs_convert_free_space_to_bitmaps()`, and checks again.
- Test cases include `test_empty_block_group()`, `test_remove_all()`, `test_remove_beginning()`, `test_remove_end()`, `test_remove_middle()`, `test_merge_left()`, `test_merge_right()`, `test_merge_both()`, and `test_merge_none()`.
- `run_test()` builds a dummy free-space-tree root, dummy block group, dummy transaction/path, and runs one case in either extent or bitmap initial format.
- `run_test_both_formats()` executes each case in both representations.
- `btrfs_test_free_space_tree()` runs all cases with sectorsize alignment and a page-based bitmap alignment.

## Control Flow

Each `run_test()` creates a dummy fs/root, enables the free-space-tree compat-ro flag, sets the root as `BTRFS_FREE_SPACE_TREE_OBJECTID`, allocates a single leaf, creates a dummy block group of `8 * alignment`, marks it as needing free-space population, and adds block-group free space. If requested, it converts the representation to bitmaps before running the test.

The individual test mutates the free-space tree through `__btrfs_remove_from_free_space_tree()` or `__btrfs_add_to_free_space_tree()`, then validates expected ranges. After each case, the block group free-space items are removed and the root leaf is expected to have zero items.

## State And Persistence Behavior

State is in a dummy Btree leaf representing the free-space tree and a dummy block group. Although the APIs are production tree-modification helpers, the tree is not persisted to disk. The tests explicitly check both logical free ranges and physical item cleanup.

## Dependencies And Integration Points

The file integrates with Btrfs ctree item accessors, free-space-tree search/add/remove/convert helpers, transaction handle scaffolding, block group state, path allocation, and dummy extent buffers. It protects code used by filesystems with `BTRFS_FEATURE_COMPAT_RO_FREE_SPACE_TREE`.

## Risks

The direct tree inspection is tightly coupled to free-space-tree item layout. Format conversion is checked, which is valuable but means changes to bitmap sizing or item ordering require test updates. The dummy tree is single-leaf, so it does not cover multi-leaf split/merge behavior.

## Test Signals

Failures report missing free-space info, wrong extent counts, invalid tree item layout, conversion failures, leftover free-space-tree items, or case-specific failures annotated with function pointer, representation, sectorsize, nodesize, and alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tree-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/inode-tests.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/tests/inode-tests.c

## Purpose

`inode-tests.c` validates Btrfs inode extent lookup and outstanding delalloc extent accounting. It constructs synthetic file extent items that cover inline extents, holes, regular extents, prealloc extents, split extents, compressed extents, and implied holes, then checks `btrfs_get_extent()` output.

## Important APIs, Types, And Functions

- `insert_extent()` inserts a `BTRFS_EXTENT_DATA_KEY` item into a dummy leaf and initializes a `btrfs_file_extent_item`.
- `insert_inode_item_key()` inserts a minimal inode item key used by the hole-first test.
- `setup_file_extents()` builds a complex synthetic extent layout covering inline data, explicit and implied holes, regular/prealloc/compressed extents, and split extents with offsets.
- `test_btrfs_get_extent()` walks through the synthetic layout and validates `struct extent_map` fields returned by `btrfs_get_extent()`.
- `test_hole_first()` validates a file whose first range is an implied hole before a real extent.
- `test_extent_accounting()` validates `BTRFS_I(inode)->outstanding_extents` while setting, clearing, splitting, merging, and refilling delalloc ranges.
- `btrfs_test_inodes()` initializes expected flag masks and runs the three groups.

## Control Flow

`test_btrfs_get_extent()` creates a dummy inode/fs/root/leaf, first confirms that an empty tree returns a hole, then populates the leaf with `setup_file_extents()`. It calls `btrfs_get_extent()` sequentially from offset to offset, verifying each returned extent map’s `disk_bytenr`, `start`, `len`, flags, offset, block start, and compression type.

`test_hole_first()` inserts a blank inode item and one regular extent starting at `sectorsize`, then verifies a hole for `[0, sectorsize)` and a real extent after it. `test_extent_accounting()` mutates the inode `io_tree` with `btrfs_set_extent_delalloc()` and `btrfs_clear_extent_bit()` and validates outstanding extent counts after each split/merge shape.

## State And Persistence Behavior

The tests use a dummy inode root and in-memory extent buffer as the subvolume tree leaf. Extent maps are allocated and freed in memory; no disk persistence occurs. Delalloc accounting state lives in the inode’s `io_tree` and `outstanding_extents` counter and is cleared on failure and at the end.

## Dependencies And Integration Points

This file depends on Btrfs file extent item accessors, `btrfs_get_extent()`, compression flags, extent-map helpers, dummy inode/root/fs allocation, extent I/O tree delalloc helpers, and Btrfs inode accounting. It protects read path mapping and writeback reservation accounting behavior.

## Risks

The expected values are tightly coupled to the synthetic layout in `setup_file_extents()`, as the file comments warn. The tests are broad for mapping types but still single-leaf and single-threaded. The global static expected flag masks are updated with `|=`, so repeated invocations rely on idempotent bit setting.

## Test Signals

Failures report the exact unexpected extent-map field, compression type, flags, block start, or outstanding extent count. A zero return from `btrfs_test_inodes()` means extent lookup and delalloc accounting passed for the requested sectorsize/nodesize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/inode-tests.c -->
