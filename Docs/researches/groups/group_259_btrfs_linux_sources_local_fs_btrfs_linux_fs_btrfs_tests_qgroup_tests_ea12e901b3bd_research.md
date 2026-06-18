# Group Research: group_259_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_tests_qgroup_tests_ea12e901b3bd

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/qgroup-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/qgroup-tests.c

## Summary
Selftests Btrfs qgroup accounting by building dummy extent-tree state, walking backrefs, and calling `btrfs_qgroup_account_extent()` directly for controlled add/remove scenarios.

## Main Responsibilities
- Create synthetic extent items and inline/tree backrefs in a dummy extent tree.
- Add and remove tree refs while manually updating extent ref counts.
- Use `btrfs_find_all_roots()` to compute old/new root ownership sets.
- Verify qgroup referenced/exclusive counts after extent ownership changes.
- Set up dummy fs roots for `BTRFS_FS_TREE_OBJECTID` and `BTRFS_FIRST_FREE_OBJECTID`.

## Key APIs
- Test entry: `btrfs_test_qgroups()`.
- Helpers: `insert_normal_tree_ref()`, `add_tree_ref()`, `remove_extent_item()`, `remove_extent_ref()`.
- Test cases: `test_no_shared_qgroup()`, `test_multiple_refs()`.
- Btrfs APIs under test: `btrfs_create_qgroup()`, `btrfs_find_all_roots()`, `btrfs_qgroup_account_extent()`, `btrfs_verify_qgroup_counts()`.

## Important Behavior
`test_no_shared_qgroup()` creates one qgroup, inserts a tree ref for one root, accounts the extent, expects referenced and exclusive bytes to equal `nodesize`, then removes the extent item and expects both counters to return to zero.

`test_multiple_refs()` creates a second qgroup/root, first accounts a single-root extent, then adds a second root reference. Both qgroups should report referenced bytes but zero exclusive bytes while the extent is shared. Removing the second ref should drop that qgroup to zero and restore exclusivity to the first root.

The test bypasses normal delayed refs because dummy transactions do not model the full kernel delayed-ref machinery. It directly computes old/new root lists and passes them to qgroup accounting.

## Setup and State
The entry point allocates dummy `fs_info` and an extent root, inserts it as a global extent-tree root, points `tree_root` and `quota_root` at it, enables `BTRFS_FS_QUOTA_ENABLED`, allocates an extent buffer at `nodesize`, and inserts two dummy fs roots into `fs_roots_radix`.

## Risks
These tests depend on precise dummy tree shape and bytenr choices. Bytenr `0` is intentionally avoided because backref walking assumes real nonzero block addresses. The tests also depend on `btrfs_qgroup_account_extent()` freeing the ulists passed into it.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/qgroup-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/raid-stripe-tree-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/raid-stripe-tree-tests.c

## Summary
Selftests RAID stripe tree insert, update, lookup, and deletion behavior for a synthetic two-device RAID1 filesystem.

## Main Responsibilities
- Allocate dummy fs/device/stripe-root state with `RAID_STRIPE_TREE` incompat enabled.
- Insert RAID stripe extents through `btrfs_insert_one_raid_extent()`.
- Delete full, front, tail, middle, and multi-item ranges through `btrfs_delete_raid_extent()`.
- Verify logical-to-physical mapping and surviving lengths with `btrfs_get_raid_extent_offset()`.
- Run each scenario in a fresh dummy transaction/filesystem.

## Key APIs
- Test entry: `btrfs_test_raid_stripe_tree()`.
- Harness: `run_test()`, `btrfs_device_by_devid()`.
- Test cases: `test_simple_create_delete()`, `test_create_update_delete()`, `test_tail_delete()`, `test_front_delete()`, `test_front_delete_prev_item()`, `test_punch_hole()`, `test_punch_hole_3extents()`, `test_delete_two_extents()`.

## Important Behavior
The simple create/delete case writes a 64K RAID1 stripe extent at logical 1M, with device 0 physical at 1M and device 1 physical at 1G+1M, verifies lookup, then deletes it.

The update case overwrites the same logical range with new physical addresses offset by 1G, exercising update-in-place behavior in RAID stripe extent insertion.

Tail and front delete cases truncate a single 64K item from either end and verify both the surviving mapping and the deleted hole.

`test_front_delete_prev_item()` inserts adjacent 1M items, deletes a range starting halfway through the first and continuing into the second, then verifies the first item is shortened, the second item starts later, and the middle range is absent.

Punch-hole tests split one or several extents around deleted middle ranges. The three-extent case verifies deletion of all middle extents plus partial trimming of both bookends.

`test_delete_two_extents()` removes the first two of three adjacent extents and verifies the third remains unchanged.

## Setup and State
Each scenario gets a new dummy `fs_info`, root, leaf extent buffer, and two dummy devices with devids `0` and `1`. The stripe root is both `fs_info->stripe_root` and `tree_root` for the dummy btree operations.

## Risks
The file is scenario-heavy and sensitive to exact length/offset expectations. Several cleanup paths delete surviving extents after verification, so a failed intermediate assertion may leave dummy tree state unclean only within that isolated test instance.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/raid-stripe-tree-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/zoned-tests.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/zoned-tests.c

## Summary
Selftests zoned block-group write-pointer loading for different RAID profiles, conventional/sequential zone mixtures, degraded cases, and invalid write-pointer patterns.

## Main Responsibilities
- Define table-driven test vectors for `btrfs_load_block_group_by_raid_type()`.
- Model per-stripe physical address, capacity, and allocation offset.
- Mark active stripes when sequential-zone write pointers are nonzero and within zone capacity.
- Toggle the dummy filesystem `DEGRADED` mount option per case.
- Verify expected return code and computed `bg->alloc_offset`.

## Key APIs
- Test entry: `btrfs_test_zoned()`.
- Harness: `test_load_zone_info()`.
- Data structures: `load_zone_info_test_vector`, local `zone_info`.
- API under test: `btrfs_load_block_group_by_raid_type()`.

## Important Behavior
The vector table covers SINGLE, DUP, RAID1, RAID0, and RAID10.

DUP and RAID1 validate matching mirrored write pointers, sequential plus conventional-zone handling via `last_alloc`, erroring on mismatched write pointers, and missing-device behavior. RAID1 accepts a partial missing device only for degraded mount; DUP treats partial missing device as invalid.

RAID0 and RAID10 validate stripe-progress reconstruction across partially written stripes, one-stripe-advanced cases, conventional-zone gaps, and `last_alloc` reconciliation. They reject disordered stripes, excessive distance between write pointers, too many partial writes, and missing stripes in RAID0-level layouts even when degraded.

The test uses sentinel values `WP_MISSING_DEV` and `WP_CONVENTIONAL` to describe unavailable or conventional-zone stripes.

## Setup and State
Each test allocates a dummy block group and chunk map, fills per-stripe test zone info, sets RAID10 `sub_stripes = 2`, and passes an active bitmap to the zoned loader.

## Risks
The table encodes expected allocator reconstruction semantics. Changes to zoned RAID placement, conventional-zone treatment, or degraded acceptance rules must update both the vector descriptions and expected offsets/errors.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tests/zoned-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/transaction.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/transaction.c

## Summary
Implements Btrfs transaction lifecycle management: joining/starting transactions, reserving metadata, committing roots and superblocks, creating pending snapshots, waiting for commits, handling aborts, and cleaning up committed or failed transactions.

## Main Responsibilities
- Maintain transaction state transitions from running through commit prep/start/doing/unblocked/super committed/completed.
- Allocate, join, reference, and release `btrfs_transaction` and `btrfs_trans_handle`.
- Reserve and release transaction metadata, qgroup metadata, delayed-ref metadata, chunk metadata, and relocation-root metadata.
- Record dirty roots in a transaction and switch commit roots after commit.
- Commit fs roots, cow-only roots, dirty block groups, delayed refs/items, qgroups, device stats, dev-replace state, and superblocks.
- Create pending snapshots at commit time with qgroup inheritance, root refs, dir items, UUID-tree entries, and relocation hooks.
- Provide synchronous/asynchronous commit helpers and wait-for-commit barriers.
- Abort transactions and clean up aborted transaction state.

## Key APIs
- Start/join/attach: `btrfs_start_transaction()`, `btrfs_start_transaction_fallback_global_rsv()`, `btrfs_join_transaction()`, `btrfs_join_transaction_spacecache()`, `btrfs_join_transaction_nostart()`, `btrfs_attach_transaction()`, `btrfs_attach_transaction_barrier()`.
- End/commit/wait: `btrfs_end_transaction()`, `btrfs_end_transaction_throttle()`, `btrfs_commit_transaction()`, `btrfs_commit_transaction_async()`, `btrfs_commit_current_transaction()`, `btrfs_wait_for_commit()`, `btrfs_throttle()`.
- Root tracking: `btrfs_record_root_in_trans()`, `btrfs_add_dropped_root()`, `btrfs_add_dead_root()`, `btrfs_maybe_wake_unfinished_drop()`, `btrfs_clean_one_deleted_snapshot()`.
- I/O waiting: `btrfs_write_marked_extents()`, `btrfs_wait_tree_log_extents()`.
- Abort/init: `__btrfs_abort_transaction()`, `btrfs_transaction_init()`, `btrfs_transaction_exit()`.

## Important Behavior
`join_transaction()` either attaches to an existing running transaction or creates a new one, honoring the blocked transaction type table for each commit state. Transaction creation initializes delayed-ref xarrays, dirty/pinned extent I/O trees, block-group lists, snapshot/drop lists, wait queues, refcounts, and bumps `fs_info->generation`.

`start_transaction()` reserves qgroup metadata, btree metadata, delayed-ref space, and optional relocation-root space before joining. It handles nested transaction handles through `current->journal_info`, freeze protection for freezable transaction types, blocked-current-transaction waits, delayed-ref reserve refills, forced chunk allocation, and root recording after handle setup.

`btrfs_commit_transaction()` is the central commit sequence. It runs delayed refs/items, starts dirty block-group I/O, serializes against other committers, waits for previous transactions as needed, blocks external writers, waits pending ordered extents, pauses scrub, creates snapshots, commits fs roots and cow-only roots, switches commit roots, updates the super copy, unblocks new transactions before writing metadata/superblocks, writes and waits dirty btree extents, writes all supers, finishes extent commit, marks the transaction completed, and releases references.

Snapshot creation is deliberately delayed into commit. `create_pending_snapshot()` allocates a new root id, sets qgroup skip state, handles relocation reservation/hooks, records parent/source roots, copies the source root, inserts root items and root refs, gets the new fs root, performs qgroup full/simple inheritance, inserts the parent dir item, updates parent inode, and records UUID-tree entries.

Abort cleanup marks the transaction aborted, forces the filesystem read-only through fs error handling, wakes waiters, cancels scrub unless relocation is running, cleans one transaction, drops pending block groups, releases reservations, and removes the failed transaction from lists.

## State and Synchronization
Transaction state is protected mainly by `fs_info->trans_lock`; writer counts use atomics and wait queues. Commit-root switching uses `commit_root_sem`. Root transaction setup uses `reloc_mutex` plus `BTRFS_ROOT_IN_TRANS_SETUP` memory barriers. Commit critical sections coordinate with scrub, relocation, tree-log mutex, block-group mutexes, freeze intwrite references, and lockdep maps for transaction states/writer counts.

## Risks
Commit ordering is fragile: delayed refs, qgroups, snapshots, root updates, dirty block groups, metadata writeback, and superblock writes must occur in the right sequence. Error paths must release reservations without letting another task observe partially committed state. Snapshot qgroup accounting contains explicit race-window comments and a simplified internal commit, making it particularly sensitive to changes.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/transaction.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/transaction.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/transaction.h

## Summary
Declares Btrfs transaction state, transaction and transaction-handle structures, pending snapshot state, transaction type flags, abort helpers, qgroup skip helpers, and public transaction APIs.

## Main Responsibilities
- Define `enum btrfs_trans_state` commit lifecycle states.
- Define `struct btrfs_transaction` for global transaction state.
- Define `struct btrfs_trans_handle` for per-task participation and reservations.
- Define `struct btrfs_pending_snapshot` for snapshot work deferred into commit.
- Provide inline helpers for inode last-trans updates and qgroup skip-id state.
- Provide the `btrfs_abort_transaction()` macro and abort stack-print policy.
- Export transaction start/join/commit/wait/root/dead-root APIs.

## Key Structures
`struct btrfs_transaction` stores transid, external/total writer counts, refcount, state, abort code, dirty pages, wait queues, pending snapshots, device updates, roots to switch, dirty/io/deleted block groups, dropped roots, pinned extents, delayed refs, and pending ordered extents.

`struct btrfs_trans_handle` stores reservation accounting, chunk metadata reservation, delayed-ref counters, transaction pointer, block reservation pointers, pending snapshot pointer, type flags, abort code, qgroup/csum/chunk flags, fsync flag, new block groups, local delayed-ref reserve, and inhibited extent-buffer writeback xarray.

`struct btrfs_pending_snapshot` captures dentry, parent dir inode, source root, copied root item, resulting root, qgroup inheritance, path, block reserve, error, anon device number, readonly flag, and list linkage.

## Important Behavior
Transaction type bits distinguish start, attach, join, join-nolock, dummy, and join-nostart modes. `TRANS_EXTWRITERS` covers transaction starts and attaches, which must drain before the commit critical section proceeds.

`TRANS_ABORTED()` uses `READ_ONCE()` because abort state is lockless and can change between checks, though once nonzero it does not change.

`btrfs_abort_transaction()` reports only the first abort since mount with optional stack trace. It suppresses stack traces for common external failures like `-EIO`, `-EROFS`, and `-ENOMEM`.

## Risks
The header encodes concurrency contracts relied on by many files. Changing state ordering, transaction type bits, or abort semantics affects commit blocking, freeze behavior, fsync interaction, qgroup accounting, and cleanup paths across the filesystem.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/transaction.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.c

## Summary
Validates Btrfs tree blocks, leaf items, chunks, ownership, and parent key/level expectations when metadata is read or checked, rejecting corrupted structures with detailed diagnostics.

## Main Responsibilities
- Emit corruption diagnostics for generic items, file extents, directory items, block groups, chunks, devices, and extents.
- Validate item-specific content for common Btrfs key types.
- Validate whole-leaf key ordering, item offsets, item sizes, item packing, and required non-empty trees.
- Validate whole-node level, item count, child block pointers, and key ordering.
- Validate chunk items and superblock system chunks.
- Validate extent-buffer owner compatibility and expected first-key/level parent checks.

## Key APIs
- Leaf/node checks: `__btrfs_check_leaf()`, `btrfs_check_leaf()`, `__btrfs_check_node()`, `btrfs_check_node()`.
- Chunk check: `btrfs_check_chunk_valid()`.
- Parent/owner checks: `btrfs_check_eb_owner()`, `btrfs_verify_level_key()`.
- Dispatcher: `check_leaf_item()`.
- Major validators: `check_extent_data_item()`, `check_csum_item()`, `check_dir_item()`, `check_block_group_item()`, `check_leaf_chunk_item()`, `check_dev_item()`, `check_inode_item()`, `check_root_item()`, `check_extent_item()`, `check_extent_data_ref()`, `check_inode_ref()`, `check_inode_extref()`, `check_raid_stripe_extent()`, `check_remap_key()`, `check_dev_extent_item()`, free-space item validators.

## Important Behavior
File extent checks validate offset alignment, previous inode key consistency for fs trees, minimal item size, extent type, compression/encryption fields, inline extent rules, fixed size for regular/prealloc extents, sector alignment of disk/ram/offset/length fields, extent-end overflow, and overlap with the previous file extent in the same leaf.

Directory and inode-reference checks validate previous inode grouping, location-key type/range, file type, xattr consistency, name/data length bounds, item boundary containment, and hash match for dir/xattr items.

Block-group checks validate nonzero length, v1/v2 item size depending on remap-tree feature, chunk objectid/global-root id, used bytes, profile/type flags, remap feature gating, remap byte bounds, and identity remap count.

Chunk validation checks logical/length/sectorsize alignment, stripe length, chunk length upper bound, known type/profile flags, exactly one profile bit, required data/metadata/system type, mixed-group rules, remap feature gating, stripe count/sub-stripe rules, copy/parity constraints, and works both for leaf chunks and superblock sys-chunk array chunks.

Extent item checks validate skinny metadata feature gating, bytenr alignment, tree level, item size, generation, data/tree-block flag exclusivity, tree/data length rules, inline ref boundaries, ref type ordering, per-type sequence ordering, data-ref root/objectid/offset/count, shared-ref alignment/count, no padding, inline ref count not exceeding total refs, and overlap with previous extent items.

Whole-leaf validation requires level 0, written flag, valid non-empty roots for specific tree owners, globally increasing keys, tightly packed item data from the end of the leaf, item data within leaf bounds, no item/data overlap, and per-key item validation. Whole-node validation requires written flag, level in `[1, BTRFS_MAX_LEVEL)`, valid pointer count, nonzero aligned child block pointers, and increasing child keys.

`btrfs_check_eb_owner()` skips dummy tests, unknown owner `0`, log trees, and reloc trees. For non-subvolume trees, owner must match exactly; for subvolume trees, the extent buffer owner must also be a subvolume-tree id.

`btrfs_verify_level_key()` verifies expected level, optionally verifies first key for disk-read blocks whose generation is not newer than the last committed transaction, and rejects empty blocks when a first-key check is requested.

## Risks
Checker rules must be strict enough to reject fuzzed/corrupt images but not so strict that valid historical or feature-specific filesystems fail to mount. Feature-gated checks for remap tree, extent-tree v2, skinny metadata, simple quota, raid stripe tree, mixed groups, and read-only inode flags are especially sensitive.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.h

## Summary
Declares Btrfs tree-checker status codes, parent-check input structure, valid block-group flag mask, and exported checker APIs.

## Main Responsibilities
- Define `struct btrfs_tree_parent_check` for owner/transid/first-key/level validation.
- Define `enum btrfs_tree_block_status` for clean and specific corruption classes.
- Define `BTRFS_BLOCK_GROUP_VALID` as the accepted block-group type/profile/remapped flag mask.
- Export leaf/node, chunk, owner, and parent key/level checker functions.

## Key APIs
- `__btrfs_check_leaf()` and `__btrfs_check_node()` return detailed `btrfs_tree_block_status` values.
- `btrfs_check_leaf()` and `btrfs_check_node()` wrap detailed checks as `0` or `-EUCLEAN`.
- `btrfs_check_chunk_valid()` validates chunk structures from either leaves or superblock sys-chunk arrays.
- `btrfs_check_eb_owner()` validates tree block owner compatibility.
- `btrfs_verify_level_key()` validates parent-provided level and optional first-key expectations.

## Important Behavior
`btrfs_tree_parent_check` allows owner and transid checks to be skipped with zero values, but documents that transid skipping should be limited to paths such as backref walking. `has_first_key` explicitly controls whether first-key matching is required.

The status enum separates structural failures such as invalid item counts, parent key mismatch, bad key order, invalid level/free space/offsets/block pointers/items/owner, and missing written flag.

## Risks
The header is part of the interface used by disk I/O, metadata validation, and btrfs-progs-compatible status reporting. Any enum or API behavior change can affect both kernel validation paths and users of detailed checker status codes.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.h -->