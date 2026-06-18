# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/format.h

This header defines persistent snapshot and subvolume key formats.

Subvolume format:
- `SUBVOL_POS_MIN`, `SUBVOL_POS_MAX` define valid key range.
- `BCACHEFS_ROOT_SUBVOL` is subvolume ID 1.
- `struct bch_subvolume` contains:
  - flags
  - snapshot ID
  - root inode
  - snapshot creation parent
  - filesystem path parent
  - creation time
- Subvolume flags:
  - read-only
  - is snapshot
  - unlinked

Snapshot format:
- `struct bch_snapshot` contains:
  - flags
  - parent
  - two child slots
  - associated subvolume
  - snapshot tree ID
  - depth
  - three skiplist entries
  - birth time
- Snapshot flags:
  - `WILL_DELETE`
  - `SUBVOL`
  - `DELETED`
  - `NO_KEYS`

Snapshot tree format:
- `struct bch_snapshot_tree` records:
  - master subvolume
  - root snapshot

Important design notes embedded in comments:
- Snapshot trees and subvolume creation trees are separate.
- Deleted snapshot keys may remain as explicit deleted markers to distinguish known-deleted IDs from unknown missing IDs.
- `NO_KEYS` exists because runtime interior-node removal cannot update tree metadata atomically.
- Comments explicitly warn that snapshot deletion should be cross-checked with subvolume state because incorrect deletion has high blast radius.

Research notes:
- This file is the on-disk ABI for snapshot/subvolume metadata.
- The flags here directly control recovery and deletion behavior in `check_snapshots.c`, `snapshot.c`, `subvolume.c`, and `delete.c`.
