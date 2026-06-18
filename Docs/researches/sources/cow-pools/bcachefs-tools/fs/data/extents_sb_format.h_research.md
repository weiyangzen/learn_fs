# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_sb_format.h

## Purpose
Defines the on-disk superblock field payload for extent-entry u64 sizes.

## Main Interfaces
- `struct bch_sb_field_extent_type_u64s` embeds `struct bch_sb_field field` followed by flexible byte array `d[]`, where each byte stores the u64 length for the entry type at the same index.

## Notes
The format is intentionally compact because extent entry sizes are small and indexed by `BCH_EXTENT_ENTRY_*`.
