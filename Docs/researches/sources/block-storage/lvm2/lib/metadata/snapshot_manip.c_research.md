# File Research: sources/block-storage/lvm2/lib/metadata/snapshot_manip.c

This file implements classic LVM snapshot metadata manipulation: identifying origins and COW volumes, sizing COW storage, creating/removing snapshot metadata segments, managing merge state, visibility rules, and validating snapshot origins.

Core functions:
- `lv_is_origin()` returns whether an LV has snapshots.
- `lv_is_cow()` identifies classic COW snapshot volumes while avoiding confusion with thin merging origins.
- `find_cow()`, `find_snapshot()`, and `origin_from_cow()` navigate snapshot relationships.
- `cow_max_extents()` and `cow_has_min_chunks()` enforce COW size limits and minimum snapshot size.
- `lv_is_cow_covering_origin()` checks whether a COW LV is large enough to cover its origin.
- `lv_is_visible()` applies LVM snapshot visibility rules, hiding snapshot wrapper LVs and merging COWs while exposing virtual origins where appropriate.
- `init_snapshot_seg()` links origin, COW, and snapshot segment metadata, hides the COW, increments origin count, marks virtual origin status where needed, and optionally initializes merge state.
- `init_snapshot_merge()` and `clear_snapshot_merge()` manage snapshot-merge metadata flags and visibility changes.
- `vg_add_snapshot()` creates the internal snapshot LV and attaches the COW/origin relationship.
- `vg_remove_snapshot()` removes snapshot metadata, deactivates virtual origins when needed, updates/commits VG metadata, suspends/resumes active origins, and reactivates the COW.
- `validate_snapshot_origin()` rejects unsupported origins such as COWs, locked/pvmove/hidden volumes, merging origins, cache/thin pool internals, mirror subvolumes, RAID subvolumes, and RAID-with-integrity under cache/writecache wrappers.

Sizing behavior:
- `_cow_max_size()` models classic snapshot disk layout: header chunk, metadata chunks, and data chunks for origin chunks.
- `_cow_extra_chunks()` adds extra space for kernels without `SNAPSHOT_FEATURE_FIXED_LEAK`; kernels with the fixed leak feature do not need the extra allowance.
- Minimum COW size is `SNAPSHOT_MIN_CHUNKS` chunks.

Operational notes:
- Snapshot wrapper LVs are virtual and generally invisible; COW LVs are hidden while attached and made visible after removal.
- Snapshot merge uses both segment status and origin status `MERGING`; thin snapshot merge has special handling through `merge_lv`.
- Snapshot removal is careful around active origins: it writes metadata, suspends active origins, commits, activates the COW if necessary, and resumes the origin.
