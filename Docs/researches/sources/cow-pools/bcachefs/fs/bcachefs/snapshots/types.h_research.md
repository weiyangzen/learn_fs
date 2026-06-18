# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/types.h

This header defines in-memory snapshot subsystem data structures.

Key types:
- `snapshot_id_list`: darray of `u32` snapshot IDs.
- `IS_ANCESTOR_BITMAP`: 128 nearby ancestor bits.
- `struct snapshot_t`:
  - snapshot ID state: empty/live/deleted
  - parent
  - three skiplist entries
  - depth
  - two normalized children
  - associated subvolume ID
  - snapshot tree ID
  - nearby ancestor bitmap
- `struct snapshot_table`:
  - RCU header
  - flexible array of `snapshot_t`
- `struct snapshot_interior_delete`:
  - interior snapshot ID
  - surviving live child
- `interior_delete_list`: darray of interior delete records.
- `struct snapshot_delete`:
  - delete worker locks/state
  - running thread pointer
  - progress tracking
  - delete worklists
  - eytzinger delete list
- `struct bch_fs_snapshots`:
  - RCU snapshot table
  - table lock
  - create semaphore
  - deletion state
  - pagecache deletion work
  - unlinked-subvolume list and lock
- `subvol_inum`: packed pair of subvolume ID and inode number.

Important invariants:
- Snapshot IDs decrease down the tree.
- `children[0] >= children[1]` is the normalized form.
- RCU readers may tolerate partial ancestor-bitmap updates because they can fall back to skiplist/parent traversal.
- `subvol_inum` explicitly must not contain padding.

Research notes:
- This file captures the performance strategy for ancestry checks: skiplist, bitmap, parent walk.
