# File Research: sources/block-storage/util-linux/libblkid/src/partitions/ultrix.c

## Purpose
Parses Ultrix partition labels.

## Main Components
- Defines label location near byte 16384 and eight partition entries.
- Reads the sector containing the label and points into the label offset.
- Validates `pt_magic == ULTRIX_MAGIC` and `pt_valid == 1`.
- Records the magic location through `blkid_probe_set_magic()`.
- Creates an `ultrix` partition table for binary probing.
- Iterates eight entries, preserving numbers for empty entries and adding non-empty partitions from `pi_blkoff` and `pi_nblocks`.
- `ultrix_pt_idinfo` has no fixed magic descriptor and relies on custom probing.

## Dependencies and Interactions
Uses generic partition helpers and raw probe sector reads.

## Research Notes
The file comment says “uktrix”, but the implementation and exported idinfo are Ultrix.
