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
