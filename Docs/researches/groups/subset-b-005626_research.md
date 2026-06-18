# Research Group: subset-b-005626

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/qgroup-tests.c -->
## sources/distributed-fs/ceph-client/fs/btrfs/tests/qgroup-tests.c

### Purpose
`qgroup-tests.c` is a Btrfs selftest for quota group accounting over tree block references. It builds a dummy filesystem, installs dummy extent, quota, and fs roots, then mutates extent-tree backrefs so `btrfs_find_all_roots()` and `btrfs_qgroup_account_extent()` can be checked without running the full delayed-ref machinery.

### Important APIs, Types, And Functions
The file is centered on helper functions that synthesize extent-tree records: `insert_normal_tree_ref()` creates a `BTRFS_EXTENT_ITEM_KEY` with one inline tree block ref, using either `BTRFS_TREE_BLOCK_REF_KEY` for direct root ownership or `BTRFS_SHARED_BLOCK_REF_KEY` for parent references. `add_tree_ref()` increments `btrfs_extent_refs()` and inserts a separate keyed tree ref item. `remove_extent_item()` deletes the main extent item, while `remove_extent_ref()` decrements its reference count and deletes the matching keyed backref.

The two scenario tests are `test_no_shared_qgroup()` and `test_multiple_refs()`. The public test entry point is `btrfs_test_qgroups(u32 sectorsize, u32 nodesize)`.

### Control Flow
`btrfs_test_qgroups()` allocates `btrfs_fs_info`, a dummy root used as the extent root, a leaf `extent_buffer`, and two dummy fs roots (`BTRFS_FS_TREE_OBJECTID` and `BTRFS_FIRST_FREE_OBJECTID`). It marks quota enabled and maps `tree_root`, `quota_root`, and `fs_root` to satisfy code paths used by backref and qgroup helpers.

Each test captures old owners by initializing a `btrfs_backref_walk_ctx`, calling `btrfs_find_all_roots()`, mutating extent refs, calling `btrfs_find_all_roots()` again, and passing both ulist sets to `btrfs_qgroup_account_extent()`. It then validates expected referenced and exclusive byte counts with `btrfs_verify_qgroup_counts()`. `test_no_shared_qgroup()` covers add and remove of one unshared tree block. `test_multiple_refs()` adds a second root reference to the same extent, verifies both qgroups become referenced but not exclusive, removes one reference, and verifies exclusivity returns to the remaining owner.

### State And Persistence Behavior
All state is in dummy in-memory Btrfs structures. The test writes leaf items through normal Btrfs item helpers, but no disk persistence occurs. Qgroup accounting state is stored in the dummy `fs_info` quota structures. Ownership state is represented by extent items, inline refs, keyed refs, and root records inserted in the dummy fs root index.

### Dependencies And Integration Points
The test exercises code from `transaction.h`, `disk-io.h`, `qgroup.h`, `backref.h`, `fs.h`, and accessor helpers. It depends on dummy test allocation helpers from `btrfs-tests.h`, root indexing through `btrfs_insert_fs_root()`, backref walking through `btrfs_find_all_roots()`, and qgroup accounting through `btrfs_qgroup_account_extent()`.

### Risks And Edge Cases
The test deliberately bypasses delayed refs and calls qgroup accounting directly, so it validates the accounting function under controlled roots rather than the full transaction commit path. Reference manipulation must keep the extent item reference count and keyed refs consistent, or later backref walking will report false failures. The test avoids bytenr 0 because the backref code treats it specially. A subtle behavior is that `btrfs_qgroup_account_extent()` owns and frees the old/new ulist inputs, so callers clear local pointers after success.

### Test Signals
Failures are surfaced through `test_err()` and negative errno returns. Positive signals are exact qgroup count checks: unshared add gives referenced and exclusive `nodesize`, deletion returns both to zero, shared refs remove exclusivity from both qgroups, and removing one shared ref returns exclusive ownership to the remaining root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/qgroup-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/raid-stripe-tree-tests.c -->
## sources/distributed-fs/ceph-client/fs/btrfs/tests/raid-stripe-tree-tests.c

### Purpose
`raid-stripe-tree-tests.c` is a Btrfs selftest suite for the RAID stripe tree feature. It verifies that RAID stripe extents can be inserted, looked up, overwritten, truncated, punched, and deleted while preserving logical-to-physical stripe mappings for a two-device RAID1 test layout.

### Important APIs, Types, And Functions
The suite uses `struct btrfs_io_context` plus per-device `struct btrfs_io_stripe` entries as input to `btrfs_insert_one_raid_extent()`. It checks mappings through `btrfs_get_raid_extent_offset()` and removes ranges through `btrfs_delete_raid_extent()`. `btrfs_device_by_devid()` is a local lookup helper over `fs_devices->devices`.

Scenario functions cover one behavior each: `test_simple_create_delete()`, `test_create_update_delete()`, `test_tail_delete()`, `test_front_delete()`, `test_front_delete_prev_item()`, `test_punch_hole()`, `test_punch_hole_3extents()`, and `test_delete_two_extents()`. `run_test()` builds an isolated dummy filesystem and transaction for each scenario, and `btrfs_test_raid_stripe_tree()` runs the scenario table.

### Control Flow
Each scenario allocates a `btrfs_io_context`, fills two stripes with devices 0 and 1, chooses `RST_TEST_RAID1_TYPE`, and inserts one or more logical ranges. Lookups select device 0 and assert the physical address and returned length. Deletion scenarios then call `btrfs_delete_raid_extent()` over exact, front, tail, middle, or cross-item ranges, followed by lookup assertions for retained fragments and `-ENODATA` assertions for holes.

`run_test()` allocates a dummy fs, creates a dummy stripe root with `BTRFS_FEATURE_INCOMPAT_RAID_STRIPE_TREE`, installs an empty leaf, allocates two dummy devices, initializes a dummy transaction, runs the selected scenario, and frees the dummy root and fs. This per-test isolation prevents leftover stripe extents from affecting later cases.

### State And Persistence Behavior
State is held in the dummy stripe root btree and dummy device list. The tests mutate the RAID stripe tree through production insert and delete helpers, but no disk IO is performed. Logical ranges are generally anchored at 1 MiB, with device 1 physical addresses offset by 1 GiB to make copy selection visible.

### Dependencies And Integration Points
The suite integrates with `fs.h`, `disk-io.h`, `transaction.h`, `volumes.h`, and `raid-stripe-tree.h`. It validates the RAID stripe tree implementation behind the higher-level volume mapping code, especially the contract that lookups return the correct physical address and maximum contiguous length for a requested logical offset.

### Risks And Edge Cases
The strongest coverage is around range surgery. Tests verify deletion of two complete extents while leaving a third intact; punching a hole in one extent into two fragments; punching a 2 MiB hole across three 1 MiB extents; front deletion that shifts item starts; tail deletion that shrinks length; and cross-item deletion where the deletion starts in one item and ends in the next. Because all tests use RAID1 with two devices, they do not validate RAID0/10 profile-specific stripe math. Several cases also rely on exact size constants, so future stripe tree item coalescing behavior could require careful expectation updates.

### Test Signals
The suite signals success by exact lookup behavior after every mutation: retained fragments must return expected physical offsets and lengths, deleted regions must return `-ENODATA`, and cleanup deletes remaining extents. `btrfs_test_raid_stripe_tree()` reports the failing function pointer with `%ps`, which is useful for locating the failed scenario in kernel selftest output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/raid-stripe-tree-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/zoned-tests.c -->
## sources/distributed-fs/ceph-client/fs/btrfs/tests/zoned-tests.c

### Purpose
`zoned-tests.c` is a table-driven Btrfs selftest for loading zoned block group allocation state from per-stripe write pointers. It focuses on `btrfs_load_block_group_by_raid_type()` behavior across SINGLE, DUP, RAID1, RAID0, and RAID10 profiles, including conventional zones, missing devices, degraded mounts, partially written stripes, and invalid write pointer layouts.

### Important APIs, Types, And Functions
The key local type is `struct load_zone_info_test_vector`, which declares raid profile, stripe count, per-stripe allocation offsets, last allocation pointer, block group length, degraded mode, expected return, and expected allocation offset. The local `struct zone_info` mirrors the fields consumed by the loader: physical, capacity, and alloc offset. `test_load_zone_info()` builds a dummy block group, chunk map, zone info array, and active bitmap, then calls `btrfs_load_block_group_by_raid_type()`.

Special sentinel offsets model device states: `WP_MISSING_DEV` for a missing device and `WP_CONVENTIONAL` for a conventional zone. `HALF_STRIPE_LEN` expresses partial-stripe progress.

### Control Flow
`btrfs_test_zoned()` allocates a dummy fs info and loops over `load_zone_info_tests[]`. Each vector sets up a chunk map with `map->type`, `map->num_stripes`, and RAID10 `sub_stripes = 2` when needed. Active bits are set for sequential zones with an allocation offset inside `ZONE_SIZE`. The test toggles the mount `DEGRADED` option based on the vector, invokes the loader, compares the returned errno with `expected_result`, and for success compares `bg->alloc_offset` with `expected_alloc_offset`.

### State And Persistence Behavior
The test is purely in memory. Persistent zoned state is modeled by zone write pointers and `last_alloc`; loader output is represented by the dummy block group's `alloc_offset`. The active bitmap models zones with outstanding sequential allocations. Mount option state is mutated on the dummy `fs_info->mount_opt` to exercise degraded recovery rules.

### Dependencies And Integration Points
The file depends on Btrfs test helpers, `space-info.h`, `volumes.h`, and `zoned.h`. It directly covers zoned integration between chunk-map RAID geometry and block group allocation recovery. The vectors encode how the zoned allocator expects mirrored profiles to agree on write pointers, striped profiles to preserve stripe order, and conventional zones to be reconciled through `last_alloc`.

### Risks And Edge Cases
Important negative cases include mismatched mirrored write pointers, partial missing devices for nonrecoverable profiles, `last_alloc` greater than the sequential write pointer, disordered RAID0 or RAID10 stripes, stripes too far apart, and too many partial writes. Positive degraded behavior is limited to RAID1-style recovery where the available mirror can define the allocation pointer. Conventional-zone cases are sensitive because the loader must infer a consistent logical allocation point from incomplete physical write-pointer data.

### Test Signals
The table intentionally expects some loader errors, and the entry point announces that error messages are expected. A vector fails only when the return code differs from `expected_result` or a successful call produces the wrong block group `alloc_offset`. This makes the file a compact regression matrix for zoned allocation recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tests/zoned-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/transaction.c -->
## sources/distributed-fs/ceph-client/fs/btrfs/transaction.c

### Purpose
`transaction.c` implements Btrfs transaction lifetime, metadata reservation, root recording, commit sequencing, snapshot creation during commit, writeback of dirty btree blocks, superblock update, abort handling, and cleanup of dead roots. It is the central coordination layer that turns many concurrent filesystem mutations into an ordered committed generation.

### Important APIs, Types, And Functions
Externally visible transaction entry points include `btrfs_start_transaction()`, `btrfs_start_transaction_fallback_global_rsv()`, `btrfs_join_transaction()`, `btrfs_join_transaction_spacecache()`, `btrfs_join_transaction_nostart()`, `btrfs_attach_transaction()`, `btrfs_attach_transaction_barrier()`, `btrfs_end_transaction()`, `btrfs_end_transaction_throttle()`, `btrfs_commit_transaction()`, `btrfs_commit_transaction_async()`, `btrfs_commit_current_transaction()`, `btrfs_wait_for_commit()`, `btrfs_transaction_blocked()`, `btrfs_record_root_in_trans()`, `btrfs_add_dropped_root()`, `btrfs_add_dead_root()`, `btrfs_clean_one_deleted_snapshot()`, and `__btrfs_abort_transaction()`.

Important internal functions include `join_transaction()`, `start_transaction()`, `record_root_in_trans()`, `wait_current_trans()`, `btrfs_trans_release_metadata()`, `__btrfs_end_transaction()`, `btrfs_write_marked_extents()`, `btrfs_write_and_wait_transaction()`, `commit_fs_roots()`, `commit_cowonly_roots()`, `switch_commit_roots()`, `create_pending_snapshot()`, `create_pending_snapshots()`, `update_super_roots()`, `cleanup_transaction()`, and `btrfs_cleanup_pending_block_groups()`.

### Control Flow
Transaction start first reserves qgroup and metadata space, optionally reserves delayed-ref and relocation-root space, then joins or creates a running transaction under `fs_info->trans_lock`. The transaction state table controls which transaction types may attach at each phase. `start_transaction()` handles freeze protection, waits for blocked current transactions when appropriate, initializes the handle, performs chunk allocation pressure work if needed, records the root in the transaction, and converts qgroup prealloc reservations to per-transaction reservations.

Ending a transaction releases metadata reservations, creates pending block groups, releases chunk metadata, drops freeze protection, uninhibits writeback, decrements writer counters, wakes commit waiters, and returns abort or read-only errors when the filesystem has failed.

Commit starts by releasing the caller's unused reservation, flushing delayed refs and dirty block groups, then transitions through `COMMIT_PREP`, `COMMIT_START`, `COMMIT_DOING`, `UNBLOCKED`, `SUPER_COMMITTED`, and `COMPLETED`. The committer waits for previous transactions, extwriters, delalloc, fsync-started ordered extents, and all other writers. In the critical section it pauses scrub, runs pending snapshots, delayed items, delayed refs, commits fs roots and cow-only roots, accounts qgroups, switches commit roots, updates super root pointers, releases the running transaction so a new one may start, writes and waits dirty btree extents, writes superblocks, finishes extent commit, updates last committed transid, removes the transaction from the list, and frees references.

### State And Persistence Behavior
In-memory transaction state lives in `struct btrfs_transaction`: writer counters, external writer counters, state, abort code, dirty pages, pinned extents, delayed refs, pending snapshots, dirty block groups, dropped roots, deleted block groups, and wait queues. Per-handle state tracks reservations, delayed refs, pending snapshots, chunk operations, relocation reservations, fsync context, and inhibited writeback extent buffers. Persistent effects include root item updates, chunk/root super fields, uuid tree updates, qgroup accounting, block group IO, dirty btree writeback, and superblock writes.

### Dependencies And Integration Points
This file connects nearly every major Btrfs subsystem: extent tree and delayed refs, qgroups, block groups and chunk allocation, root tree updates, relocation, tree log, device replace and device stats, scrub, ordered extents, delayed inodes/items, uuid tree, fscrypt names during snapshot creation, and freeze/writeback infrastructure. It also exports wait and blocked-state helpers used by throttling, transaction kthread, fsync, cleaner, and mount/unmount paths.

### Risks And Edge Cases
The riskiest areas are ordering and cleanup. Writer counters and transaction states must prevent new mutators from entering while supporting join paths needed during commit. Root recording relies on memory barriers around `BTRFS_ROOT_IN_TRANS_SETUP` and `last_trans`. Commit must not expose a new superblock before all referenced tree blocks are durably written. Snapshot creation has partial-failure semantics where some errors only fail the pending snapshot while commit-affecting errors abort the transaction. Abort cleanup must avoid use-after-free with the transaction kthread, release block group references, avoid scrub deadlock during relocation, and clear reservations consistently.

### Test Signals
Direct tests are mostly elsewhere in the Btrfs selftest suite, but this file exposes many observable failure signals: `-EROFS` for filesystem error state, `-ENOENT` for attach without a running transaction, abort errno propagation, transaction wait behavior, dirty writeback errors via `BTRFS_FS_BTREE_ERR`, and warnings/assertions for impossible state. The qgroup and RAID stripe tree tests in this subset use dummy transactions and `transaction.h` helpers but do not exercise the full commit path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/transaction.h -->
## sources/distributed-fs/ceph-client/fs/btrfs/transaction.h

### Purpose
`transaction.h` defines the public transaction data structures, state enum, transaction type flags, abort macro, inline helpers, and exported function prototypes for Btrfs transaction management. It is the contract between transaction implementation and the rest of the filesystem.

### Important APIs, Types, And Functions
`enum btrfs_trans_state` names the commit lifecycle: running, commit prep, commit start, commit doing, unblocked, super committed, completed, and max. `struct btrfs_transaction` holds the global transaction object with transid, writer counts, use count, flags, state, abort code, dirty trees, pending snapshot and device update lists, dirty and IO block group lists, dropped/deleted roots, pinned extents, delayed refs, fs info, and ordered-extents wait state.

`struct btrfs_trans_handle` is the per-task handle with reservation accounting, delayed-ref counters, pointer to the transaction, block reservation pointers, pending snapshot pointer, type, abort field, flags for csum/chunk/relocation/fsync operations, `fs_info`, new block groups, local delayed-ref reservation, and a writeback-inhibited extent-buffer xarray.

`struct btrfs_pending_snapshot` captures all state needed to create a snapshot at commit time: dentry, parent inode, source root, root item, resulting snapshot root, qgroup inheritance, path, block reservation, error, anonymous device id, readonly flag, and list node.

Inline helpers include `btrfs_set_inode_last_trans()`, `btrfs_set_skip_qgroup()`, `btrfs_clear_skip_qgroup()`, and `btrfs_abort_should_print_stack()`. The `btrfs_abort_transaction()` macro records first-abort diagnostics and calls `__btrfs_abort_transaction()`.

### Control Flow
Callers start or join transactions through the declared start/join/attach helpers, modify Btrfs trees under a returned handle, then end or commit through `btrfs_end_transaction()`, `btrfs_end_transaction_throttle()`, or `btrfs_commit_transaction()`. Snapshot callers populate `pending_snapshot` and commit moves it to the transaction list once commit prep starts. Abort callers use the macro, which sets filesystem-level abort state on first hit, decides whether to print a stack based on errno, logs the abort, and delegates to the cold implementation.

### State And Persistence Behavior
The header describes how transaction state controls persistence. `num_extwriters` must reach zero before commit can proceed into the exclusive phase, while `num_writers` must reach zero except for the committer. Dirty pages and pinned extents track metadata that must be written or finalized. `pending_ordered` represents fast-fsync ordered extents that commit must wait on to preserve logged data. The qgroup skip helper mutates delayed-ref root state so snapshot qgroup accounting can omit a newly created qgroup until inheritance accounts it.

### Dependencies And Integration Points
The header depends on Linux atomics, refcounts, lists, waits, mutexes, xarrays, and Btrfs inode and delayed-ref definitions. Its prototypes are used by tree modification code, root management, qgroups, block groups, transaction kthread code, scrub/relocation, fsync/log code, and selftests.

### Risks And Edge Cases
The `aborted` fields are intentionally lockless and must be read with `READ_ONCE()` through `TRANS_ABORTED()`. Transaction type flags are bit encodings used by `transaction.c` state gating, so adding a type requires updating blocked-state logic. The abort macro can print a stack only for errors likely to indicate bugs, while common external failures such as `-EIO`, `-EROFS`, and `-ENOMEM` avoid noisy warnings.

### Test Signals
The header itself is not tested directly, but compile-time and selftest coverage validates structure fields and prototypes. Many Btrfs tests create dummy `struct btrfs_trans_handle` values through `btrfs_init_dummy_trans()` and rely on these definitions for qgroup, raid stripe tree, and tree mutation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/transaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.c -->
## sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.c

### Purpose
`tree-checker.c` validates Btrfs tree blocks after read and before higher-level code trusts their contents. It detects corrupt leaves, nodes, malformed item payloads, invalid owners, invalid chunk geometry, and parent/first-key mismatches. The goal is to centralize defensive validation so normal tree users can assume basic on-disk invariants.

### Important APIs, Types, And Functions
The main exported validators are `btrfs_check_leaf()`, `btrfs_check_node()`, `btrfs_check_chunk_valid()`, `btrfs_check_eb_owner()`, and `btrfs_verify_level_key()`. `__btrfs_check_leaf()` and `__btrfs_check_node()` return detailed `enum btrfs_tree_block_status` values for btrfs-progs and internal callers.

Static item validators include checks for file extents, checksum items, directory items, inode refs/extrefs, block group items, chunk items, device items and extents, inode items, root items, extent items and refs, RAID stripe extents, remap keys, and free-space tree items. Error reporters such as `generic_err()`, `file_extent_err()`, `dir_item_err()`, `block_group_err()`, `chunk_err()`, `dev_item_err()`, and `extent_err()` produce structured corruption messages and dump the first extent-buffer page.

### Control Flow
`__btrfs_check_leaf()` first verifies the block is level 0, has the WRITTEN flag, and is not an invalid empty critical tree. It then walks every slot in key order, checks key ordering, verifies item data offsets are packed backwards without holes or overlap, ensures item data stays inside the leaf and does not overlap item metadata, and dispatches by key type through `check_leaf_item()`.

`__btrfs_check_node()` verifies WRITTEN, internal level range, nritems bounds, nonzero and aligned child pointers, and increasing node keys. `btrfs_check_leaf()` and `btrfs_check_node()` convert any non-clean detailed status to `-EUCLEAN`.

`btrfs_check_chunk_valid()` is shared by leaf chunk items and superblock sys chunk array validation. It decodes either leaf-backed or stack-backed chunk fields, validates stripe counts against RAID profile, logical and length alignment, sector size, stripe length, length overflow, recognized type/profile flags, mixed group rules, remap feature gates, and RAID parity/copy constraints.

### State And Persistence Behavior
The checker does not persist state. It reads on-disk structures from `extent_buffer` memory and reports corruption through Btrfs logging. It uses `fs_info` for sectorsize, nodesize, csum size, feature flags, super generation, readonly state, and last committed transaction. Some validation is intentionally feature-gated, for example remap tree, extent tree v2, skinny metadata, simple quotas, mixed block groups, and RAID stripe tree.

### Dependencies And Integration Points
This file integrates with Btrfs accessors, on-disk format definitions, compression constants, volumes and RAID metadata, file/inode/dir item helpers, extent tree helpers, and error injection. It is invoked by disk IO and tree read paths before tree blocks are accepted. `btrfs_check_eb_owner()` supports callers that know the expected root owner, while `btrfs_verify_level_key()` validates parent-driven expectations after a block is read.

### Risks And Edge Cases
The leading risk is false positives: overly strict validation can prevent mounting valid historical filesystems. The file explicitly avoids checks when fields are unreliable or not yet initialized, such as superblock sys chunks without reliable `fs_info->sectorsize`, extent tree v2 global root counts during early mount, dummy fs selftests, tree log and relocation owner semantics, and live tree blocks newer than the last committed transaction. Validation must also avoid unsafe item reads by checking sizes and boundaries before dereferencing variable-length structures.

### Test Signals
Failures return `-EUCLEAN` or detailed `BTRFS_TREE_BLOCK_*` statuses and emit corruption logs naming root, block, slot, and decoded keys. Error injection is enabled for `btrfs_check_leaf()` and `btrfs_check_node()`. The checks provide strong regression signals for fuzzed images, malformed chunks, invalid free-space tree items, overlap in extent or checksum ranges, and feature-incompatible item types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.h -->
## sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.h

### Purpose
`tree-checker.h` declares the Btrfs tree block validation interface and status vocabulary. It is the public boundary for code that reads or verifies Btrfs tree blocks, chunks, owners, and parent expectations.

### Important APIs, Types, And Functions
`struct btrfs_tree_parent_check` packages expected parent-derived facts for a tree block: owner root, expected transid, first key plus a `has_first_key` flag, and expected level. `enum btrfs_tree_block_status` distinguishes clean blocks from invalid item counts, parent keys, key ordering, levels, free-space data, offsets, block pointers, item payloads, owners, and missing WRITTEN flags.

`BTRFS_BLOCK_GROUP_VALID` defines the accepted block group type/profile/remap mask used by chunk validation. Declared functions include `__btrfs_check_leaf()`, `__btrfs_check_node()`, `btrfs_check_leaf()`, `btrfs_check_node()`, `btrfs_check_chunk_valid()`, `btrfs_check_eb_owner()`, and `btrfs_verify_level_key()`.

### Control Flow
Callers that need detailed status use the double-underscore leaf and node functions. Callers that only need errno semantics use `btrfs_check_leaf()` and `btrfs_check_node()`, which return zero or `-EUCLEAN`. Chunk validation can be called for both leaf chunk items and superblock system chunk arrays by passing an optional `extent_buffer`. Parent verification callers fill `btrfs_tree_parent_check` and call `btrfs_verify_level_key()` after reading a block.

### State And Persistence Behavior
The header itself has no state. It defines validation inputs that refer to persistent on-disk facts: root ownership, transid, level, first key, block group flags, and chunk geometry. The `owner_root`, `transid`, and `has_first_key` fields are explicitly skippable for cases such as backref walks where the parent context is incomplete.

### Dependencies And Integration Points
The header includes Linux types and the userspace Btrfs tree format header, then forward-declares `extent_buffer`, `btrfs_fs_info`, `btrfs_chunk`, and `btrfs_key`. It is consumed by disk read paths, tree navigation, backref/qgroup code, btrfs-progs shared code, and any subsystem that must validate chunks or extent-buffer ownership.

### Risks And Edge Cases
The status enum is part of a shared interface with btrfs-progs, so changes should preserve meaning for external users. Parent checks are deliberately optional in several fields; forcing them on incomplete contexts would break valid backref and root-read paths. The block group valid mask must stay aligned with new on-disk block group flags.

### Test Signals
The header enables compile-time integration checks and defines the statuses that tests and callers can assert. Functional signals come from `tree-checker.c` returning detailed enum values or `-EUCLEAN` through this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.h -->
