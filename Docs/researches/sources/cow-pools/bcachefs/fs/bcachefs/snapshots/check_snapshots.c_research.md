# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/check_snapshots.c

This file implements snapshot and snapshot-tree fsck/recovery validation. It repairs links among snapshot nodes, snapshot tree records, subvolumes, skiplist/depth fields, and snapshot-tagged btree keys.

Major operations:
- Ensures in-memory snapshot table capacity with `bch2_snapshot_table_make_room()`.
- Creates replacement snapshot-tree records via `bch2_snapshot_tree_create()`.
- Finds a usable master subvolume for a snapshot tree with:
  - `bch2_snapshot_oldest_subvol()`
  - `bch2_snapshot_tree_master_subvol()`
- Validates each `snapshot_tree` key in `check_snapshot_tree()`:
  - root snapshot must exist
  - root snapshot must be the actual root
  - snapshot must point back to the tree
  - master subvolume must exist, be in the same snapshot tree, and not itself be a snapshot subvolume
  - invalid tree records can be deleted or repaired
- Public pass `bch2_check_snapshot_trees()` scans `BTREE_ID_snapshot_trees`.
- Validates each snapshot key in `check_snapshot()`:
  - parent exists and points back to child
  - children exist and point back to parent
  - `BCH_SNAPSHOT_SUBVOL` flag matches subvolume linkage
  - snapshot-tree pointer is valid or repairable
  - depth field matches parent depth
  - skiplist entries are valid ancestors and sorted after repair
- Public passes:
  - `bch2_check_snapshots_trans()`
  - `bch2_check_snapshots()`
- Reconstructs missing snapshot nodes from snapshot-bearing keys:
  - groups snapshot IDs by affected btree object
  - only reconstructs singleton missing nodes
  - creates missing `snapshot_tree` records as needed
- Validates snapshot IDs on arbitrary keys with `__bch2_check_key_has_snapshot()`:
  - keys in deleted snapshots are auto-fixable deletion candidates
  - keys in missing snapshots may require additional recovery passes before deletion is offered

Important invariants:
- Snapshot IDs decrease from parent to child; validation relies on this ordering.
- Snapshot depth repair iterates snapshots in reverse so parent depths are already correct.
- Tree pointer repair anchors on the computed root snapshot.
- Missing snapshot deletion is conservative and gated by required recovery passes.

Dependencies:
- Btree iteration/update APIs.
- Snapshot and subvolume lookup helpers.
- Fsck error framework and recovery pass scheduling.
- `snapshot_id_list` darrays.

Research notes:
- This file is the consistency safety net for the snapshot subsystem.
- It distinguishes “missing because deleted” from “missing and unknown,” preventing aggressive key deletion before reconstruction/check passes run.
