# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.h

This header exposes snapshot and snapshot-tree bkey operations, in-memory lookup helpers, traversal macros, list helpers, fsck/recovery entry points, overwrite queries, deletion entry points, and subsystem init/exit APIs.

Key exported bkey operation structures:
- `bch2_bkey_ops_snapshot_tree`
- `bch2_bkey_ops_snapshot`

Core inline helpers:
- `__snapshot_t()` maps snapshot ID to table slot with `U32_MAX - id`.
- `snapshot_t()` RCU-loads from `c->snapshots.table`.
- `bch2_snapshot_tree()` returns tree ID.
- `bch2_snapshots_same_tree()` compares table tree IDs.
- `bch2_snapshot_parent*()` returns parent ID, with debug depth sanity checks.
- `bch2_snapshot_nth_parent()` walks ancestors.
- `bch2_snapshot_root()` finds root.
- `bch2_snapshot_id_state()` distinguishes empty/live/deleted.
- `bch2_snapshot_exists()` checks live state.
- `bch2_snapshot_is_leaf()` and `bch2_snapshot_is_internal_node()` classify nodes.
- `bch2_snapshot_live_descendent()` follows `NO_KEYS` interior nodes to the surviving live descendant.

Traversal and list utilities:
- `__for_each_snapshot_child`
- `for_each_snapshot_child`
- `snapshot_list_has_id()`
- `snapshot_list_has_ancestor()`
- `snapshot_list_add()`
- `snapshot_list_add_nodup()`
- `snapshot_list_merge()`

Public operations:
- Lookup:
  - `bch2_snapshot_lookup()`
  - `bch2_snapshot_get_subvol()`
- Creation:
  - `bch2_snapshot_node_create()`
- Checking/reconstruction:
  - `bch2_check_snapshot_trees()`
  - `bch2_check_snapshots_trans()`
  - `bch2_check_snapshots()`
  - `bch2_reconstruct_snapshots()`
- Snapshot-aware key validation:
  - `bch2_check_key_has_snapshot()`
- Overwrite tracking:
  - `bch2_get_snapshot_overwrites()`
  - `bch2_key_has_snapshot_overwrites()`
- Deletion:
  - `bch2_snapshot_node_set_deleted()`
  - `bch2_delete_dead_snapshots*()`
  - `bch2_delete_dead_interior_snapshots()`
- Lifecycle:
  - `bch2_snapshots_read()`
  - `bch2_fs_snapshots_exit()`
  - `bch2_fs_snapshots_init_early()`

Important invariants:
- `bch2_snapshot_is_ancestor()` rejects zero IDs with `EBUG_ON`.
- Fast overwrite checks skip non-snapshot-aware btrees and leaf snapshots.
- `SNAPSHOT_ID_deleted` is distinct from missing/empty, which is important for fsck decisions.

Research notes:
- This header forms the main contract used by snapshot, subvolume, fsck, and btree iterator code.
- Many helpers are inline because snapshot ancestry checks are on hot lookup paths.
