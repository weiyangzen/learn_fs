# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.h

## Purpose
Public declarations for the extent-entry-size superblock field support.

## Main Interfaces
- `bch2_sb_extent_type_u64s_to_cpu(struct bch_fs *)`
- `bch2_sb_extent_type_u64s_from_cpu(struct bch_fs *)`
- `bch_sb_field_ops_extent_type_u64s`

## Dependencies
Relies on `struct bch_fs` and `struct bch_sb_field_ops` declarations from broader bcachefs headers.
