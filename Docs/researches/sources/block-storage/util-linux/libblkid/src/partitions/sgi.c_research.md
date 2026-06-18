# File Research: sources/block-storage/util-linux/libblkid/src/partitions/sgi.c

## Purpose
Parses SGI disk labels.

## Main Components
- Reads sector 0 as `struct sgi_disklabel`.
- Verifies checksum with `sgi_pt_checksum()`.
- Returns success early for type-only probing.
- Creates an `sgi` partition table.
- Iterates `SGI_MAXPARTITIONS`, skipping empty entries while preserving partition numbers.
- Adds partitions with big-endian start, size, and numeric type.
- `sgi_pt_idinfo` detects big-endian magic `0B E5 A9 41`.

## Dependencies and Interactions
Uses SGI structures/checksum from `pt-sgi.h` and generic partition-list helpers.

## Research Notes
Checksum mismatch is treated as no valid SGI label rather than a hard error.
