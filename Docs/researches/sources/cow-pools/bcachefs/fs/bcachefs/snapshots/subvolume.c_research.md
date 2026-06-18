# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.c

This file implements subvolume bkey validation, fsck repair, lookup, read-only checks, unlink/delete, creation, initial root-subvolume creation, and upgrade support.

Fsck/checking:
- `bch2_subvolume_missing()` schedules `check_inodes` recovery for missing subvolumes.
- `check_subvol()` validates:
  - referenced snapshot exists
  - unlinked subvolumes are deleted
  - root subvolume has no filesystem path parent
  - `subvolume_children` index contains required parent-child entries
  - root inode exists and has correct `bi_subvol` and `bi_snapshot`
  - missing roots can be recreated as directories for lost+found reattachment
  - non-snapshot subvolumes must be the master subvolume of their snapshot tree
- `bch2_check_subvols()` scans `BTREE_ID_subvolumes`.
- `check_subvol_child()` validates reverse child-index entries.
- `bch2_check_subvol_children()` scans `BTREE_ID_subvolume_children`.

Bkey operations:
- `bch2_subvolume_validate()` checks key position, nonzero snapshot, and nonzero inode.
- `bch2_subvolume_to_text()` prints root inode, snapshot ID, parents, and flags.
- `bch2_subvolume_trigger()` maintains the `subvolume_children` btree when `fs_path_parent` changes.

Lookup and access:
- `bch2_subvol_has_children()` reports non-empty subvolume-child state.
- `bch2_subvolume_get()` fetches cached subvolume keys.
- `bch2_subvol_is_ro_trans()` returns `-EROFS` for read-only or unlinked subvolumes.
- `bch2_snapshot_get_subvol()` maps snapshot ID to its subvolume.
- `bch2_subvolume_get_snapshot()` maps subvolume ID to snapshot ID.

Deletion/unlink:
- `bch2_subvolumes_reparent()` reparents creation-tree children before deletion.
- `__bch2_subvolume_delete()`:
  - clears snapshot-tree master if deleting the master subvolume
  - deletes the subvolume key
  - marks the snapshot node deleted
- `bch2_subvolume_unlink()`:
  - sets `UNLINKED`
  - clears `fs_path_parent`
  - registers a commit hook to evict pagecache and queue actual deletion
- `bch2_subvolume_wait_for_pagecache_and_delete()` drains unlinked subvolumes after inode eviction.

Creation:
- `bch2_subvolume_create()` allocates a new subvolume ID, creates one or two snapshot nodes, updates the source subvolume snapshot when making a snapshot, initializes the new subvolume, and sets read-only/snapshot flags.
- For normal subvolume creation, one root snapshot node is created.
- For snapshot creation, two child snapshot nodes are created under the source snapshot.

Initialization/upgrade:
- `bch2_initialize_subvolumes()` creates:
  - root snapshot tree ID 1
  - root snapshot ID `U32_MAX`
  - root subvolume ID 1
- `bch2_fs_upgrade_for_subvolumes()` sets `bi_subvol` on the root inode.
- `bch2_fs_subvolumes_init_early()` initializes delayed pagecache deletion work.

Important invariants:
- Root subvolume is ID 1 and root snapshot starts at `U32_MAX`.
- Subvolume deletion is delayed until pagecache eviction prevents stale inode references.
- `creation_parent` records snapshot creation ancestry, separate from filesystem path parent and snapshot tree parentage.
