# Group Research: group_958_linux_stable_sources_os_linux_linux_stable_fs_btrfs_tests_qgroup_tes_6d616d77f1ee

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/qgroup-tests.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/qgroup-tests.c

## Role

Self-test coverage for Btrfs qgroup extent accounting using an in-memory dummy filesystem. The file manually creates and removes extent items/backrefs, walks roots through `btrfs_find_all_roots()`, and calls `btrfs_qgroup_account_extent()` directly because the dummy transaction does not model full delayed-ref machinery.

## Main Entry Point

- `btrfs_test_qgroups(sectorsize, nodesize)`: allocates dummy `fs_info`, extent root, quota root, and two fs roots, enables `BTRFS_FS_QUOTA_ENABLED`, then runs the qgroup scenarios.

## Helpers

- `insert_normal_tree_ref()`: inserts an `EXTENT_ITEM` with one inline tree block ref, either `TREE_BLOCK_REF` for root-owned refs or `SHARED_BLOCK_REF` for parent refs.
- `add_tree_ref()`: increments the extent ref count and inserts a keyed tree/shared block ref item.
- `remove_extent_item()`: deletes the whole extent item.
- `remove_extent_ref()`: decrements the extent ref count and removes the keyed backref.

## Test Scenarios

- `test_no_shared_qgroup()`: creates qgroup for `BTRFS_FS_TREE_OBJECTID`, verifies adding one tree block charges referenced and exclusive bytes, then deleting it returns both counts to zero.
- `test_multiple_refs()`: creates a second qgroup, adds a second root ref to the same extent, verifies both qgroups become referenced but not exclusive, then removes one ref and verifies exclusivity returns to the remaining owner.

## Dependencies and Interactions

- Exercises qgroup APIs from `qgroup.h`, root discovery from `backref.h`, and item manipulation through ctree accessors.
- Uses `btrfs_init_dummy_trans()` rather than normal transaction start/commit.
- Relies on dummy roots inserted with `btrfs_insert_fs_root()` so backref walking can resolve root IDs.

## Error Handling Notes

- Allocation/search/insert failures log via self-test helpers and return kernel errno values.
- The test depends on `btrfs_qgroup_account_extent()` consuming/freeing old/new root ulists after successful accounting.
- The test intentionally avoids bytenr zero because backref walking expects nonzero block addresses.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/qgroup-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/raid-stripe-tree-tests.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/raid-stripe-tree-tests.c

## Role

Self-tests for RAID stripe tree insert, lookup, update, and deletion behavior. Each test creates a fresh dummy filesystem with the `RAID_STRIPE_TREE` incompat feature, a dummy stripe root, and two dummy devices.

## Main Entry Point

- `btrfs_test_raid_stripe_tree(sectorsize, nodesize)`: iterates a table of test functions and runs each through `run_test()`.

## Test Harness

- `run_test()`: builds dummy `fs_info`, root, empty leaf node, and two devices with devids `0` and `1`, then creates a dummy transaction.
- `btrfs_device_by_devid()`: local device lookup helper over `fs_devices->devices`.

## Covered Behaviors

- `test_simple_create_delete()`: inserts one RAID1 stripe extent, verifies physical mapping and length, then deletes it.
- `test_create_update_delete()`: overwrites an existing stripe extent with new physical addresses to exercise update behavior inside `btrfs_insert_one_raid_extent()`.
- `test_tail_delete()`: truncates the tail of an extent and verifies the remaining prefix plus hole lookup.
- `test_front_delete()`: deletes from the front and verifies the item start/physical offset moves forward.
- `test_front_delete_prev_item()`: deletes a range spanning two adjacent on-disk stripe items and verifies the first is truncated, the second is shifted, and the removed middle is absent.
- `test_punch_hole()`: deletes a middle range from a single extent and verifies two remaining fragments.
- `test_punch_hole_3extents()`: deletes a range spanning three extents, checking dropped middle extent plus trimmed bookends.
- `test_delete_two_extents()`: removes two whole extents while preserving the third.

## Dependencies and Interactions

- Calls production RAID stripe tree APIs: `btrfs_insert_one_raid_extent()`, `btrfs_delete_raid_extent()`, and `btrfs_get_raid_extent_offset()`.
- Uses `alloc_btrfs_io_context()` and `btrfs_io_stripe` to model logical-to-physical stripe layout.
- Assumes two-device RAID1 through `RST_TEST_RAID1_TYPE`.

## Error Handling Notes

- Expected absent ranges return `-ENODATA`; any successful lookup in a hole is treated as test failure.
- Each test cleans up inserted stripe extents where possible and releases the `bioc`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/raid-stripe-tree-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/zoned-tests.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/zoned-tests.c

## Role

Self-tests for zoned-mode block-group allocation offset recovery across RAID profiles. The tests drive `btrfs_load_block_group_by_raid_type()` with synthetic zone write pointers, conventional zones, missing devices, degraded mode, and `last_alloc`.

## Main Entry Point

- `btrfs_test_zoned()`: allocates dummy `fs_info`, then runs every vector in `load_zone_info_tests`.

## Test Model

- `struct load_zone_info_test_vector`: describes RAID type, stripe count, per-stripe allocation offsets, last allocation, block group length, degraded flag, expected return, and expected recovered `alloc_offset`.
- `struct zone_info`: test-local physical/capacity/alloc-offset shape passed to production zoned loading code.
- Sentinel offsets:
  - `WP_MISSING_DEV`: missing stripe/device.
  - `WP_CONVENTIONAL`: conventional zone, where write pointer is not the same signal as sequential zones.
  - `ZONE_SIZE`: fixed 256 MiB synthetic zone capacity.

## Covered Profiles

- SINGLE: basic sequential write pointer recovery.
- DUP and RAID1: matching mirrors, sequential plus conventional zones, larger/smaller `last_alloc`, mismatched write pointers, missing devices, and degraded RAID1 recovery.
- RAID0: stripe-progress reconstruction, disordered stripes, far-distance errors, too many partial writes, missing device errors, and mixed sequential/conventional stripe cases.
- RAID10: mirror-pair equivalents of RAID0 cases, including sub-stripe setup and degraded/missing-device rejection for RAID0-level loss.

## Dependencies and Interactions

- Allocates dummy block groups with `btrfs_alloc_dummy_block_group()`.
- Allocates `btrfs_chunk_map` with the tested RAID profile and stripe count.
- Sets or clears `DEGRADED` mount option per vector.
- Uses cleanup attributes (`__free`, `AUTO_KFREE`) for local allocations.

## Error Handling Notes

- Some test vectors intentionally expect `-EIO`; the entry-point message notes error messages are expected.
- The test validates both return code and, for success, the recovered `bg->alloc_offset`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tests/zoned-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/transaction.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/transaction.c

## Role

Core Btrfs transaction lifecycle implementation. This file manages transaction creation/joining, metadata/qgroup reservations, root recording, delayed refs/items, commit sequencing, pending snapshots, superblock updates, transaction abort cleanup, and wait/wakeup coordination.

## Transaction State Machine

The file documents and implements transitions through:

- `TRANS_STATE_RUNNING`
- `TRANS_STATE_COMMIT_PREP`
- `TRANS_STATE_COMMIT_START`
- `TRANS_STATE_COMMIT_DOING`
- `TRANS_STATE_UNBLOCKED`
- `TRANS_STATE_SUPER_COMMITTED`
- `TRANS_STATE_COMPLETED`

`btrfs_blocked_trans_types[]` defines which start/join modes are blocked at each state.

## Start and Join Path

- `join_transaction()`: attaches to an existing running transaction or allocates a new `btrfs_transaction`. It initializes delayed refs, dirty page trees, pinned extents, pending snapshot/device/block-group lists, counters, wait queues, transid/generation, and tree-mod-log boundaries.
- `start_transaction()`: high-level transaction handle setup. It reserves qgroup metadata, transaction metadata, delayed-ref metadata, optional relocation-root space, handles freezer write refs, waits for blocked commits, joins/creates the transaction, initializes the handle, optionally triggers chunk allocation, records the root, and converts qgroup reservation from prealloc to per-transaction.
- Public wrappers include `btrfs_start_transaction()`, fallback-global-reserve start, join, spacecache join, nostart join, attach, and attach-barrier variants.

## Root Recording

- `record_root_in_trans()`: tags shareable roots in `fs_roots_radix` with `BTRFS_ROOT_TRANS_TAG`, updates `last_trans`, and initializes relocation roots under setup barriers.
- `btrfs_record_root_in_trans()`: public wrapper using `reloc_mutex` to serialize first setup.
- `btrfs_add_dropped_root()`: moves roots to transaction dropped list and clears their transaction radix tag.

## Ending and Waiting

- `btrfs_end_transaction()` / `btrfs_end_transaction_throttle()`: release metadata reservations, create pending block groups, release chunk metadata, drop freezer refs, uninhibit extent-buffer writeback, decrement writer counters, wake commit waiters, and free the handle.
- `btrfs_wait_for_commit()`: waits for a specific transid or latest committing transaction.
- `wait_for_commit()`: waits for at least `SUPER_COMMITTED` or `COMPLETED`, with ordering across earlier transactions.
- `btrfs_should_end_transaction()` and `btrfs_throttle()` expose pressure/blocked-commit checks to callers.

## Commit Writeout

- `btrfs_write_marked_extents()`: starts writeback for dirty btree ranges and marks ranges needing wait.
- `__btrfs_wait_marked_extents()` / `btrfs_wait_extents()`: wait for btree writeback and convert fs error flags to `-EIO`.
- `btrfs_write_and_wait_transaction()`: writes and waits for transaction dirty btree pages, then releases the dirty-pages io tree.
- `btrfs_wait_tree_log_extents()`: log-tree equivalent with log error flags.

## Root Commit Work

- `commit_fs_roots()`: processes radix-tagged fs roots, frees log trees, updates relocation roots, clears forced COW, switches dirty roots, and updates root items in the tree root.
- `commit_cowonly_roots()`: updates chunk/tree/cow-only roots, runs device stats, dev-replace, qgroups, space cache, delayed refs, and dirty block group writeout until stable.
- `switch_commit_roots()`: swaps each dirty root’s `commit_root` to current root node, cleans qgroup swapped blocks, and drops freed roots.

## Snapshot Commit Path

- `create_pending_snapshot()`: creates scheduled snapshots during commit. It handles fscrypt name setup, new objectid allocation, qgroup skip setup, relocation pre/post hooks, parent dir index checks, qgroup creation, delayed items, root copy, root item/guid/timestamp setup, root refs, new fs root lookup, qgroup inheritance/accounting, dir item insertion, parent inode update, and UUID tree updates.
- `qgroup_account_snapshot()`: special full-qgroup path that records source/parent roots, flushes delayed refs, commits fs roots, accounts extents, inherits qgroups, performs a simplified cow-only commit/writeout, switches commit roots, and forces parent root recording.
- `create_pending_snapshots()`: drains the transaction pending snapshot list.

## Main Commit Sequence

`btrfs_commit_transaction()`:

1. Releases handle metadata reservation and runs an initial delayed-ref flush.
2. Creates pending block groups and starts dirty block group writeout once.
3. Moves transaction to `COMMIT_PREP`/`COMMIT_START`, waits for earlier commits if needed.
4. Starts optional delalloc flush, runs delayed items, waits for external writers, ordered extents, and all other transaction writers.
5. Pauses scrub, moves to `COMMIT_DOING`, adds pending snapshot, and enters the critical commit section.
6. Creates snapshots, flushes delayed items and refs, commits fs roots, frees log root tree, accounts qgroups, commits cow-only roots, switches commit roots, updates super roots and device sizes.
7. Sets transaction `UNBLOCKED`, clears `running_transaction`, wakes new transaction starters, writes btree blocks, writes supers, marks `SUPER_COMMITTED`.
8. Finishes extent commit, clears free-space fullness if needed, records last committed transid, marks `COMPLETED`, removes transaction from list, releases references, resumes scrub, and frees the handle.

## Abort and Cleanup

- `cleanup_transaction()`: aborts, waits for writers, removes the transaction from lists, runs transaction cleanup, clears `running_transaction`, drops freezer refs, cancels scrub unless relocation is running, uninhibits writeback, and frees the handle.
- `btrfs_cleanup_pending_block_groups()`: releases delayed-ref reservations for new block groups on abort.
- `__btrfs_abort_transaction()`: records abort on handle and transaction, optionally dumps ENOSPC space info, wakes waiters, and marks filesystem error state.
- `btrfs_clean_one_deleted_snapshot()`: cleaner helper for dead snapshot roots.

## Concurrency and Locking

- `fs_info->trans_lock` protects `running_transaction`, transaction list membership, state changes, and transaction waits.
- Atomic writer/extwriter counters gate commit progression.
- `reloc_mutex` prevents relocation racing with root/snapshot commit work.
- `tree_log_mutex` prevents log tree superblock commits from racing the main superblock commit.
- `commit_root_sem` protects commit-root switching.
- Scrub is paused across the critical commit region.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/transaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/transaction.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/transaction.h

## Role

Public transaction interface and core transaction data structures for Btrfs.

## Key Types

- `enum btrfs_trans_state`: transaction lifecycle states from running through completed.
- `struct btrfs_transaction`: filesystem-wide transaction object containing transid, writer counters, state/abort status, dirty page tree, pending snapshots, device updates, dirty/io/deleted block groups, dropped roots, delayed refs, pinned extents, and wait queues.
- `struct btrfs_trans_handle`: per-task handle containing reservations, delayed-ref accounting, current block reserve, pending snapshot pointer, handle type, abort status, qgroup/checksum/chunk flags, fsync marker, new block groups, delayed-ref reserve, and inhibited writeback xarray.
- `struct btrfs_pending_snapshot`: queued snapshot creation request with dentry, parent inode, source root, new root item, qgroup inheritance, path, block reserve, anon dev, readonly flag, and result error.

## Transaction Modes

Internal bits distinguish freezable starts, attach, join, join-nolock, dummy, and join-nostart. Public mode macros include:

- `TRANS_START`
- `TRANS_ATTACH`
- `TRANS_JOIN`
- `TRANS_JOIN_NOLOCK`
- `TRANS_JOIN_NOSTART`
- `TRANS_EXTWRITERS`

## Inline Helpers

- `btrfs_set_inode_last_trans()`: updates inode transaction/log tracking.
- `btrfs_set_skip_qgroup()` / `btrfs_clear_skip_qgroup()`: set delayed-ref qgroup skip id for snapshot accounting.
- `btrfs_abort_should_print_stack()`: suppresses stack traces for common external/error conditions.
- `btrfs_abort_transaction()`: macro that records first abort, logs/warns, and calls `__btrfs_abort_transaction()` with callsite.

## Exported API

Declares transaction start/join/attach/end/commit functions, async/current commit helpers, commit wait, throttling, root recording, dirty extent write/wait helpers, transaction blocked checks, dropped/dead root handling, chunk metadata release, abort implementation, and slab-cache init/exit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/transaction.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-checker.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-checker.c

## Role

Btrfs metadata validation layer for tree blocks. It validates leaves, nodes, chunks, item layouts, item contents, owner/parent expectations, and key-level relationships when tree blocks are read or otherwise checked.

## Diagnostics

- `generic_err()`, `file_extent_err()`, `dir_item_err()`, `block_group_err()`, `chunk_err()`, `dev_item_err()`, and `extent_err()` produce structured corruption messages and page dumps.
- Errors generally return `-EUCLEAN` through wrappers or `BTRFS_TREE_BLOCK_*` status codes internally.

## Leaf Item Validators

- File extents: `check_extent_data_item()` validates offset alignment, previous inode key continuity, item size/type, compression/encryption fields, inline extent rules, regular/prealloc alignment, overflow, and overlap with previous file extent.
- Checksums: `check_csum_item()` validates objectid, offset alignment, item size alignment, and overlap with previous csum range.
- Directory/xattr items: `check_dir_item()` validates previous inode continuity, embedded location keys, file type, xattr/data length constraints, boundary safety, and name-hash match.
- Inode refs/extrefs: `check_inode_ref()` and `check_inode_extref()` validate packed variable-length name records do not overflow item bounds.
- Inode items: `check_inode_item()` validates key, item size, generation/transid bounds, mode bits/type, directory nlink, and inode flags/ro-compat flags.
- Root items: `check_root_item()` validates key, legacy/current item size, generation fields, bytenr alignment, level/drop level, interrupted-drop checkpoint sanity, and root flags.
- Block groups: `check_block_group_item()` validates item size by feature, chunk objectid/global root id, used bytes, profile/type flags, remap/remapped feature gating, remap bytes, and identity remap count.
- Chunks: `check_leaf_chunk_item()` validates chunk item size then delegates to `btrfs_check_chunk_valid()`.
- Devices: `check_dev_item()` validates dev item objectid, size, devid match, and bytes used <= total.
- Device extents: `check_dev_extent_item()` validates chunk tree/objectid, alignment, length, and overlap with previous extent.
- Extent items/backrefs: `check_extent_item()`, `check_simple_keyed_refs()`, and `check_extent_data_ref()` validate extent alignment, skinny metadata gating, tree/data flag consistency, generation, tree block info, inline ref bounds/order/counts, keyed ref sizes, data-ref root/objectid/offset/count, and extent overlap.
- RAID stripe extents: `check_raid_stripe_extent()` validates alignment and `RAID_STRIPE_TREE` incompat feature.
- Remap keys: `check_remap_key()` validates `REMAP_TREE` feature, item size by key type, nonzero aligned length, aligned objectid, and overflow.
- Free-space tree items: `check_free_space_info()`, `check_free_space_extent()`, and `check_free_space_bitmap()` validate alignment, item size, flags, extent count, zero-sized extent item, and bitmap byte count.

## Chunk Validation

`btrfs_check_chunk_valid()` is shared by leaf chunk items and superblock sys chunk array checks. It validates:

- nonzero stripes except remapped chunks;
- stripe count versus copies/parity/profile;
- logical/length/sector-size alignment;
- stripe length equal to `BTRFS_STRIPE_LEN`;
- overflow and artificial maximum chunk size;
- recognized block group flags;
- exactly one profile bit where applicable;
- type flag presence and system/data/metadata exclusivity;
- mixed-group gating;
- remap feature gating;
- profile-specific stripe/sub-stripe counts.

## Leaf and Node Checks

- `__btrfs_check_leaf()`: validates level zero, `WRITTEN` flag, empty-leaf rules by owner/tree/features, strict key ordering, packed item offsets with no holes/overlap, item data inside leaf bounds, item pointer not overlapping item array, then dispatches to item-specific validators.
- `btrfs_check_leaf()`: converts non-clean status to `-EUCLEAN` and allows error injection.
- `__btrfs_check_node()`: validates `WRITTEN`, level range, item count, child block pointer nonzero/aligned, and node key ordering.
- `btrfs_check_node()`: wrapper returning `-EUCLEAN` and allowing error injection.

## Parent/Owner Checks

- `btrfs_check_eb_owner()`: verifies extent-buffer owner against expected root, with exceptions for testing, unknown owner checks, log trees, relocation trees, and subvolume-owner equivalence.
- `btrfs_verify_level_key()`: verifies expected level and optional first key from parent context, skipping first-key checks for live blocks newer than the last committed transaction.

## Important Constraints

- Validators intentionally rely only on item-local data and immediate previous key/item where possible.
- Some checks are feature-gated to avoid rejecting valid older or feature-specific filesystems.
- Empty extent trees are allowed with `EXTENT_TREE_V2`; several other core trees must not be empty.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-checker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-checker.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-checker.h

## Role

Header for Btrfs tree block validation.

## Key Types

- `struct btrfs_tree_parent_check`: caller-provided expectations for tree-block verification:
  - `owner_root`: expected owner root, zero to skip.
  - `transid`: expected transaction id, zero only for limited contexts such as backref walking.
  - `first_key` plus `has_first_key`: expected first key from parent.
  - `level`: expected tree level.
- `enum btrfs_tree_block_status`: internal detailed validation results, including invalid item count, parent key, key order, level, free space, offsets, block pointer, item, owner, and missing `WRITTEN` flag.

## Constants

- `BTRFS_BLOCK_GROUP_VALID`: accepted block-group type/profile/remap flag mask for chunk validation.

## Exported API

- `__btrfs_check_leaf()` and `__btrfs_check_node()`: detailed status-code validators, exported for btrfs-progs compatibility.
- `btrfs_check_leaf()` and `btrfs_check_node()`: kernel errno wrappers.
- `btrfs_check_chunk_valid()`: common chunk validator for leaf chunk items and superblock system chunk array.
- `btrfs_check_eb_owner()`: owner-root validator.
- `btrfs_verify_level_key()`: parent-level and first-key verification helper.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/tree-checker.h -->