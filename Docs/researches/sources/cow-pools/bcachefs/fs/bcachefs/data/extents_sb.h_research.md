# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.h

## Role

`extents_sb.h` declares the extent-entry-size superblock conversion and operation table.

## API

- `bch2_sb_extent_type_u64s_to_cpu(struct bch_fs *)`
- `bch2_sb_extent_type_u64s_from_cpu(struct bch_fs *)`
- `bch_sb_field_ops_extent_type_u64s`

## Use

Included by superblock I/O and mount/update paths that need to parse, validate, or emit extent-entry size metadata.
