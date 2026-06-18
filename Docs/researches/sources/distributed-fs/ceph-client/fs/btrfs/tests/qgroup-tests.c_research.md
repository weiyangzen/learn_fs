# sources/distributed-fs/ceph-client/fs/btrfs/tests/qgroup-tests.c

## Purpose
`qgroup-tests.c` is a Btrfs selftest for quota group accounting over tree block references. It builds a dummy filesystem, installs dummy extent, quota, and fs roots, then mutates extent-tree backrefs so `btrfs_find_all_roots()` and `btrfs_qgroup_account_extent()` can be checked without running the full delayed-ref machinery.

## Important APIs, Types, And Functions
The file is centered on helper functions that synthesize extent-tree records: `insert_normal_tree_ref()` creates a `BTRFS_EXTENT_ITEM_KEY` with one inline tree block ref, using either `BTRFS_TREE_BLOCK_REF_KEY` for direct root ownership or `BTRFS_SHARED_BLOCK_REF_KEY` for parent references. `add_tree_ref()` increments `btrfs_extent_refs()` and inserts a separate keyed tree ref item. `remove_extent_item()` deletes the main extent item, while `remove_extent_ref()` decrements its reference count and deletes the matching keyed backref.

The two scenario tests are `test_no_shared_qgroup()` and `test_multiple_refs()`. The public test entry point is `btrfs_test_qgroups(u32 sectorsize, u32 nodesize)`.

## Control Flow
`btrfs_test_qgroups()` allocates `btrfs_fs_info`, a dummy root used as the extent root, a leaf `extent_buffer`, and two dummy fs roots (`BTRFS_FS_TREE_OBJECTID` and `BTRFS_FIRST_FREE_OBJECTID`). It marks quota enabled and maps `tree_root`, `quota_root`, and `fs_root` to satisfy code paths used by backref and qgroup helpers.

Each test captures old owners by initializing a `btrfs_backref_walk_ctx`, calling `btrfs_find_all_roots()`, mutating extent refs, calling `btrfs_find_all_roots()` again, and passing both ulist sets to `btrfs_qgroup_account_extent()`. It then validates expected referenced and exclusive byte counts with `btrfs_verify_qgroup_counts()`. `test_no_shared_qgroup()` covers add and remove of one unshared tree block. `test_multiple_refs()` adds a second root reference to the same extent, verifies both qgroups become referenced but not exclusive, removes one reference, and verifies exclusivity returns to the remaining owner.

## State And Persistence Behavior
All state is in dummy in-memory Btrfs structures. The test writes leaf items through normal Btrfs item helpers, but no disk persistence occurs. Qgroup accounting state is stored in the dummy `fs_info` quota structures. Ownership state is represented by extent items, inline refs, keyed refs, and root records inserted in the dummy fs root index.

## Dependencies And Integration Points
The test exercises code from `transaction.h`, `disk-io.h`, `qgroup.h`, `backref.h`, `fs.h`, and accessor helpers. It depends on dummy test allocation helpers from `btrfs-tests.h`, root indexing through `btrfs_insert_fs_root()`, backref walking through `btrfs_find_all_roots()`, and qgroup accounting through `btrfs_qgroup_account_extent()`.

## Risks And Edge Cases
The test deliberately bypasses delayed refs and calls qgroup accounting directly, so it validates the accounting function under controlled roots rather than the full transaction commit path. Reference manipulation must keep the extent item reference count and keyed refs consistent, or later backref walking will report false failures. The test avoids bytenr 0 because the backref code treats it specially. A subtle behavior is that `btrfs_qgroup_account_extent()` owns and frees the old/new ulist inputs, so callers clear local pointers after success.

## Test Signals
Failures are surfaced through `test_err()` and negative errno returns. Positive signals are exact qgroup count checks: unshared add gives referenced and exclusive `nodesize`, deletion returns both to zero, shared refs remove exclusivity from both qgroups, and removing one shared ref returns exclusive ownership to the remaining root.
