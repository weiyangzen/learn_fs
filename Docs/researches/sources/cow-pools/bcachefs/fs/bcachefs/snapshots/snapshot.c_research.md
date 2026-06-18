# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.c

This file implements snapshot-tree formatting, validation, in-memory snapshot-table maintenance, ancestor queries, snapshot node creation, snapshot-aware overwrite checks, initialization, and diagnostic tree printing.

High-level snapshot design:
- Subvolumes point to snapshot IDs.
- Snapshot-aware btrees store snapshot IDs in `bpos.snapshot`.
- Snapshot visibility is ancestor-based: keys from ancestors are visible unless overwritten closer to the target snapshot.
- Snapshot creation is O(1): two child nodes are created under the current source snapshot, one for the new snapshot and one replacing the source subvolume snapshot.
- Snapshot deletion is deferred and batched.

Snapshot tree APIs:
- `bch2_snapshot_tree_to_text()`
- `bch2_snapshot_tree_validate()`
- `bch2_snapshot_tree_lookup()`
- `__bch2_snapshot_tree_create()`

Ancestor lookup:
- Early/recovery path: parent walk via `bch2_snapshot_is_ancestor_early()`.
- Fast path:
  - skiplist jumps for far ancestors
  - 128-bit in-memory ancestor bitmap for nearby ancestors
- Debug mode compares fast and slow paths and panics on mismatch with detailed traces.

In-memory table:
- `bch2_snapshot_t_mut()` grows `c->snapshots.table` with RCU replacement.
- Table index is `U32_MAX - id`, matching the design where newer/deeper IDs descend downward.
- `__bch2_mark_snapshot()` populates `snapshot_t` fields from btree keys and updates ancestor bitmap.
- `WILL_DELETE` marks the filesystem as needing snapshot deletion and may queue async cleanup.

Validation:
- `bch2_snapshot_validate()` checks:
  - key position range
  - parent ID ordering
  - normalized children
  - duplicate children
  - child ID ordering
  - normalized skiplist
  - skiplist entries not below parent

Traversal:
- `__bch2_snapshot_tree_next()` performs depth-first traversal using parent/child links.
- `bch2_snapshot_tree_next()` wraps it under RCU.

Overwrite queries:
- `__bch2_get_snapshot_overwrites()` collects ancestor snapshot IDs that overwrite a key.
- `__bch2_key_has_snapshot_overwrites()` checks whether any ancestor key exists for a position.

Creation:
- `create_snapids()` allocates new snapshot keys, initializes depth/skiplists, sets `SUBVOL`, and marks the in-memory table.
- `bch2_snapshot_node_create_children()` converts a leaf parent into an interior node with two children.
- `bch2_snapshot_node_create_tree()` creates a new snapshot tree root.
- `bch2_snapshot_node_create()` dispatches based on whether a parent exists.

Initialization and diagnostics:
- `bch2_snapshots_read()` builds the in-memory table in reverse order and schedules deletion passes if needed.
- `bch2_fs_snapshots_init_early()` initializes locks and deletion work.
- `bch2_snapshot_tree_keys_to_text()` prints a full snapshot tree with path and accounting info.

Important invariants:
- Parent IDs are greater than child IDs.
- A parent that gains children ceases to be a subvolume snapshot node.
- Snapshot table updates are RCU-visible and protected by `table_lock` during mutation.
- Ancestor bitmap updates tolerate readers observing partially updated state because slow paths remain valid.

Research notes:
- This is the core snapshot implementation file.
- The embedded documentation is unusually complete and explains the architectural difference from btrfs: bcachefs shares individual btree keys rather than cloning COW btrees.
