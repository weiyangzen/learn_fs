# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_types.h

In-memory disk group type declarations.

Defines:
- `struct bch_disk_group_cpu` with deletion state, parent ID, fixed label, and accumulated device mask.
- `struct bch_disk_groups_cpu` with RCU header, entry count, and flexible array of CPU group entries.

Purpose:
- Provides the live RCU-safe representation used by target resolution and allocator device filtering.
- CPU entries are derived from superblock disk-group metadata and include transitive device membership masks.
