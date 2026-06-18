# File Research: sources/block-storage/util-linux/libblkid/src/partitions/dasd.c

## Purpose
Detects and parses IBM s390 DASD partition labels in CDL and LDL formats.

## Main Components
- EBCDIC-to-ASCII helpers extract volume serial (`volser`) and dataset names (`dsnam`).
- CCHH helpers decode large-volume cylinder/head fields.
- Label recognizers identify CDL `VOL1`, LDL `LNX1`/`CMS1`, and format-4 labels.
- `probe_dasd_pt_cdl()` finds the format-4 label, derives blocks per track, heads, cylinders, scans format-1/8 labels, converts track ranges to 512-sector ranges, and adds up to three partitions with name/type strings derived from dataset names.
- `probe_dasd_pt_ldl()` creates one implicit partition starting at block 3 and sizes it from LDL version metadata or device size.
- `probe_dasd_pt()` tries the current sector size and known DASD block sizes, records magic and PTUUID, creates the `dasd` table, sets table ID, and dispatches to CDL or LDL parsing.
- `dasd_pt_idinfo` has no fixed magic location because label location depends on format/block size.

## Dependencies and Interactions
Uses structures/constants from `pt-dasd.h`, partition helpers, probe buffer reads, and string trimming. This is included as the last partition prober in `partitions.c`.

## Research Notes
The file is dated 2026 and handles both real DASD geometry and disk-image cases where the libblkid sector size may not match the DASD block size.
