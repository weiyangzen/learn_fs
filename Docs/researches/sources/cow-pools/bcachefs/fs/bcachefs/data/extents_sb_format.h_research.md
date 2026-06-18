# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb_format.h

## Role

`extents_sb_format.h` defines the on-disk superblock field layout for extent entry sizes.

## Structure

`struct bch_sb_field_extent_type_u64s` contains:
- common `struct bch_sb_field field`
- flexible byte array `d[]`, where each byte stores the u64 count for the corresponding extent entry type

## Purpose

The compact byte array lets old binaries skip unknown extent entry types by reading their advertised size from the superblock field.
