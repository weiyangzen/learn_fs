# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/disk_groups_format.h

On-disk disk group format header.

Defines:
- `BCH_SB_LABEL_SIZE` as 32 bytes.
- `struct bch_disk_group`, containing a fixed-size label and two 64-bit flag words.
- Bitfields:
  - `BCH_GROUP_DELETED`
  - `BCH_GROUP_DATA_ALLOWED`
  - `BCH_GROUP_PARENT`
- `struct bch_sb_field_disk_groups`, a variable-length superblock field containing disk group entries.

Purpose:
- Stores hierarchical disk labels/groups in the bcachefs superblock.
- Parent IDs are stored as 1-based values; callers convert by subtracting or adding one when walking group paths.
