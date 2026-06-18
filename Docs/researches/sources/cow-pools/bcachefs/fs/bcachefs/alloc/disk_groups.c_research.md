# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.c

Implements disk group superblock validation, CPU mirror construction, target resolution, disk group path manipulation, option parsing, and display helpers.

Key responsibilities:
- Validate `BCH_SB_FIELD_disk_groups`:
  - Member group indices must exist.
  - Members cannot reference deleted groups.
  - Non-deleted labels must be non-empty.
  - Sibling labels under the same parent must be unique.
- Convert on-disk disk group entries to an RCU-protected `bch_disk_groups_cpu`.
- Populate each group’s transitive device mask by walking parent links from each alive member’s group.
- Resolve targets:
  - `TARGET_NULL` means no target restriction.
  - `TARGET_DEV` maps directly to one device.
  - `TARGET_GROUP` maps to a group’s device mask.
- Parse dotted disk paths, find or create missing path components in the superblock, and assign devices to groups.
- Parse mount/options target strings as either device names, group paths, or `none`.
- Render targets and disk paths against either live filesystem state or a raw superblock.

Important APIs:
- `bch2_sb_disk_groups_to_cpu()`
- `bch2_target_to_mask()`
- `bch2_dev_in_target_rcu()`
- `bch2_disk_path_find()`
- `bch2_disk_path_find_or_create()`
- `bch2_dev_group_set()`
- `bch2_opt_target_parse()`
- `bch2_target_to_text()`

Concurrency:
- Superblock mutations require `c->sb_lock`.
- Live disk group lookup uses RCU.
- `bch2_dev_group_set()` wraps mutation in `PF_MEMALLOC_NOFS`, writes the superblock, and marks reconcile scanning state before/after changing group membership.

Dependencies:
- Superblock member helpers, superblock IO, device lookup, reconcile work marking, RCU device iteration, and Linux `sort`.
