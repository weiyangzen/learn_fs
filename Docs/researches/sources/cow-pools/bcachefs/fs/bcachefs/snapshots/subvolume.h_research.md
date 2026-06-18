# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.h

This header exposes the subvolume API and bkey ops.

Main exports:
- Fsck/checks:
  - `bch2_check_subvols()`
  - `bch2_check_subvol_children()`
- Bkey operations:
  - `bch2_subvolume_validate()`
  - `bch2_subvolume_to_text()`
  - `bch2_subvolume_trigger()`
  - `bch2_bkey_ops_subvolume`
- Lookup:
  - `bch2_subvol_has_children()`
  - `bch2_subvolume_get()`
  - `bch2_subvolume_get_snapshot()`
- Read-only checks:
  - `bch2_subvol_is_ro_trans()`
  - `bch2_subvol_is_ro()`
- Iteration helpers:
  - `bch2_btree_iter_peek_in_subvolume_max_type()`
  - `for_each_btree_key_in_subvolume_max_continue`
  - `for_each_btree_key_in_subvolume_max`
- Lifecycle:
  - `bch2_subvolume_unlink()`
  - `bch2_subvolume_create()`
  - `bch2_initialize_subvolumes()`
  - `bch2_fs_upgrade_for_subvolumes()`
  - `bch2_fs_subvolumes_init_early()`

Important behavior:
- Subvolume iteration helpers translate subvolume ID to snapshot ID and then set the btree iterator snapshot.
- `bch2_bkey_ops_subvolume` uses a minimum value size of 16 bytes for backward-compatible decoding.

Research notes:
- This header is the bridge between VFS-facing subvolume operations and snapshot-aware btree iteration.
