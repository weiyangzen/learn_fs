# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_types.h

In-memory disk group type declarations.

Defines:
- `struct bch_disk_group_cpu`:
  - deletion flag
  - parent group ID
  - fixed label
  - accumulated device mask
- `struct bch_disk_groups_cpu`:
  - RCU header
  - number of entries
  - flexible array of CPU group entries

Purpose:
- Provides RCU-safe live group lookup and target mask resolution derived from superblock disk group metadata.
