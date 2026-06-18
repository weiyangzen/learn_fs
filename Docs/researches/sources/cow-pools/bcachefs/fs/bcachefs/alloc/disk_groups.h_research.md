# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups.h

Public disk group and target header.

Defines:
- `disk_groups_nr()` for deriving entry count from variable-size superblock field.
- `struct target` and target encoding constants.
- `dev_to_target()`, `group_to_target()`, and `target_decode()`.
- `target_rw_devs()` to intersect allocator RW device masks with a target mask.
- `bch2_target_accepts_data()` for checking whether a target can accept a data type.

Exports:
- Disk path lookup/create/text functions.
- Target parse/text option functions via `bch2_opt_target`.
- Disk group superblock-to-CPU conversion.
- Device group assignment functions.
- Disk group debug text.

Role in allocator:
- Foreground allocation uses `target_rw_devs()` to decide eligible devices for a write’s data type and target.
