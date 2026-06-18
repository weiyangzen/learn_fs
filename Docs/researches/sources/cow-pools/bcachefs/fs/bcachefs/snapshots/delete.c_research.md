# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/delete.c

This file implements asynchronous snapshot cleanup and deferred deletion of dead snapshot nodes.

Conceptual model:
- Dead leaf snapshot: no children and no subvolume points to it.
- Redundant interior snapshot: one live child, no subvolume, and keys can be moved to the child.
- Interior node physical removal is deferred because depth/skiplist updates across a subtree are not safely atomic during normal runtime.

Major APIs:
- `bch2_snapshot_delete_status_to_text()` prints running deletion status and worker backtrace.
- `bch2_snapshot_node_set_deleted()` marks a snapshot leaf for cleanup:
  - sets `WILL_DELETE`
  - clears `SUBVOL`
  - clears `subvol`
- `bch2_snapshot_node_set_no_keys()` marks interior nodes whose keys have been removed/moved.
- `bch2_snapshot_node_delete()` physically removes a snapshot node or marks it deleted depending on metadata-version support.
- `__bch2_delete_dead_snapshots()` runs the deletion worker under `snapshot_delete.lock`.
- `bch2_delete_dead_snapshots()` respects `auto_snapshot_deletion`.
- `bch2_delete_dead_snapshots_async()` queues background work with write-reference protection.
- `bch2_delete_dead_interior_snapshots()` removes `NO_KEYS` interior nodes during recovery.
- `bch2_check_snapshot_needs_deletion()` marks the filesystem as needing cleanup when it sees `WILL_DELETE`, redundant interior nodes, or `NO_KEYS`.

Deletion flow:
- `check_should_delete_snapshot()` builds deletion sets:
  - `deleting_from_trees`
  - `delete_leaves`
  - `delete_interior`
  - `no_keys`
- `eytzinger_delete_list` is built from leaves and interior deletes for fast repeated membership checks.
- Snapshot-aware btrees are scanned and keys in dying snapshots are processed:
  - leaf snapshot keys are deleted
  - interior snapshot keys may be copied to the surviving child if not already overwritten
- Runtime deletion physically deletes leaves.
- Runtime deletion marks interior nodes `NO_KEYS`.
- Recovery later adjusts child depths/skiplists and physically deletes empty interior nodes.

Important paths:
- `delete_dead_snapshot_keys_v1()` scans all snapshot-aware btrees.
- `delete_dead_snapshot_keys_v2()` accelerates cleanup by scanning inodes first and then scanning extents/dirents/xattrs only for affected inode ranges.
- `skip_unrelated_snapshot_tree()` avoids scanning unrelated snapshot trees.
- `bch2_fix_child_of_deleted_snapshot()` repairs depth and skiplist fields before recovery-time interior deletion.

Important invariants:
- A snapshot node with two children cannot be deleted directly.
- Runtime physical deletion of interior nodes is rejected.
- Parent child pointers are normalized after mutation.
- Deleting the root updates or deletes the corresponding `snapshot_tree`.
- Delete progress state is protected separately from the main delete lock.

Research notes:
- This is one of the highest-risk paths in the group because it can delete large amounts of data-bearing metadata.
- The implementation is conservative: runtime handles key removal, recovery handles structural tree surgery.
