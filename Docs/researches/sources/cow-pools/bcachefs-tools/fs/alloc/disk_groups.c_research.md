# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.c

Implements disk group superblock validation, RCU CPU representation construction, target resolution, disk-group path manipulation, option parsing, and text rendering.

Key responsibilities:
- Validate `BCH_SB_FIELD_disk_groups`:
  - Device group indexes must exist.
  - Devices may not reference deleted groups.
  - Non-deleted labels must be nonempty.
  - Sibling labels under the same parent must be unique.
- Build `struct bch_disk_groups_cpu` from the on-disk superblock field.
- Populate each CPU disk group with the transitive mask of devices in that group and its descendants.
- Resolve allocation targets:
  - `TARGET_NULL` means no target mask.
  - `TARGET_DEV` maps to one device.
  - `TARGET_GROUP` maps to the disk group’s device mask.
- Parse dotted group paths, find existing path components, or create missing components in the superblock.
- Assign devices to groups and persist the superblock.
- Parse target mount/options strings as `none`, device names, or disk group paths.
- Render targets and disk paths from either live filesystem state or raw superblock state.

Important APIs:
- `bch2_sb_disk_groups_to_cpu()`
- `bch2_target_to_mask()`
- `bch2_dev_in_target_rcu()`
- `bch2_disk_path_find()`
- `bch2_disk_path_find_or_create()`
- `__bch2_dev_group_set()` / `bch2_dev_group_set()`
- `bch2_opt_target_parse()`
- `bch2_target_to_text()` / `bch2_opt_target_to_text()`

Concurrency:
- Superblock mutation requires `c->sb_lock`.
- Live group lookup uses RCU through `c->disk_groups`.
- `bch2_dev_group_set()` marks reconcile scanning before and after changing group membership, uses `PF_MEMALLOC_NOFS`, writes the superblock, and refreshes CPU group state.

Dependencies:
- Superblock member helpers, superblock field resize/write helpers, device lookup, reconcile work marking, RCU device iteration, and Linux `sort`.
