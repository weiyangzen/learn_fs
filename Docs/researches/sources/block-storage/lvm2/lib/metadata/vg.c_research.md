# File Research: sources/block-storage/lvm2/lib/metadata/vg.c

This file implements allocation, lifetime, accessors, attribute rendering, extent-size mutation, limits, persistence flags, and PV removal for `struct volume_group`.

Main entry points:
- Lifetime: `alloc_vg()`, `release_vg()`, `free_orphan_vg()`.
- LV membership: `link_lv_to_vg()`, `unlink_lv_from_vg()`, `vg_max_lv_reached()`.
- Accessors/dup helpers: `vg_fmt_dup()`, `vg_name_dup()`, `vg_system_id_dup()`, `vg_lock_type_dup()`, `vg_lock_args_dup()`, `vg_uuid_dup()`, `vg_tags_dup()`, `vg_seqno()`, `vg_status()`, `vg_size()`, `vg_free()`, and count getters.
- Metadata areas: `vg_mda_count()`, `vg_mda_used_count()`, `vg_mda_copies()`, `vg_mda_size()`, `vg_mda_free()`, `vg_set_mda_copies()`.
- Mutators: `vg_check_new_extent_size()`, `vg_set_extent_size()`, `vg_set_max_lv()`, `vg_set_max_pv()`, `vg_set_alloc_policy()`, `vg_set_system_id()`, `vg_set_lock_type()`, `vg_set_persist()`.
- Reporting/operations: `vg_attr_dup()`, `vgreduce_single()`, `vg_backup_if_needed()`.

Control flow:
- `alloc_vg()` creates a VG memory pool, initializes all list heads, sets defaults, and stores the VG name.
- `release_vg()` recursively releases committed/precommitted VG copies, then destroys config trees, radix trees, and the VG pool.
- `vg_set_extent_size()` validates the new PE size, updates format setup, and recalculates VG, PV, PV segment, LV, LV segment, VDO virtual extent, and area offsets.
- `vgreduce_single()` validates the PV is unused and not the last PV, moves it to orphan state, updates VG counts, splits metadata areas, writes/commits if requested, and clears PV metadata.

Dependencies:
- Format instance operations, metadata area callbacks, radix tree name indexes, archiver backup, PV helpers, and activation persistence helpers.

Correctness notes:
- Extent-size changes require exact divisibility across every affected count and offset.
- `vg_set_max_lv()` counts only visible LVs.
- `vg_attr_dup()` encodes write/resize/export/missing/allocation/shared/persistent reservation state in report format.
- `vg_backup_if_needed()` backs up the committed VG copy, not necessarily the currently mutable in-memory copy.

Risks:
- `vg_set_extent_size()` mutates `vg->extent_size` early; failures after partial recalculation rely on caller-level error handling and VG lifetime discipline.
- `vgreduce_single()` touches both VG and orphan metadata and must clean up PV fids correctly on error or commit.
