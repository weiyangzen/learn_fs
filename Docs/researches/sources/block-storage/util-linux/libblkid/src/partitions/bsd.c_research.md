# File Research: sources/block-storage/util-linux/libblkid/src/partitions/bsd.c

## Purpose
Parses BSD disklabels and exposes FreeBSD, NetBSD, OpenBSD, or generic BSD nested partition tables.

## Main Components
- Offset macros convert `blkid_idmag` positions into 512-sector and byte offsets.
- `bsd_checksum()` validates disklabels by XORing 16-bit words.
- `probe_bsd_pt()` reads the disklabel at architecture/variant-specific magic offsets, verifies checksum, determines table name from the parent MBR partition type, creates a partition table, and adds active BSD partitions.
- Handles FreeBSD relative offsets by detecting a zero-offset third whole-disk partition in newer labels.
- Skips entries equal to the parent partition and entries outside the parent range.
- `bsd_pt_idinfo` declares three little-endian magic locations: sector 1 offset 0, sector 0 offset 64, and sector 0 offset 128.

## Dependencies and Interactions
Typically invoked as a nested subprobe from DOS partition types, but also appears in the general partition dispatcher. Relies on `pt-bsd.h` constants and `partitions.c` nested-dimension checks.

## Research Notes
Type-only probing returns the initial `BLKID_PROBE_NONE` value in this implementation before reading details, so its useful path is binary/nested detail parsing.
