# Group Research: group_716_linux_sources_os_linux_linux_fs_btrfs_tests_qgroup_tests_c_sources_o_55047160eede

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/qgroup-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/qgroup-tests.c

## Purpose

This file implements Btrfs selftests for qgroup accounting using dummy filesystem/root objects and synthetic extent-tree backreferences. It verifies that `btrfs_qgroup_account_extent()` updates referenced and exclusive byte counters correctly when a tree block becomes owned, shared between roots, and unshared/removed.

## Main Entry Point

- `btrfs_test_qgroups(u32 sectorsize, u32 nodesize)`: creates a dummy `fs_info`, an extent/quota/tree root, and two dummy fs roots, enables `BTRFS_FS_QUOTA_ENABLED`, then runs:
  - `test_no_shared_qgroup()`
  - `test_multiple_refs()`

## Helper Functions

- `insert_normal_tree_ref()`: inserts a synthetic `BTRFS_EXTENT_ITEM_KEY` containing one inline tree block reference. It writes the extent item, tree block info, and inline ref directly into the leaf.
- `add_tree_ref()`: increments the extent refcount and inserts a keyed backref item for either `BTRFS_SHARED_BLOCK_REF_KEY` or `BTRFS_TREE_BLOCK_REF_KEY`.
- `remove_extent_item()`: removes the whole extent item from the dummy extent tree.
- `remove_extent_ref()`: decrements the extent refcount and deletes the matching keyed backref item.

All helpers use `btrfs_init_dummy_trans()` and real B-tree search/insert/delete helpers, so the test exercises actual metadata manipulation paths in a minimal harness.

## Test Scenarios

`test_no_shared_qgroup()`:
- Creates a qgroup for `BTRFS_FS_TREE_OBJECTID`.
- Captures old roots for `nodesize` with `btrfs_find_all_roots()`.
- Inserts a single tree block ref owned by the filesystem tree.
- Captures new roots and calls `btrfs_qgroup_account_extent()`.
- Verifies referenced/exclusive counts become `nodesize/nodesize`.
- Removes the extent item, accounts again, and verifies counts return to zero.

`test_multiple_refs()`:
- Creates a qgroup for `BTRFS_FIRST_FREE_OBJECTID`.
- Inserts one tree ref for `BTRFS_FS_TREE_OBJECTID` and verifies it is exclusive.
- Adds a second ref for `BTRFS_FIRST_FREE_OBJECTID`.
- Verifies both roots have referenced bytes but zero exclusive bytes.
- Removes the second ref.
- Verifies the first root returns to exclusive ownership while the second root returns to zero.

## Key Dependencies

- Backref walking: `btrfs_find_all_roots()`.
- Qgroup APIs: `btrfs_create_qgroup()`, `btrfs_qgroup_account_extent()`, `btrfs_verify_qgroup_counts()`.
- Extent item accessors and inline ref layout.
- Dummy fs/root/transaction selftest helpers.
- Global root insertion and dummy fs-root lookup behavior.

## Important Invariants

- The tested bytenr is `nodesize`, not zero, because backref walking paths do not tolerate bytenr zero.
- The dummy extent root is also assigned as `tree_root` and `quota_root`.
- Dummy fs roots are inserted so backref walking can resolve root ownership.
- `btrfs_qgroup_account_extent()` frees the old/new root ulists it receives; the test resets local pointers after successful calls.
- Qgroup accounting is called directly because the dummy transaction does not have production delayed-ref machinery.

## Error Handling

Failures are reported with `test_err()` or `test_std_err()`. Allocation failures return `-ENOMEM`; accounting mismatches and unexpected lookup/deletion behavior generally return `-EINVAL`.

## Research Notes

This is a narrow qgroup regression test. It is valuable because it drives the qgroup root-difference accounting with synthetic but structurally real extent-tree backreferences, covering both exclusive and shared ownership transitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/qgroup-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/raid-stripe-tree-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/raid-stripe-tree-tests.c

## Purpose

This file implements Btrfs selftests for RAID stripe tree operations. It builds dummy filesystems with a `stripe_root`, synthetic devices, and dummy transactions, then verifies create, lookup, update, and delete behavior for RAID stripe extents.

The tests focus on edge cases in `btrfs_insert_one_raid_extent()`, `btrfs_get_raid_extent_offset()`, and `btrfs_delete_raid_extent()`.

## Main Entry Point

- `btrfs_test_raid_stripe_tree(u32 sectorsize, u32 nodesize)`: runs each test in the `tests[]` table through `run_test()`.

## Harness

`run_test()`:
- Allocates dummy `fs_info`.
- Allocates a dummy root and marks it as `BTRFS_RAID_STRIPE_TREE_OBJECTID`.
- Enables `BTRFS_FEATURE_INCOMPAT_RAID_STRIPE_TREE`.
- Sets `fs_info->stripe_root` and `tree_root`.
- Allocates an empty leaf extent buffer.
- Allocates two dummy devices with devids `0` and `1`.
- Initializes a dummy transaction and invokes the specific test.

`btrfs_device_by_devid()` searches the dummy device list.

The fixed profile is a two-device RAID1 data mapping:
`BTRFS_BLOCK_GROUP_DATA | BTRFS_BLOCK_GROUP_RAID1`.

## Test Scenarios

- `test_simple_create_delete()`: inserts one 64 KiB RAID1 stripe extent at logical 1 MiB, verifies lookup on device 0, then deletes it.
- `test_create_update_delete()`: inserts the same logical range twice with shifted physical addresses, verifying that reinsert updates the existing stripe item.
- `test_tail_delete()`: deletes the final 16 KiB of a 64 KiB extent and verifies a 48 KiB front segment remains.
- `test_front_delete()`: deletes the first 16 KiB of a 64 KiB extent and verifies the remaining item starts at logical/physical `1 MiB + 16 KiB`.
- `test_front_delete_prev_item()`: inserts two adjacent 1 MiB extents, deletes a range spanning the tail of the first and head of the second, and verifies truncation plus a hole.
- `test_punch_hole()`: deletes a 64 KiB middle range from one 1 MiB extent and verifies two surviving extents around the hole.
- `test_punch_hole_3extents()`: inserts three adjacent 1 MiB extents and deletes a 2 MiB middle range, validating first-item truncation, middle deletion, and third-item front truncation.
- `test_delete_two_extents()`: inserts three adjacent 1 MiB extents, deletes the first two, verifies lookups fail for the deleted ranges, and verifies the third remains intact.

## Key Dependencies

- RAID stripe tree API from `raid-stripe-tree.h`.
- IO context allocation and stripe mapping structures from Btrfs volume code.
- Dummy fs/root/device helpers from the Btrfs selftest framework.
- Real B-tree insert/delete/search behavior through `stripe_root`.

## Important Invariants

- Each inserted `bioc` has `map_type`, `size`, `logical`, and per-stripe device/physical addresses initialized.
- Device 0 is commonly used for lookup verification through `io_stripe.dev`.
- Surviving mappings are checked for both physical offset and returned length.
- Deleted/hole ranges are expected to return `-ENODATA`.
- Tests clean up inserted extents where possible so each scenario remains isolated in its fresh dummy fs.

## Error Handling

Tests return:
- `-ENOMEM` for allocation failures.
- `-EINVAL` for unexpected physical addresses, lengths, or lookup outcomes.
- The underlying Btrfs API error for insert/delete/lookup failures.

## Research Notes

The file is intentionally repetitive. The duplicated setup makes each logical/physical range expectation explicit, which is useful for validating stripe tree split/truncate/delete behavior without hiding details behind test helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/raid-stripe-tree-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/zoned-tests.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tests/zoned-tests.c

## Purpose

This file implements Btrfs zoned-mode selftests for loading a block group allocation offset from per-zone write pointer state. It validates `btrfs_load_block_group_by_raid_type()` across SINGLE, DUP, RAID1, RAID0, and RAID10 layouts.

## Main Entry Point

- `btrfs_test_zoned(void)`: allocates dummy `fs_info`, iterates `load_zone_info_tests[]`, and runs `test_load_zone_info()` for each vector.

## Test Data Model

`struct load_zone_info_test_vector` defines:
- `raid_type`: Btrfs block group profile.
- `num_stripes`: number of stripes in the synthetic chunk map.
- `alloc_offsets[8]`: per-stripe write pointer or sentinel.
- `last_alloc`: prior allocation offset used when conventional zones are involved.
- `bg_length`: dummy block group length.
- `degraded`: whether mount option `DEGRADED` is set.
- `expected_result`: expected return value.
- `expected_alloc_offset`: expected `bg->alloc_offset` on success.
- `description`: test label.

Special sentinel values:
- `WP_MISSING_DEV`: missing device/stripe.
- `WP_CONVENTIONAL`: conventional zone.
- Numeric values represent sequential-zone write pointer offsets.

`struct zone_info` is the minimal shape needed by the target zoned code: physical, capacity, and allocation offset.

## Harness Behavior

`test_load_zone_info()`:
- Allocates a dummy block group and chunk map.
- Allocates zone info and an active-zone bitmap.
- Sets `map->type`, `map->num_stripes`, and RAID10 `sub_stripes`.
- Fills each synthetic zone with capacity `ZONE_SIZE`.
- Marks a zone active if its allocation offset is nonzero and inside the zone.
- Toggles `DEGRADED` mount option from the vector.
- Calls `btrfs_load_block_group_by_raid_type()`.
- Verifies both return code and successful `bg->alloc_offset`.

## Covered Cases

SINGLE:
- Sequential zone write pointer loading.

DUP and RAID1:
- Matching write pointers.
- Sequential plus conventional zone with matching `last_alloc`.
- Sequential plus conventional zone with smaller `last_alloc`.
- Different write pointers as `-EIO`.
- Missing-device cases, including degraded RAID1 recovery.
- Sequential/conventional combinations with too-large `last_alloc` as `-EIO`.

RAID0:
- Initial partial write.
- Progression into later stripes.
- One stripe advanced.
- Disordered stripe progression.
- Excessive distance between stripes.
- Too many partial writes.
- Missing device under degraded mount rejected.
- Sequential/conventional reconstruction from `last_alloc`.
- Four-stripe mixed conventional cases with success and failure expectations.

RAID10:
- RAID0-like progression across mirrored stripe pairs.
- Mirrored pair consistency.
- Conventional-zone combinations.
- Disordered, far-distance, too-many-partial, and missing mirror-group failures.
- Eight-stripe mixed conventional reconstruction cases.

## Key Dependencies

- Dummy fs/block group helpers.
- Chunk map allocation/freeing from `volumes.h`.
- Zoned allocator logic from `zoned.h`.
- Linux cleanup attributes and bitmap helpers.

## Important Invariants

- RAID10 test vectors set `map->sub_stripes = 2`.
- Active-zone state is derived from nonzero write pointers below `ZONE_SIZE`.
- Missing devices and conventional zones are represented as high sentinel `u64` values.
- Expected failures are part of normal test coverage; the entry point logs that error messages are expected.

## Research Notes

The test is vector-driven and compact. One notable implementation detail: after `bitmap_zalloc()`, the failure check tests `zone_info` again instead of `active`; if bitmap allocation failed, the current code would not catch it at that branch.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tests/zoned-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/transaction.c -->
# File Research: sources/os/linux/linux/fs/btrfs/transaction.c

## Purpose

This file implements the Btrfs transaction lifecycle: starting and joining transactions, metadata reservation, root transaction tracking, transaction end, commit orchestration, snapshot creation, qgroup snapshot handling, metadata writeback, superblock persistence, abort cleanup, deleted snapshot cleanup, and transaction handle cache management.

It is one of Btrfs’ central consistency coordination files.

## Transaction State Model

The file documents and implements these states:

- `TRANS_STATE_RUNNING`: normal metadata modifications are allowed.
- `TRANS_STATE_COMMIT_PREP`: a committer has begun preparation.
- `TRANS_STATE_COMMIT_START`: new external starts/attaches are blocked; limited joins may still happen.
- `TRANS_STATE_COMMIT_DOING`: all normal joining is blocked; supporting trees are updated.
- `TRANS_STATE_UNBLOCKED`: tree updates are complete; a new transaction may start while the old one writes out.
- `TRANS_STATE_SUPER_COMMITTED`: superblocks have been written.
- `TRANS_STATE_COMPLETED`: extent commit cleanup is done and the transaction is removed.

`btrfs_blocked_trans_types[]` maps each state to the transaction handle types blocked in that state.

## Public APIs

Transaction lifecycle:
- `btrfs_start_transaction()`
- `btrfs_start_transaction_fallback_global_rsv()`
- `btrfs_join_transaction()`
- `btrfs_join_transaction_spacecache()`
- `btrfs_join_transaction_nostart()`
- `btrfs_attach_transaction()`
- `btrfs_attach_transaction_barrier()`
- `btrfs_end_transaction()`
- `btrfs_end_transaction_throttle()`
- `btrfs_commit_transaction()`
- `btrfs_commit_transaction_async()`
- `btrfs_commit_current_transaction()`
- `btrfs_wait_for_commit()`

Root and cleanup helpers:
- `btrfs_record_root_in_trans()`
- `btrfs_add_dropped_root()`
- `btrfs_add_dead_root()`
- `btrfs_maybe_wake_unfinished_drop()`
- `btrfs_clean_one_deleted_snapshot()`

Writeback and state helpers:
- `btrfs_write_marked_extents()`
- `btrfs_wait_tree_log_extents()`
- `btrfs_transaction_blocked()`
- `btrfs_throttle()`
- `btrfs_should_end_transaction()`
- `btrfs_trans_release_chunk_metadata()`

Abort/cache:
- `__btrfs_abort_transaction()`
- `btrfs_put_transaction()`
- `btrfs_transaction_init()`
- `btrfs_transaction_exit()`

## Starting and Joining Transactions

`join_transaction()`:
- Runs under `fs_info->trans_lock`.
- Rejects work if the filesystem is in error state.
- Joins an existing running transaction if the current state permits the requested type.
- Increments transaction refcount, writer count, and external-writer count.
- Allocates and initializes a new `struct btrfs_transaction` when no transaction exists and the type may start one.
- Initializes delayed-ref xarrays, dirty page/pinned extent trees, wait queues, block group lists, dropped roots, generation, transaction list membership, and state.

`start_transaction()`:
- Reserves qgroup metadata before joining.
- Reserves transaction metadata and delayed-ref bytes.
- Optionally reserves relocation-root space.
- Refills delayed-ref reserve for zero-item throttling starts.
- Allocates a transaction handle from `btrfs_trans_handle_cachep`.
- Handles freeze protection with `sb_start_intwrite()`.
- Waits for blocked transactions when the type permits waiting.
- Joins or starts the transaction.
- Initializes handle fields, local delayed-ref reserve, and writeback inhibition tracking.
- Performs forced chunk allocation when metadata space requires it.
- Records the root in the transaction after `current->journal_info` is initialized.
- Converts qgroup metadata reservation from prealloc to per-transaction.

## Root Tracking

`record_root_in_trans()` and `btrfs_record_root_in_trans()`:
- Track shareable roots modified in a transaction by tagging `fs_roots_radix` with `BTRFS_ROOT_TRANS_TAG`.
- Update `root->last_trans`.
- Initialize relocation roots when needed.
- Use `BTRFS_ROOT_IN_TRANS_SETUP` plus memory barriers so concurrent users can distinguish in-progress setup from completed recording.

`btrfs_add_dropped_root()`:
- Adds a dropped root to the transaction’s `dropped_roots`.
- Clears the root’s radix transaction tag so commit does not update it.

`switch_commit_roots()`:
- Under `commit_root_sem`, replaces each root’s `commit_root` with the current root node.
- Releases dirty log pages and qgroup swapped-block state.
- Frees roots queued in `dropped_roots`.

## Ending Transactions

`__btrfs_end_transaction()`:
- Handles nested transaction handle references through `use_count`.
- Releases metadata reservations.
- Creates pending block groups.
- Releases chunk metadata reservations.
- Ends freeze write protection for freezable transaction types.
- Uninhibits extent buffer writeback before decrementing writer counters.
- Decrements writer and external-writer counters.
- Wakes commit waiters.
- Releases lockdep maps and transaction references.
- Clears `current->journal_info`.
- Optionally runs delayed iputs.
- Returns abort or read-only errors when applicable.

## Commit Flow

`btrfs_commit_transaction()` is the main transaction commit state machine.

High-level sequence:
1. Stop early if the transaction is already aborted.
2. Release handle metadata reservation.
3. Run an initial delayed-ref flush once per transaction.
4. Create pending block groups.
5. Start dirty block group IO once per transaction.
6. If another committer is active, enqueue pending snapshot, end this handle, and wait.
7. Become the committer by entering `TRANS_STATE_COMMIT_PREP`.
8. Wait for previous transaction completion when required.
9. Enter `TRANS_STATE_COMMIT_START`.
10. Start delalloc flush if `FLUSHONCOMMIT`.
11. Run delayed items.
12. Wait for external writers to drain.
13. Run delayed items again and wait for delalloc.
14. Wait for fast-fsync pending ordered extents.
15. Pause scrub.
16. Enter `TRANS_STATE_COMMIT_DOING`.
17. Wait for all writers to drain.
18. Lock relocation mutex.
19. Create pending snapshots.
20. Run delayed items and delayed refs.
21. Assert delayed root emptiness.
22. Commit filesystem roots and free log root tree.
23. Account qgroup extents.
24. Commit cow-only roots.
25. Add tree and chunk roots to the commit-root switch list.
26. Switch commit roots.
27. Update superblock root pointers and prepare `super_for_commit`.
28. Commit device sizes and clear log error flags.
29. Release chunk metadata.
30. Lock tree log mutex, unblock the transaction, and clear `running_transaction`.
31. Wake waiters and optionally wake cleaner for feature changes.
32. Uninhibit extent buffer writeback.
33. Write and wait dirty transaction extents.
34. Write all superblocks.
35. Mark `TRANS_STATE_SUPER_COMMITTED`.
36. Finish extent commit.
37. Clear full-space flags if needed.
38. Update last committed transaction id.
39. Mark `TRANS_STATE_COMPLETED`.
40. Remove transaction from list, release references, resume scrub, clear journal info, and free the handle.

## Cow-Only and FS Root Commit

`commit_fs_roots()`:
- Iterates radix-tagged roots.
- Clears transaction tags.
- Frees per-transaction qgroup metadata.
- Frees log trees.
- Updates relocation roots.
- Clears `BTRFS_ROOT_FORCE_COW`.
- Updates root item pointers in the tree root.
- Queues roots whose commit root must be switched.

`commit_cowonly_roots()`:
- COWs the tree root node.
- Runs device stats, device replace, qgroups, and space-cache setup.
- Updates all dirty cow-only roots.
- Repeatedly runs delayed refs and writes dirty block groups until stable.
- Updates the committed dev-replace cursor.

`update_cowonly_root()` loops until the root item bytenr/used fields stabilize after updating the root pointer.

## Snapshot Creation

Pending snapshots are created only during transaction commit.

`create_pending_snapshot()`:
- Sets up encrypted filename handling in a NOFS allocation context.
- Allocates a new root objectid.
- Sets qgroup skip id for the new snapshot.
- Runs relocation pre-snapshot hooks and reserves extra metadata if needed.
- Switches transaction block reserve to the pending snapshot reservation.
- Records the parent and source roots in the transaction.
- Allocates a directory index and checks for name conflicts.
- Creates the new qgroup.
- Runs delayed items before root copying.
- Copies the source root item and root block.
- Sets snapshot flags, UUIDs, parent UUID, received UUID handling, and timestamps.
- Inserts the new root item and root refs.
- Opens the new fs root.
- Runs relocation post-snapshot hooks.
- Performs qgroup inheritance/accounting.
- Inserts the directory item and updates parent inode.
- Adds UUID tree entries.
- Restores reserves, clears skip qgroup, frees temporary resources, and stores errors in `pending->error`.

`qgroup_account_snapshot()` performs a special mini-commit for full qgroup accounting so snapshot inheritance sees consistent root and extent usage.

## Writeback and Waiting

`btrfs_write_marked_extents()`:
- Converts dirty extent bits to `EXTENT_NEED_WAIT`.
- Starts writeback for btree inode ranges.
- If marking fails with `-ENOMEM`, it still waits for writeback to avoid committing a superblock that points to unwritten metadata.

`__btrfs_wait_marked_extents()`:
- Waits on ranges marked `EXTENT_NEED_WAIT`.
- Clears that state where possible.

`btrfs_wait_extents()` and `btrfs_wait_tree_log_extents()`:
- Convert btree/log writeback error flags into `-EIO`.

`btrfs_write_and_wait_transaction()`:
- Writes and waits all transaction dirty pages and releases the transaction dirty-page io tree.

## Abort and Cleanup

`cleanup_transaction()`:
- Aborts the transaction.
- If still running, transitions to commit-doing and waits for writers.
- Removes the transaction from the transaction list.
- Calls `btrfs_cleanup_one_transaction()`.
- Clears `running_transaction`.
- Releases freeze protection and transaction refs.
- Cancels scrub unless relocation is running.
- Uninhibits writeback and frees the handle.

`btrfs_cleanup_pending_block_groups()`:
- Releases delayed-ref reservations for pending new block groups on abort.

`__btrfs_abort_transaction()`:
- Stores the abort error in both handle and transaction.
- Dumps space info for first `-ENOSPC` abort.
- Wakes transaction waiters.
- Marks the filesystem error state.

## Research Notes

This file is the transaction consistency spine for Btrfs. The most sensitive areas are the transition between `COMMIT_DOING` and `UNBLOCKED`, snapshot creation during commit, qgroup mini-commit behavior, writer/extwriter draining, and the ordering of metadata writeback versus superblock writes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/transaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/transaction.h -->
# File Research: sources/os/linux/linux/fs/btrfs/transaction.h

## Purpose

This header defines Btrfs transaction state, transaction/handle data structures, pending snapshot data, transaction type flags, abort helpers, and public transaction API declarations used by the rest of the filesystem.

## Core Types

`enum btrfs_trans_state`:
- Defines the transaction state machine from `TRANS_STATE_RUNNING` through `TRANS_STATE_COMPLETED`.

`struct btrfs_transaction`:
- Represents one filesystem-wide transaction.
- Tracks transaction id, writer counts, external writer counts, refcount, state, abort status, flags, dirty pages, pending snapshots, device updates, dirty block groups, dropped roots, delayed refs, pinned extents, deleted block groups, and pending ordered extents.
- Provides wait queues for writers, commit waiters, and pending ordered extents.
- Owns lists used during commit: `pending_snapshots`, `dev_update_list`, `switch_commits`, `dirty_bgs`, `io_bgs`, `dropped_roots`, and `deleted_bgs`.

`struct btrfs_trans_handle`:
- Per-task transaction handle.
- Tracks transid, reserved bytes, delayed-ref bytes, chunk metadata reservation, delayed-ref update counters, qgroup/csum deletion state, transaction pointer, block reservations, pending snapshot, type flags, abort status, fs info, new block groups, local delayed-ref reserve, and extent buffers with writeback inhibited by the handle.

`struct btrfs_pending_snapshot`:
- Carries all state needed to create a snapshot during commit.
- Includes dentry, parent dir inode, source root, new root item, resulting snapshot root, qgroup inheritance, path, block reserve, anon device, readonly flag, error, and list linkage.

## Transaction Type Flags

Internal bits include:
- `__TRANS_FREEZABLE`
- `__TRANS_START`
- `__TRANS_ATTACH`
- `__TRANS_JOIN`
- `__TRANS_JOIN_NOLOCK`
- `__TRANS_DUMMY`
- `__TRANS_JOIN_NOSTART`

Public combinations include:
- `TRANS_START`
- `TRANS_ATTACH`
- `TRANS_JOIN`
- `TRANS_JOIN_NOLOCK`
- `TRANS_JOIN_NOSTART`
- `TRANS_EXTWRITERS`

These flags determine whether a handle can start, attach, join, bypass some locking, or count as an external writer.

## Inline Helpers

- `btrfs_set_inode_last_trans()`: records the current transaction and log-subtransaction state on an inode.
- `btrfs_set_skip_qgroup()` / `btrfs_clear_skip_qgroup()`: set and clear a delayed-ref qgroup id to skip during accounting.
- `btrfs_abort_should_print_stack()`: suppresses stack traces for common external/resource errors like `-EIO`, `-EROFS`, and `-ENOMEM`.

## Abort Macro

`btrfs_abort_transaction(trans, error)`:
- Reports the first transaction abort since mount.
- Prints a stack trace only for errors likely to indicate a bug.
- Sets `BTRFS_FS_STATE_TRANS_ABORTED`.
- Delegates to `__btrfs_abort_transaction()` with function and line metadata.

## Public API Declarations

The header declares transaction start/join/attach/end/commit APIs, commit waiting, throttling, root recording, marked extent writeback, tree log extent waiting, transaction state checks, dropped root handling, chunk metadata release, abort implementation, and transaction cache init/exit.

## Important Invariants

- Transaction abort fields are accessed with `READ_ONCE()`/`WRITE_ONCE()` through `TRANS_ABORTED()` because abort status is not protected by a regular lock.
- `num_extwriters` must reach zero before commit can proceed past external-writer draining.
- `num_writers` must reach the commit holder before full commit work proceeds.
- `io_bgs` list consistency is guarded by transaction critical-section ordering rather than its own explicit lock.
- Pending ordered extents started by fast fsync must be waited before commit completes.

## Research Notes

This header is tightly coupled to `transaction.c`. The structs expose the concurrency and commit-ordering contract: writer accounting, state transitions, delayed refs, dirty block groups, snapshots, and abort propagation all meet here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/transaction.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-checker.c -->
# File Research: sources/os/linux/linux/fs/btrfs/tree-checker.c

## Purpose

This file implements Btrfs tree block validation. It checks nodes and leaves read from disk for structural consistency and item-level sanity before normal filesystem code trusts their contents. It is intended to catch fuzzed/corrupt images and internal bugs while avoiding false rejection of valid historical filesystems.

## Diagnostic Helpers

- `generic_err()`: common corrupt leaf/node reporter with root, block, slot, and page dump.
- `file_extent_err()`: file extent reporter including inode and file offset.
- `dir_item_err()`: directory/xattr reporter including inode.
- `block_group_err()`: block group reporter including start and length.
- `chunk_err()`: chunk reporter for either chunk tree leaves or superblock syschunk array.
- `dev_item_err()`, `extent_err()`, and `inode_ref_err()`: specialized diagnostics.

Detected corruption generally returns `-EUCLEAN` through item validators or maps to `-EUCLEAN` in public wrappers.

## File Extent and Csum Validation

`check_extent_data_item()` validates:
- File offset alignment.
- Previous key objectid continuity for inode-related items in subvolume trees.
- Minimum item size and valid file extent type.
- Compression range and zero encryption.
- Inline extent offset and uncompressed inline size.
- Regular/prealloc fixed item size.
- Alignment of ram bytes, disk bytenr, disk bytes, offset, and num bytes.
- Extent-end overflow.
- Overlap with the previous file extent in the same leaf.
- Debug-only ram/disk size mismatch for uncompressed extents.

`file_extent_end()` computes the logical end used for overlap checking.

`check_csum_item()` validates:
- Objectid is `BTRFS_EXTENT_CSUM_OBJECTID`.
- Key offset is sectorsize aligned.
- Item size is checksum-size aligned.
- Adjacent csum item ranges do not overlap.

## Inode, Directory, and Xattr Validation

`check_prev_ino()` detects missing inode-item ordering context for inode-related keys in subvolume trees.

`check_inode_key()` validates inode location keys and requires xattr location keys to be zero.

`check_root_key()` validates root ids, relocation-root rules, and prevents directory-like references to non-fs trees.

`check_dir_item()` iterates packed `struct btrfs_dir_item` entries and validates:
- Header and payload bounds.
- Location key type and value.
- Directory file type.
- Xattr key/type consistency.
- Name/data length limits.
- Non-xattr data length is zero.
- DIR_ITEM/XATTR key hash matches the item name.

`check_inode_item()` validates:
- Item size.
- Inode generation and transid against super generation + 1.
- Mode bit mask and file type.
- Directory nlink <= 1.
- Inode incompat and ro-compat flags, rejecting unknown ro flags on writable mounts.

`check_inode_ref()` and `check_inode_extref()` validate packed inode ref/extref entry boundaries and nonzero name payload shape.

## Root Item Validation

`check_root_item()`:
- Validates key rules through `check_root_key()`.
- Accepts modern and legacy root item sizes.
- Checks generation, generation_v2, and last_snapshot against super generation + 1.
- Checks root bytenr alignment.
- Checks root and drop levels below `BTRFS_MAX_LEVEL`.
- Rejects nonzero `drop_progress.objectid` with `drop_level == 0`.
- Allows only readonly and dead root flags.

## Block Group and Chunk Validation

`check_block_group_item()` validates:
- Nonzero block group length.
- Item size based on whether remap tree is enabled.
- Chunk objectid/global root id rules.
- Used bytes <= block group length.
- At most one profile bit.
- Metadata remap/remapped flags require remap-tree incompat.
- Type is one of allowed data/metadata/system/remap/mixed values.
- V2 remap bytes and identity remap count within block group bounds.

`valid_stripe_count()` encodes profile-specific stripe/sub-stripe constraints.

`btrfs_check_chunk_valid()` validates chunk items and superblock syschunk entries:
- Stripe count, copies, and parity constraints unless remapped.
- Logical address alignment.
- Sector size match.
- Nonzero aligned length and no logical+length overflow.
- Stripe length equals `BTRFS_STRIPE_LEN`.
- Chunk length below the artificial maximum.
- Recognized type/profile flags.
- Exactly one or zero profile bits.
- Required type flag.
- System chunks do not mix with data/metadata.
- Mixed data/metadata chunks require mixed-groups feature.
- Remap flags require remap-tree feature.
- Profile-specific stripe/sub-stripe count validity.

`check_leaf_chunk_item()` adds leaf item size validation before calling the common chunk validator.

## Device and Dev Extent Validation

`check_dev_item()` validates:
- Key objectid is `BTRFS_DEV_ITEMS_OBJECTID`.
- Item size.
- Device id matches key offset.
- Bytes used does not exceed total bytes.

`check_dev_extent_item()` validates:
- Chunk tree id and chunk objectid.
- Key offset, chunk offset, and length alignment.
- No overlap with previous dev extent for the same device.

## Extent and Backref Validation

`check_extent_item()` validates `BTRFS_EXTENT_ITEM_KEY` and `BTRFS_METADATA_ITEM_KEY`:
- Skinny metadata feature requirement.
- Bytenr alignment.
- Metadata key level bounds.
- Minimum extent item size.
- Generation <= super generation + 1.
- Exactly one of DATA or TREE_BLOCK flags.
- Tree extent length/nodesize rules.
- Data extent key type, length alignment, and no full-backref flag.
- Tree block info level for non-skinny tree extents.
- Inline ref bounds, allowed ref types, alignment, objectid/root validity, and nonzero counts.
- Inline ref ordering by type and descending sequence/hash.
- No padding.
- Inline ref count not greater than total refs.
- Previous extent item does not overlap the current one.

`check_simple_keyed_refs()` validates simple keyed backrefs, including item size and alignment.

`check_extent_data_ref()` validates arrays of keyed data refs for item-size alignment, root/objectid/offset validity, and nonzero count.

`is_valid_dref_root()` permits data backrefs from subvolume trees, data reloc tree, and root tree.

## RAID Stripe, Remap, and Free-Space Validation

`check_raid_stripe_extent()`:
- Requires aligned objectid.
- Requires `RAID_STRIPE_TREE` incompat feature.

`check_remap_key()`:
- Requires `REMAP_TREE`.
- Validates item sizes for identity/remap/backref keys.
- Requires nonzero aligned length and aligned objectid.
- Rejects objectid+length overflow.

`check_free_space_info()`:
- Validates aligned block group range key.
- Validates item size and flags.
- Checks extent count does not exceed maximum sectors in the range.

`check_free_space_extent()`:
- Validates aligned key and zero item size.

`check_free_space_bitmap()`:
- Validates aligned key.
- Requires nonzero length.
- Requires exact bitmap item size for the represented range.

## Leaf Validation

`check_leaf_item()` dispatches by key type to item-specific validators.

`__btrfs_check_leaf()` performs whole-leaf checks:
- Header level must be 0.
- `BTRFS_HEADER_FLAG_WRITTEN` must be set.
- Certain roots must not have empty leaves, with exceptions for relocation and extent-tree-v2 empty extent trees.
- Keys must be strictly increasing.
- Item data must be contiguous from the end of the leaf, with no holes or overlaps.
- Item data must stay inside the leaf data area.
- Item data must not overlap item headers.
- Each item must pass item-specific validation.

`btrfs_check_leaf()` maps non-clean status to `-EUCLEAN` and supports error injection.

## Node Validation

`__btrfs_check_node()` validates:
- `BTRFS_HEADER_FLAG_WRITTEN`.
- Level in `[1, BTRFS_MAX_LEVEL - 1]`.
- Nritems in `[1, BTRFS_NODEPTRS_PER_BLOCK]`.
- Nonzero aligned block pointers.
- Strictly increasing node keys.

`btrfs_check_node()` maps non-clean status to `-EUCLEAN` and supports error injection.

## Ownership and Parent Checks

`btrfs_check_eb_owner()`:
- Skips dummy selftest fs, unknown owner `0`, log tree, and reloc tree cases.
- For non-subvolume trees, extent buffer owner must equal root owner.
- For subvolume trees, owner may differ but must still be a valid subvolume tree id.

`btrfs_verify_level_key()`:
- Verifies extent buffer level against expected parent check level.
- Optionally verifies first key.
- Skips first-key verification for live tree blocks newer than the last committed transaction.
- Rejects empty tree blocks when a first-key check is required.
- Compares expected first key to the first node/item key.

## Important Invariants

- Validators must not reject valid historical formats, so legacy root item sizes and selective strictness are supported.
- Item checks rely on item data and local key ordering, not broader tree traversal.
- Feature-gated formats such as skinny metadata, RAID stripe tree, remap tree, mixed groups, and extent-tree-v2 are explicitly checked.
- Empty-tree allowances depend on root type and feature flags.
- `-EUCLEAN` is the standard corruption result.

## Research Notes

`tree-checker.c` is a defensive boundary between raw on-disk metadata and normal Btrfs code. Its highest-risk maintenance area is balancing stricter corruption detection against compatibility with valid existing filesystems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-checker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-checker.h -->
# File Research: sources/os/linux/linux/fs/btrfs/tree-checker.h

## Purpose

This header declares the public Btrfs tree-checker interface and shared validation status types. It is used by tree read/validation paths and by code that needs parent/owner checks for extent buffers.

## Core Types

`struct btrfs_tree_parent_check` describes expected parent-derived metadata for a tree block:
- `owner_root`: expected owner root, or 0 to skip.
- `transid`: expected transaction id, or 0 to skip.
- `first_key`: expected first key.
- `has_first_key`: whether first-key validation should run.
- `level`: expected tree level.

`enum btrfs_tree_block_status` enumerates detailed validation outcomes:
- Clean block.
- Invalid nritems.
- Invalid parent key.
- Bad key order.
- Invalid level.
- Invalid free space.
- Invalid offsets.
- Invalid block pointer.
- Invalid item.
- Invalid owner.
- Missing written flag.

## Constants

`BTRFS_BLOCK_GROUP_VALID` defines the accepted block group/chunk flag mask:
- Type mask.
- Profile mask.
- Remapped flag.

## Declared APIs

- `__btrfs_check_leaf()`: detailed leaf validation returning `enum btrfs_tree_block_status`.
- `__btrfs_check_node()`: detailed node validation returning `enum btrfs_tree_block_status`.
- `btrfs_check_leaf()`: public leaf validator returning 0 or `-EUCLEAN`.
- `btrfs_check_node()`: public node validator returning 0 or `-EUCLEAN`.
- `btrfs_check_chunk_valid()`: common validator for chunk items and superblock syschunk entries.
- `btrfs_check_eb_owner()`: validates extent buffer owner against expected root owner.
- `btrfs_verify_level_key()`: validates extent buffer level and optional first key against parent expectations.

## Important Invariants

- `level` in `btrfs_tree_parent_check` should always be set.
- `transid` and `first_key` checks may be skipped only in limited contexts such as backref walking.
- The detailed status enum is exported because btrfs-progs wants the same status values.
- The header intentionally forward-declares most Btrfs structs to keep dependencies narrow.

## Research Notes

This header is the compact contract for `tree-checker.c`: callers can either request detailed validation status or the simpler kernel-style 0/error wrappers, and parent checks are bundled into a single structure to avoid ambiguous call signatures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/tree-checker.h -->