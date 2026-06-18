# File Research: sources/cow-pools/bcachefs-tools/fs/init/passes_format.h

Canonical recovery-pass declaration file and on-disk format definitions.

Key contents:
- Defines pass behavior flags:
  - `PASS_SILENT`
  - `PASS_FSCK`
  - `PASS_UNCLEAN`
  - `PASS_ALWAYS`
  - `PASS_ONLINE`
  - `PASS_ALLOC`
  - `PASS_NODEFER`
  - `PASS_FSCK_ALLOC`
  - `PASS_FSCK_DEBUG`
- Defines `BCH_RECOVERY_PASSES()` as the single ordered x-macro source for:
  - In-memory enum order.
  - Stable persistent IDs.
  - Execution flags.
  - Dependency masks.
  - Human-readable descriptions.
- The macro explicitly warns that passes may be reordered, but the second field is a persistent ID and must never change.
- Recovery pass list includes:
  - Topology and btree scanning: `scan_for_btree_nodes`, `check_topology`.
  - Accounting/allocator bootstrap: `accounting_read`, `alloc_read`, `check_allocations`, `trans_mark_dev_sbs`, `fs_journal_alloc`, `set_may_go_rw`, `journal_replay`.
  - Allocation consistency: `check_alloc_info`, `check_lrus`, `check_btree_backpointers`, `check_backpointers_to_extents`, `check_extents_to_backpointers`, `check_alloc_to_lru_refs`, `fs_freespace_init`, `bucket_gens_init`.
  - Snapshot/subvolume repair: `reconstruct_snapshots`, `delete_dead_interior_snapshots`, `check_snapshot_trees`, `check_snapshots`, `check_subvols`, `check_subvol_children`, `delete_dead_snapshots`, `fs_upgrade_for_subvolumes`.
  - File metadata fsck: `check_inodes`, `check_extents`, `check_indirect_extents`, `check_dirents`, `check_xattrs`, `check_root`, `check_unreachable_inodes`, `check_subvolume_structure`, `check_directory_structure`, `check_nlinks`.
  - Reconcile/logged/background work: `check_reconcile_work`, `resume_logged_ops`, `delete_dead_inodes`.
  - One-time/migration/maintenance passes: `kill_i_generation_keys`, `fix_reflink_p`, `set_fs_needs_reconcile`, `btree_bitmap_gc`, `lookup_root_inode`.
- Defines `enum bch_recovery_pass` from current ordered passes.
- Defines `enum bch_recovery_pass_stable` from stable pass IDs.
- Defines persistent metadata:
  - `struct recovery_pass_entry` with `last_run`, `last_runtime`, and `flags`.
  - `BCH_RECOVERY_PASS_NO_RATELIMIT` bit in entry flags.
  - `struct bch_sb_field_recovery_passes`.
  - `recovery_passes_nr_entries()` helper.

Role:
- This file is the recovery-pass schema: changing it affects mount/recovery ordering and persistent superblock interpretation.
- Descriptions are detailed enough to serve as operator-facing or documentation text for what each pass repairs/checks.
