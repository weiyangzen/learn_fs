# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups.h

Public disk group and allocation target header.

Defines:
- `disk_groups_nr()` for deriving the number of variable-length disk group entries from a superblock field.
- `struct target` with `TARGET_NULL`, `TARGET_DEV`, and `TARGET_GROUP`.
- Target encoding constants `TARGET_DEV_START` and `TARGET_GROUP_START`.
- `dev_to_target()`, `group_to_target()`, and `target_decode()`.
- `target_rw_devs()` to intersect allocator RW device masks with a target mask.
- `bch2_target_accepts_data()` to test whether a target can accept a data type.
- `bch2_dev_in_target()` wrapper around the RCU-aware implementation.

Exports:
- Disk path lookup/create/text helpers.
- Target parse/text option helpers through `bch2_opt_target`.
- Disk group superblock-to-CPU conversion.
- Device group assignment functions.
- Disk group diagnostic text.

Role:
- Foreground allocation uses target helpers to restrict candidate devices by mount option, device label, disk group, or data type.
