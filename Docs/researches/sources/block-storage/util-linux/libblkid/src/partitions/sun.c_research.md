# File Research: sources/block-storage/util-linux/libblkid/src/partitions/sun.c

## Purpose
Parses Sun/Solaris SPARC disk labels.

## Main Components
- Reads sector 0 as `struct sun_disklabel`.
- Validates checksum with `sun_pt_checksum()`.
- Creates a `sun` partition table for binary probing.
- Computes sectors per cylinder from heads and sectors-per-track.
- Validates VTOC sanity/version/nparts to decide whether type/flag metadata can be used.
- Iterates partitions, converting start cylinders to sector starts.
- Skips whole-disk tags and zero-size entries while preserving partition numbers.
- Sets type and flags when available from VTOC.
- `sun_pt_idinfo` detects big-endian magic `DA BE` at the disklabel magic field.

## Dependencies and Interactions
Uses structures/constants from `pt-sun.h`, checksum helpers, and generic partition-list APIs.

## Research Notes
The parser accepts old Linux-Sun labels by allowing a zeroed VTOC sanity/version/nparts area as an additional condition for using the partition array.
