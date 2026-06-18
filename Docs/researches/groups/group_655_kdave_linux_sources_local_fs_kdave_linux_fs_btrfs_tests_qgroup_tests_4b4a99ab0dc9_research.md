# Group Research: group_655_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_tests_qgroup_tests_4b4a99ab0dc9

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/qgroup-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/qgroup-tests.c

## Purpose

This file implements Btrfs selftests for qgroup accounting behavior using dummy filesystem/root objects and synthetic extent-tree backreferences. It verifies that `btrfs_qgroup_account_extent()` updates referenced and exclusive byte counters correctly when tree block references are added, shared between roots, and removed.

## Main Entry Point

- `btrfs_test_qgroups(u32 sectorsize, u32 nodesize)`: constructs a dummy `fs_info`, dummy extent root, quota root, and two filesystem roots, then runs:
  - `test_no_shared_qgroup()`
  - `test_multiple_refs()`

## Helpers

- `insert_normal_tree_ref()`: inserts a synthetic `BTRFS_EXTENT_ITEM_KEY` with one inline tree block reference. It can create either:
  - `BTRFS_TREE_BLOCK_REF_KEY` when `parent == 0`
  - `BTRFS_SHARED_BLOCK_REF_KEY` when `parent > 0`
- `add_tree_ref()`: increments extent refcount and inserts a separate keyed backref item.
- `remove_extent_item()`: deletes the whole extent item.
- `remove_extent_ref()`: decrements extent refcount and deletes the matching keyed backref.

All helpers use `btrfs_init_dummy_trans()` and explicit B-tree path allocation, so they exercise real B-tree item insertion/search/deletion paths without a mounted filesystem.

## Test Scenarios

`test_no_shared_qgroup()`:
- Creates qgroup for `BTRFS_FS_TREE_OBJECTID`.
- Captures old roots for the target bytenr with `btrfs_find_all_roots()`.
- Inserts a single tree block ref owned by the filesystem tree.
- Captures new roots and accounts the extent.
- Verifies qgroup referenced/exclusive counts become `nodesize/nodesize`.
- Removes the extent item.
- Accounts again and verifies counts return to zero.

`test_multiple_refs()`:
- Creates qgroup for `BTRFS_FIRST_FREE_OBJECTID`.
- Inserts one tree ref for `BTRFS_FS_TREE_OBJECTID` and verifies it is fully exclusive.
- Adds another tree ref for `BTRFS_FIRST_FREE_OBJECTID`.
- Verifies both roots reference the bytes but neither has exclusive bytes.
- Removes the second root’s ref.
- Verifies first root returns to exclusive ownership and second root returns to zero.

## Dependencies and Integration

This selftest depends on Btrfs core internals:
- Extent item format from `ctree.h` and accessors.
- Dummy transaction/root/fs helpers from the Btrfs selftest harness.
- Backref walking through `btrfs_find_all_roots()`.
- Qgroup APIs from `qgroup.h`.
- Global root insertion and dummy fs root lookup behavior.

`btrfs_test_qgroups()` is expected to be called by the Btrfs selftest runner with chosen sector/node sizes.

## Important Invariants

- The dummy extent root doubles as `tree_root` and `quota_root` to satisfy code paths that assume populated `fs_info`.
- `BTRFS_FS_QUOTA_ENABLED` is set before qgroup accounting.
- Dummy roots are inserted into the fs root radix/tree so backref walking can resolve root ownership.
- The tested extent bytenr is `nodesize`, not zero, because backref walking paths do not tolerate bytenr zero.
- `btrfs_qgroup_account_extent()` consumes/frees the old/new root ulists passed to it; the test resets local pointers after calls.

## Error Handling

The file reports failures through `test_err()` / `test_std_err()` and returns negative errno values. Allocation failure returns `-ENOMEM`; logic/accounting mismatch generally returns `-EINVAL`.

## Research Notes

This is a focused qgroup regression test rather than a generic qgroup harness. It directly edits extent-tree items and then invokes the same accounting and backref resolution functions used by production code, making it useful for catching regressions in qgroup root-difference accounting and backref interpretation.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/qgroup-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/raid-stripe-tree-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/raid-stripe-tree-tests.c

## Purpose

This file implements Btrfs selftests for RAID stripe tree operations. It builds dummy filesystems with a `stripe_root`, synthetic devices, and dummy transactions, then verifies insertion, lookup, update, and deletion behavior for RAID stripe extents.

The tests focus on how `btrfs_insert_one_raid_extent()`, `btrfs_get_raid_extent_offset()`, and `btrfs_delete_raid_extent()` handle exact deletes, front/tail truncation, hole punching, item updates, and ranges spanning adjacent stripe tree items.

## Main Entry Point

- `btrfs_test_raid_stripe_tree(u32 sectorsize, u32 nodesize)`: runs every function in the `tests[]` table through `run_test()`.

## Test Harness

- `run_test(test_func_t test, u32 sectorsize, u32 nodesize)`:
  - Allocates dummy `fs_info`.
  - Allocates a dummy root and marks it as `BTRFS_RAID_STRIPE_TREE_OBJECTID`.
  - Enables `BTRFS_FEATURE_INCOMPAT_RAID_STRIPE_TREE`.
  - Sets `fs_info->stripe_root` and `tree_root`.
  - Allocates a leaf extent buffer for the root.
  - Allocates two dummy devices with devids `0` and `1`.
  - Initializes a dummy transaction and runs the supplied test.

- `btrfs_device_by_devid()`: local helper that searches the dummy device list for a requested devid.

## Covered Scenarios

- `test_simple_create_delete()`:
  - Inserts one 64 KiB RAID1 stripe extent at logical 1 MiB.
  - Verifies lookup returns the physical address on device 0 and length 64 KiB.
  - Deletes the extent.

- `test_create_update_delete()`:
  - Inserts a 64 KiB extent.
  - Re-inserts the same logical range with shifted physical addresses.
  - Verifies lookup reflects the updated physical mapping.
  - Deletes the updated extent.
  - Explicitly exercises update behavior inside `btrfs_insert_one_raid_extent()`.

- `test_tail_delete()`:
  - Inserts a 64 KiB extent.
  - Deletes the final 16 KiB.
  - Verifies the remaining front extent is 48 KiB and the deleted tail is absent.

- `test_front_delete()`:
  - Inserts a 64 KiB extent.
  - Deletes the first 16 KiB.
  - Verifies the remaining stripe starts at logical/physical `1 MiB + 16 KiB`, has length 48 KiB, and the deleted front range is absent.

- `test_front_delete_prev_item()`:
  - Inserts two adjacent 1 MiB items.
  - Deletes a 1 MiB range starting halfway through the first item.
  - Verifies the first item is truncated to 512 KiB, the second item’s surviving part starts 512 KiB later, and the hole lookup fails.

- `test_punch_hole()`:
  - Inserts one 1 MiB extent.
  - Deletes a 64 KiB middle range.
  - Verifies two surviving extents around the hole and absence of the hole.

- `test_punch_hole_3extents()`:
  - Inserts three adjacent 1 MiB extents.
  - Deletes a 2 MiB range beginning 256 KiB into the first extent.
  - Verifies first item truncation, second item removal, third item front truncation, and cleanup deletion of survivors.

- `test_delete_two_extents()`:
  - Inserts three adjacent 1 MiB extents.
  - Deletes the first two.
  - Verifies the first two lookups return `-ENODATA`, while the third remains intact.

## Dependencies and Integration

The test uses:
- RAID stripe tree API from `raid-stripe-tree.h`.
- IO context allocation from Btrfs volume/mapping code.
- Dummy fs/root/device helpers from the selftest framework.
- Real B-tree insertion/deletion/search through the stripe root.

The fixed test configuration uses:
- Two devices.
- RAID1 data profile: `BTRFS_BLOCK_GROUP_DATA | BTRFS_BLOCK_GROUP_RAID1`.
- Device physical placement offset by 1 GiB per device.

## Important Invariants

- Every test must assign `bioc->map_type`, `bioc->size`, `bioc->logical`, and each stripe’s `dev`/`physical` before insertion.
- Lookup checks are usually performed against device 0 by setting `io_stripe.dev`.
- Deletion tests validate both positive surviving mappings and negative lookups for holes/deleted ranges.
- Each test cleans up inserted extents before returning where possible, so independent tests can run in fresh dummy fs contexts.

## Error Handling

Each test reports mismatch details via `test_err()` and returns:
- `-ENOMEM` for allocation failures.
- `-EINVAL` for unexpected lookup success/failure or wrong physical/length results.
- The original Btrfs API return code for insertion/deletion/lookup failures.

## Research Notes

The tests are intentionally explicit and repetitive. That makes individual stripe-tree edge cases easy to inspect and avoids hiding the exact logical/physical range expectations behind helper abstractions.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/raid-stripe-tree-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/zoned-tests.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/zoned-tests.c

## Purpose

This file implements Btrfs zoned-mode selftests for loading a block group allocation offset from per-zone write pointer state. It checks `btrfs_load_block_group_by_raid_type()` across SINGLE, DUP, RAID1, RAID0, and RAID10 layouts, including mixed sequential/conventional zones and degraded/missing-device cases.

## Main Entry Point

- `btrfs_test_zoned(void)`: allocates a dummy `fs_info`, iterates `load_zone_info_tests[]`, and runs `test_load_zone_info()` for each vector.

## Test Data Model

`struct load_zone_info_test_vector` describes each case:
- `raid_type`: Btrfs block group profile.
- `num_stripes`: stripe count.
- `alloc_offsets[8]`: per-stripe zone allocation/write pointer state.
- `last_alloc`: last known allocation offset for conventional-zone reconstruction.
- `bg_length`: block group length passed to dummy block group allocator.
- `degraded`: whether mount option `DEGRADED` should be set.
- `expected_result`: expected return value, default zero.
- `expected_alloc_offset`: expected `bg->alloc_offset` on success.
- `description`: failure context.

Special sentinel offsets:
- `WP_MISSING_DEV`: missing stripe/device.
- `WP_CONVENTIONAL`: conventional zone.
- Normal numeric values represent sequential-zone write pointer offsets.

`struct zone_info` supplies the minimal per-stripe physical/capacity/alloc-offset shape consumed by the target zoned code.

## Harness Behavior

`test_load_zone_info()`:
- Allocates a dummy block group and chunk map.
- Allocates `zone_info` and an active-zone bitmap.
- Sets map type, stripe count, and RAID10 sub-stripes when needed.
- Initializes each zone with capacity `ZONE_SIZE` and vector-provided offset.
- Marks a stripe active if its offset is nonzero and inside the zone.
- Toggles `DEGRADED` mount option according to the vector.
- Calls `btrfs_load_block_group_by_raid_type()`.
- Verifies both return code and successful `bg->alloc_offset`.

## Covered Cases

The vector table covers:

- SINGLE:
  - Sequential zone write pointer load.

- DUP and RAID1:
  - Matching write pointers.
  - Sequential plus conventional zone with matching `last_alloc`.
  - Sequential plus conventional zone with smaller `last_alloc`, accepting the sequential write pointer.
  - Different write pointers as `-EIO`.
  - Missing device behavior, with RAID1 degraded recovery expected to succeed.
  - Conventional/sequence combinations where `last_alloc` is larger than allowed as `-EIO`.

- RAID0:
  - Initial partial write.
  - Progress through second stripe.
  - One stripe advanced.
  - Disordered stripe progression.
  - Excess distance between stripes.
  - Too many partial writes.
  - Missing device under degraded mount still rejected.
  - Sequential/conventional combinations where `last_alloc` reconstructs the global allocation pointer.
  - Four-stripe mixed conventional cases with expected reconstructed offsets and failure for inconsistent `last_alloc`.

- RAID10:
  - Same style as RAID0, but with mirrored sub-stripe pairs.
  - Matching mirrored pair progression.
  - Conventional-zone combinations.
  - Disordered/far/too-many-partial failures.
  - Missing mirror group under degraded mount rejected for RAID0-level loss semantics.
  - Eight-stripe mixed conventional reconstruction cases.

## Dependencies and Integration

This selftest depends on:
- Dummy fs/block group helpers from the Btrfs selftest framework.
- Chunk map allocation/freeing from `volumes.h`.
- Zoned allocator logic from `zoned.h`.
- Linux cleanup attributes and allocation helpers.

It tests the zoned block-group load logic without real zoned devices by supplying synthetic per-zone metadata.

## Important Invariants

- `ZONE_SIZE` is fixed at 256 MiB.
- Stripe progression is evaluated in units of `BTRFS_STRIPE_LEN`; `HALF_STRIPE_LEN` is used for partial-stripe cases.
- Active bitmap bits are set only for sequential zones with an in-zone nonzero allocation offset.
- `bg->alloc_offset` is checked only when the target function succeeds.
- Expected error messages are normal because invalid vectors deliberately exercise corruption/inconsistency detection.

## Error Handling

Allocation failures return `-ENOMEM`. Unexpected target return values or allocation offsets return `-EINVAL` after a `test_err()` diagnostic.

## Research Notes

The test table is the core of this file. It documents zoned write-pointer reconstruction rules for mirrored, striped, and mixed conventional/sequential layouts in executable form.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tests/zoned-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/transaction.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/transaction.c

## Purpose

This file implements the Btrfs transaction lifecycle: starting/joining transactions, metadata reservation, root tracking, transaction end, commit orchestration, snapshot creation during commit, writeback/superblock persistence, abort cleanup, deleted snapshot cleanup, and transaction handle cache initialization.

It is one of the central coordination files for Btrfs metadata consistency.

## Transaction State Model

The file documents and implements a staged transaction state machine:

- `TRANS_STATE_RUNNING`: normal metadata modifications allowed.
- `TRANS_STATE_COMMIT_PREP`: a committer has started preparing.
- `TRANS_STATE_COMMIT_START`: new external starts/attaches are blocked; joins may still be allowed depending on type.
- `TRANS_STATE_COMMIT_DOING`: all normal joining is blocked; supporting trees are updated.
- `TRANS_STATE_UNBLOCKED`: tree updates are complete; a new transaction may start while old one writes out.
- `TRANS_STATE_SUPER_COMMITTED`: superblock has been written.
- `TRANS_STATE_COMPLETED`: extent commit cleanup done and transaction removed.

`btrfs_blocked_trans_types[]` defines which transaction handle types are blocked in each state.

## Major Public APIs

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

Root/snapshot helpers:
- `btrfs_record_root_in_trans()`
- `btrfs_add_dropped_root()`
- `btrfs_add_dead_root()`
- `btrfs_maybe_wake_unfinished_drop()`
- `btrfs_clean_one_deleted_snapshot()`

Writeback/helpers:
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

## Transaction Creation and Joining

`join_transaction()`:
- Runs under `fs_info->trans_lock`.
- Rejects new work on filesystem error.
- Joins existing running transactions if the transaction state allows the requested type.
- Increments writer/extwriter counters and transaction refcount.
- Allocates and initializes a new `struct btrfs_transaction` when no transaction exists and the type permits starting one.
- Initializes delayed-ref xarrays, dirty page trees, pinned extent tree, block group lists, dropped roots, wait queues, generation, and transaction list membership.

`start_transaction()`:
- Handles qgroup metadata preallocation.
- Reserves transaction metadata and delayed-ref space.
- Optionally reserves extra space for relocation root creation.
- Refills delayed-ref reserve for zero-item throttling starts.
- Allocates a transaction handle from `btrfs_trans_handle_cachep`.
- Handles freeze protection with `sb_start_intwrite()`.
- Waits for blocked transactions when appropriate.
- Joins/starts the transaction.
- Sets up transaction handle fields and local delayed-ref reserve.
- Performs forced chunk allocation when metadata space requires it.
- Records the root in the transaction after `current->journal_info` is initialized to avoid recursion deadlocks.
- Converts qgroup prealloc reservation to per-transaction reservation.

## Root Tracking

`record_root_in_trans()` and `btrfs_record_root_in_trans()`:
- Ensure shareable roots modified in a transaction are tagged in `fs_roots_radix` with `BTRFS_ROOT_TRANS_TAG`.
- Update `root->last_trans`.
- Initialize relocation roots when needed.
- Use `BTRFS_ROOT_IN_TRANS_SETUP` and memory barriers so concurrent users can distinguish setup from completed root transaction recording.

`btrfs_add_dropped_root()`:
- Adds a dropped root to the transaction’s `dropped_roots`.
- Clears the root’s radix transaction tag so commit does not update it.

`switch_commit_roots()`:
- Under `commit_root_sem`, replaces each root’s `commit_root` with the current root node.
- Releases dirty log pages and qgroup swapped-block state.
- Frees roots listed in `dropped_roots`.

## Ending Transactions

`__btrfs_end_transaction()`:
- Handles nested handle references through `use_count`.
- Releases metadata reservations.
- Creates pending block groups.
- Releases chunk metadata reservations.
- Ends freeze write protection for freezable transaction types.
- Uninhibits extent buffer writeback before decrementing writer counters.
- Decrements transaction writer/extwriter counters.
- Wakes commit waiters.
- Releases lockdep maps and transaction references.
- Clears `current->journal_info`.
- Optionally runs delayed iputs.
- Returns abort or read-only errors when applicable.

## Commit Flow

`btrfs_commit_transaction()` is the main commit state machine.

High-level sequence:
1. Validate handle use count and acquire commit-prep lockdep state.
2. Stop early on already aborted transaction.
3. Release handle metadata reservation.
4. Run an initial delayed-ref flush once per transaction.
5. Create pending block groups.
6. Start dirty block group I/O once per transaction.
7. If another committer is already active, enqueue pending snapshot, end this handle, and wait for target commit state.
8. Become the committer by moving to `TRANS_STATE_COMMIT_PREP`.
9. Wait for previous transaction if needed.
10. Move to `TRANS_STATE_COMMIT_START`.
11. Start delalloc flush if `FLUSHONCOMMIT`.
12. Run delayed items.
13. Wait for external writers to drain.
14. Run delayed items again and wait delalloc.
15. Wait for fast-fsync pending ordered extents.
16. Pause scrub.
17. Move to `TRANS_STATE_COMMIT_DOING`.
18. Wait for all writers to drain.
19. Lock relocation mutex.
20. Create pending snapshots.
21. Run delayed items and delayed refs.
22. Assert delayed root empty.
23. Commit filesystem roots and free log root tree.
24. Account qgroup extents.
25. Commit cow-only roots.
26. Add tree/chunk roots to switch list and switch commit roots.
27. Update super root pointers and prepare `super_for_commit`.
28. Commit device sizes and clear log error flags.
29. Release chunk metadata.
30. Lock tree log mutex, unblock transaction, and set `running_transaction = NULL`.
31. Wake waiters and optionally wake cleaner for feature changes.
32. Uninhibit extent buffer writeback.
33. Write and wait dirty transaction extents.
34. Write all superblocks.
35. Mark `TRANS_STATE_SUPER_COMMITTED`.
36. Finish extent commit.
37. Clear full-space flags if needed.
38. Update last committed transaction id.
39. Mark `TRANS_STATE_COMPLETED`.
40. Remove from transaction list, release references, resume scrub, clear journal info, and free handle.

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
- Updates committed dev-replace cursor.

`update_cowonly_root()` loops until the root item bytenr/used fields stabilize after updating the root pointer.

## Snapshot Creation

Pending snapshots are created only during transaction commit.

`create_pending_snapshot()`:
- Sets up encrypted filename with NOFS allocation context.
- Allocates a new root objectid.
- Sets qgroup skip id for the new snapshot.
- Runs relocation pre-snapshot hooks and reserves extra metadata if needed.
- Switches transaction block reserve to the pending snapshot reservation.
- Records the parent root and source root in the transaction.
- Allocates a directory index and verifies name absence.
- Creates the new qgroup.
- Runs delayed items before copying the root.
- Copies source root item and root block.
- Sets snapshot flags, UUIDs, parent UUID, received UUID handling, and timestamps.
- Inserts the new root item and root refs.
- Opens the new fs root.
- Runs relocation post-snapshot hook.
- Performs qgroup inheritance/accounting.
- Inserts the directory item and updates parent inode.
- Adds UUID tree entries.
- Restores reserves, clears skip qgroup, frees name/root item resources, and stores errors in `pending->error`.

`qgroup_account_snapshot()` performs a special mini-commit sequence for full qgroup accounting so snapshot qgroup inheritance sees consistent root and extent accounting.

## Writeback and Waiting

`btrfs_write_marked_extents()`:
- Converts dirty extent bits to `EXTENT_NEED_WAIT`.
- Starts writeback for btree inode ranges.
- If marking fails with `-ENOMEM`, still waits for writeback to avoid committing unwritten metadata.

`__btrfs_wait_marked_extents()` waits on ranges marked `EXTENT_NEED_WAIT` and clears that state.

`btrfs_wait_extents()` and `btrfs_wait_tree_log_extents()` translate writeback error flags into `-EIO`.

`btrfs_write_and_wait_transaction()` writes and waits all transaction dirty pages and releases the transaction dirty-page io tree.

## Abort and Cleanup

`cleanup_transaction()`:
- Calls `btrfs_abort_transaction()`.
- If still running, transitions to commit-doing and waits for writers.
- Removes the transaction from the transaction list.
- Calls `btrfs_cleanup_one_transaction()`.
- Clears `running_transaction`.
- Releases freeze protection and transaction refs.
- Cancels scrub unless relocation is running.
- Uninhibits writeback and frees handle.

`btrfs_cleanup_pending_block_groups()` releases delayed-ref reservations for pending new block groups on abort.

`__btrfs_abort_transaction()`:
- Stores abort error in both handle and transaction.
- Dumps space info for first `-ENOSPC` abort.
- Wakes transaction waiters.
- Delegates filesystem error handling to `__btrfs_handle_fs_error()`.

## Deleted Snapshot Cleanup

`btrfs_add_dead_root()` adds roots to `fs_info->dead_roots`, prioritizing unfinished drops.

`btrfs_clean_one_deleted_snapshot()`:
- Removes one root from `dead_roots`.
- Kills delayed nodes.
- Calls `btrfs_drop_snapshot()` with mixed-backref behavior based on root header.
- Drops the root reference.
- Returns `1` when more work may remain, `0` when none or on error.

## Important Concurrency and Consistency Points

- `fs_info->trans_lock` protects running transaction pointer, transaction state transitions, and transaction list manipulations.
- Writer counters gate commit phases and prevent metadata mutation while roots/supers are being committed.
- Extwriter counters allow commit to block userspace/external transaction starts before fully blocking all writers.
- `tree_log_mutex` prevents a log tree superblock write from racing between transaction unblock and transaction superblock write.
- `reloc_mutex` prevents relocation from changing extent layout during critical commit phases.
- `commit_root_sem` protects commit root switching.
- Scrub is paused during the critical commit section.
- Lockdep state annotations model transaction waiting and state transitions.

## Research Notes

This file is the authoritative Btrfs transaction coordinator. Its behavior depends on many subsystems: delayed refs/items, qgroups, block groups, chunk allocation, relocation, tree log, scrub, dev-replace, dirty block group writeback, root tree updates, and superblock writes. Most subtle bugs here would be ordering bugs: allowing a writer too late, publishing a superblock before metadata writeback, losing qgroup/snapshot consistency, or mishandling abort cleanup while other tasks still hold transaction references.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/transaction.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/transaction.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/transaction.h

## Purpose

This header defines the Btrfs transaction state machine types, transaction and transaction-handle structures, pending snapshot state, transaction type flags, abort helpers, qgroup skip helpers, and public transaction API prototypes.

## Key Definitions

- `BTRFS_TRANS_DIO_WRITE_STUB`: sentinel stored in `journal_info` for direct I/O write deadlock avoidance.
- `BTRFS_ROOT_TRANS_TAG`: radix-tree tag for roots participating in a transaction.
- `enum btrfs_trans_state`: transaction lifecycle states from `RUNNING` through `COMPLETED`.
- Transaction flags:
  - `BTRFS_TRANS_HAVE_FREE_BGS`
  - `BTRFS_TRANS_DIRTY_BG_RUN`
  - `BTRFS_TRANS_CACHE_ENOSPC`

## `struct btrfs_transaction`

Represents a filesystem-wide transaction. Important fields:
- `transid`: transaction generation.
- `num_extwriters`: external/user-visible writers that must drain before commit proceeds.
- `num_writers`: all transaction writers.
- `use_count`: lifetime refcount.
- `state`: transaction state, protected by `fs_info->trans_lock` for changes.
- `aborted`: abort errno.
- Wait queues for writers, commit waiters, and pending ordered extents.
- Lists for pending snapshots, device updates, dirty roots to switch, dirty/io block groups, dropped roots, deleted block groups.
- `dirty_pages` and `pinned_extents` extent I/O trees.
- `delayed_refs`: delayed reference root.
- Block group cache write coordination and dirty/dropped root locks.
- `pending_ordered`: fast-fsync ordered extents that commit must wait for.

## Transaction Type Flags

Internal bit flags:
- `__TRANS_FREEZABLE`
- `__TRANS_START`
- `__TRANS_ATTACH`
- `__TRANS_JOIN`
- `__TRANS_JOIN_NOLOCK`
- `__TRANS_DUMMY`
- `__TRANS_JOIN_NOSTART`

Public combinations:
- `TRANS_START`
- `TRANS_ATTACH`
- `TRANS_JOIN`
- `TRANS_JOIN_NOLOCK`
- `TRANS_JOIN_NOSTART`
- `TRANS_EXTWRITERS`

These flags drive transaction joining and commit blocking rules in `transaction.c`.

## `struct btrfs_trans_handle`

Represents a task’s handle into a transaction. Important fields:
- `transid`
- reservation counters: `bytes_reserved`, `delayed_refs_bytes_reserved`, `chunk_bytes_reserved`
- delayed-ref counters
- `transaction`
- active/original block reserves
- optional `pending_snapshot`
- `use_count`
- transaction type
- per-handle abort state
- mode booleans such as `adding_csums`, `allocating_chunk`, `removing_chunk`, `reloc_reserved`, `in_fsync`
- local `new_bgs` list
- local delayed-ref block reserve
- `writeback_inhibited_ebs` xarray for extent buffers whose writeback is inhibited by the handle

## `struct btrfs_pending_snapshot`

Carries all state needed for snapshot creation during commit:
- dentry, parent inode, source root, root item, resulting snapshot root.
- qgroup inheritance.
- path.
- operation block reserve.
- error status.
- preallocated anonymous block device number.
- readonly flag.
- transaction list node.

## Inline Helpers

- `btrfs_set_inode_last_trans()`: updates inode transaction/log tracking under inode lock.
- `btrfs_set_skip_qgroup()` / `btrfs_clear_skip_qgroup()`: set or clear delayed-ref qgroup id to skip during snapshot/qgroup accounting.
- `btrfs_abort_should_print_stack()`: suppresses stack traces for common external errors (`-EIO`, `-EROFS`, `-ENOMEM`) and prints for likely bug-triggered errors.

## Abort Macro

`btrfs_abort_transaction(trans, error)`:
- Reports the first transaction abort since mount.
- Optionally emits a warning/stack trace depending on error class.
- Calls `__btrfs_abort_transaction()` with function, line, error, and first-hit state.

## Public API Surface

The header exports start/join/attach/end/commit/wait APIs, transaction throttling, root recording, dirty extent write/wait helpers, dropped/dead root helpers, chunk metadata release, abort implementation, and module init/exit for the transaction handle cache.

## Research Notes

This header establishes the transaction contract used throughout Btrfs. The most important design signal is the distinction between a global `btrfs_transaction` and per-task `btrfs_trans_handle`, plus the explicit separation of external writers from all writers for commit ordering.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/transaction.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-checker.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-checker.c

## Purpose

This file implements Btrfs tree block validation. It checks nodes and leaves read from disk for structural consistency and item-level sanity before the rest of the filesystem code trusts their contents. It is intended to catch fuzzed/corrupt images and internal bugs early while avoiding false rejection of valid filesystems.

## Diagnostic Helpers

- `generic_err()`: common corrupt leaf/node reporter with root, block, slot, and page dump.
- `file_extent_err()`: file extent reporter including inode and file offset.
- `dir_item_err()`: directory/xattr reporter including inode.
- `block_group_err()`: block group reporter including start/length.
- `chunk_err()`: chunk reporter for either chunk tree leaves or superblock syschunk array.
- `dev_item_err()`, `extent_err()`, `inode_ref_err()`: specialized diagnostics.

Diagnostics consistently return `-EUCLEAN` for detected corruption.

## File Extent Validation

`check_extent_data_item()` validates `BTRFS_EXTENT_DATA_KEY` items:
- File offset alignment.
- Previous key objectid continuity for subvolume-tree inode-related items.
- Minimum item size.
- Valid file extent type.
- Valid compression and zero encryption.
- Inline extents:
  - Must have key offset zero.
  - Uncompressed inline ram bytes must match item size.
  - Compressed inline extents skip on-disk size match.
- Regular/prealloc extents:
  - Must have fixed item size.
  - ram bytes, disk bytenr, disk num bytes, offset, and num bytes aligned to sectorsize.
  - Extent end must not overflow.
  - Consecutive extents in the same leaf must not overlap.
- Debug builds warn on non-compressed ram/disk size mismatch.

`file_extent_end()` supports overlap checking.

## Csum Validation

`check_csum_item()` validates:
- Objectid equals `BTRFS_EXTENT_CSUM_OBJECTID`.
- Key offset sectorsize alignment.
- Item size alignment to checksum size.
- Consecutive csum item ranges do not overlap.

## Inode, Directory, and Xattr Validation

`check_prev_ino()` detects missing inode-item ordering context for inode-related keys in subvolume trees.

`check_inode_key()` validates inode location keys and xattr zero location keys.

`check_root_key()` validates root ids, relocation root rules, and prevents directory-like references to non-fs trees.

`check_dir_item()` iterates packed `struct btrfs_dir_item` entries and validates:
- Header and payload bounds.
- Location key type and value.
- Directory file type.
- Xattr type/key consistency.
- Name/data length limits.
- Non-xattr data length must be zero.
- DIR_ITEM/XATTR key hash matches item name.

`check_inode_item()` validates:
- Item size.
- Inode generation/transid against super generation + 1.
- Mode bit mask and valid file type.
- Directory nlink <= 1.
- Inode incompat and ro-compat flags, rejecting unknown ro flags on writable mounts.

`check_inode_ref()` and `check_inode_extref()` validate packed inode ref/extref entry boundaries and nonzero name payload shape.

## Root Item Validation

`check_root_item()`:
- Validates key rules through `check_root_key()`.
- Accepts modern and legacy root item sizes.
- Checks generation, generation_v2, and last_snapshot against super generation + 1.
- Checks root bytenr alignment and root/drop levels below `BTRFS_MAX_LEVEL`.
- Rejects nonzero `drop_progress.objectid` with `drop_level == 0`.
- Allows only readonly and dead root flags.

## Block Group and Chunk Validation

`check_block_group_item()` validates:
- Nonzero length.
- Item size based on whether remap tree is enabled.
- Chunk objectid/global root id rules.
- Used bytes <= block group length.
- At most one profile bit.
- Metadata remap/remapped flags require remap-tree incompat.
- Type is one of allowed data/metadata/system/remap/mixed values.
- V2 remap bytes and identity remap count within block group bounds.

`valid_stripe_count()` expresses profile-specific stripe/sub-stripe constraints.

`btrfs_check_chunk_valid()` validates chunk items and superblock syschunk entries:
- Stripe count, copies, parity constraints unless remapped.
- Logical address alignment.
- Sector size match.
- Nonzero aligned length and no overflow.
- Stripe length equals `BTRFS_STRIPE_LEN`.
- Chunk length below artificial maximum.
- Recognized type/profile flags.
- Exactly one or zero profile bits.
- Required type flag.
- System chunks cannot mix with data/metadata.
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
- Inline ref bounds, allowed ref types, alignment, objectid/root validity, nonzero counts.
- Inline ref ordering by type and descending sequence/hash.
- No padding.
- Inline ref count not greater than total refs.
- Previous extent item does not overlap the current one.

`check_simple_keyed_refs()` validates simple keyed backrefs, including item size and key alignment.

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
- Validates aligned key, nonzero length, and exact bitmap item size for the represented range.

## Leaf Validation

`check_leaf_item()` dispatches per-key-type validators.

`__btrfs_check_leaf()` performs whole-leaf checks:
- Header level must be 0.
- `BTRFS_HEADER_FLAG_WRITTEN` must be set.
- Certain roots must not have empty leaves, with exceptions for relocation and extent-tree-v2 empty extent trees.
- Keys must be strictly increasing.
- Item data must be contiguous from the end of the leaf, with no holes/overlaps.
- Item data must stay inside leaf data area.
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
- Skips testing fs, unknown owner `0`, log tree, and reloc tree cases.
- For non-subvolume trees, extent buffer owner must equal root owner.
- For subvolume trees, owner may differ but must still be a valid subvolume tree id.

`btrfs_verify_level_key()`:
- Verifies extent buffer level against expected parent check level.
- Optionally verifies first key, but skips live tree blocks newer than last committed transaction.
- Rejects empty tree blocks when a first-key check is required.
- Compares expected first key to first node/item key.

## Dependencies and Integration

This file depends heavily on:
- On-disk format accessors.
- Btrfs feature flags from the superblock.
- Filesystem geometry (`sectorsize`, `nodesize`, csum size).
- RAID profile definitions.
- Error reporting and page dump facilities.
- Tree read paths that call leaf/node validators after reading extent buffers.

## Important Invariants

- Validators must avoid rejecting valid historical formats, hence legacy root item support and selective strictness.
- Item checks rely only on item data and nearby key ordering, not broader tree traversal.
- Feature-gated formats such as skinny metadata, RAID stripe tree, remap tree, mixed groups, and extent-tree-v2 are explicitly checked.
- Empty-tree allowances are root- and feature-dependent.
- `-EUCLEAN` is the standard corruption return.

## Research Notes

`tree-checker.c` is a defensive boundary between raw on-disk metadata and normal Btrfs code. It encodes many filesystem invariants in one place, including newer feature gates for remap tree and RAID stripe tree. Its highest-risk maintenance area is balancing stricter corruption detection against compatibility with valid existing filesystems.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-checker.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-checker.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-checker.h

## Purpose

This header declares the Btrfs tree-checker interface and shared validation status types used by kernel Btrfs code and btrfs-progs-compatible validation paths.

## Key Types

`struct btrfs_tree_parent_check` describes expected parent-derived properties for an extent buffer:
- `owner_root`: expected owner root, or zero to skip.
- `transid`: expected transaction id, or zero to skip. Comments note this should only be skipped by backref-walk-related code.
- `first_key`: expected first key.
- `has_first_key`: whether first-key validation should be performed.
- `level`: expected tree level; should always be set.

`enum btrfs_tree_block_status` gives structured validation outcomes:
- Clean.
- Invalid nritems.
- Invalid parent key.
- Bad key order.
- Invalid level.
- Invalid free space.
- Invalid offsets.
- Invalid block pointer.
- Invalid item.
- Invalid owner.
- Written flag not set.

## Constants

`BTRFS_BLOCK_GROUP_VALID` defines the accepted block group flag mask as type flags, profile flags, and `BTRFS_BLOCK_GROUP_REMAPPED`.

## Exported Functions

- `__btrfs_check_leaf(struct extent_buffer *leaf)`: returns detailed tree block status.
- `__btrfs_check_node(struct extent_buffer *node)`: returns detailed tree block status.
- `btrfs_check_leaf(struct extent_buffer *leaf)`: returns `0` or `-EUCLEAN`.
- `btrfs_check_node(struct extent_buffer *node)`: returns `0` or `-EUCLEAN`.
- `btrfs_check_chunk_valid(...)`: common chunk validation for leaf chunk items and superblock syschunk arrays.
- `btrfs_check_eb_owner(...)`: validates extent buffer owner against expected root owner.
- `btrfs_verify_level_key(...)`: validates extent buffer level and optional first key against parent check metadata.

## Dependencies and Integration

The header forward-declares Btrfs core structures and includes on-disk Btrfs tree definitions. It is consumed by tree read/verification paths and by code that needs chunk validation independent of full leaf validation.

## Research Notes

This header cleanly separates detailed status-returning internal validators from simple errno-returning public wrappers. The `btrfs_tree_parent_check` structure is the key contract for validating that a read tree block matches the parent pointer’s expectations.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/tree-checker.h -->