# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/disk_groups_format.h

On-disk disk group format.

Defines:
- `BCH_SB_LABEL_SIZE` as 32 bytes.
- `struct bch_disk_group`, containing fixed-size label and two 64-bit flag words.
- Bitfields:
  - `BCH_GROUP_DELETED`
  - `BCH_GROUP_DATA_ALLOWED`
  - `BCH_GROUP_PARENT`
- `struct bch_sb_field_disk_groups`, a variable-length superblock field of disk group entries.

Purpose:
- Stores hierarchical disk labels/groups inside the bcachefs superblock.
- Parent field is 1-based in user-facing group references, matching logic in `disk_groups.c`.
