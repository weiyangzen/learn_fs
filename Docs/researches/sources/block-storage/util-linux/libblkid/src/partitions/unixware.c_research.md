# File Research: sources/block-storage/util-linux/libblkid/src/partitions/unixware.c

## Purpose
Parses UnixWare disklabel/VTOC slice tables, typically nested inside a DOS primary partition.

## Main Components
- Defines disklabel location at sector 29 and magic offsets for idinfo matching.
- Defines UnixWare slice tags, validity flag, partition struct, disklabel struct, and embedded VTOC.
- `probe_unixware_pt()` reads sector 29, validates VTOC magic, returns early for type-only probing, obtains optional parent, creates `unixware` table, and skips slice 0 as whole-disk.
- Iterates remaining slices, skipping unused, entire-disk, and invalid-flag entries.
- Validates nested slice dimensions when a parent exists.
- Adds partitions and sets type to the slice tag and flags to the slice flags.
- `unixware_pt_idinfo` sets a floppy-avoidance minimum size and declares little-endian magic at the disklabel offset.

## Dependencies and Interactions
Normally invoked as a DOS nested subprobe for UnixWare MBR partition type. Uses nested containment checks from `partitions.c`.

## Research Notes
Only slices with `UNIXWARE_FLAG_VALID` are exposed, and slice 0 is intentionally ignored because it describes the whole disk.
