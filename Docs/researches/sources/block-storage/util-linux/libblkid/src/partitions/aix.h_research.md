# File Research: sources/block-storage/util-linux/libblkid/src/partitions/aix.h

## Purpose
Defines the AIX partition-table magic string shared by AIX and DOS partition probing code.

## Main Components
- Include guard `BLKID_PARTITIONS_AIX_H`.
- `BLKID_AIX_MAGIC_STRING` as the four-byte sequence `C9 C2 D4 C1`.
- `BLKID_AIX_MAGIC_STRLEN` as the string length excluding NUL.

## Dependencies and Interactions
Included by `aix.c` for detection and by `dos.c` to suppress DOS probing on AIX-labeled disks.

## Research Notes
The header has no functions or structs; it centralizes one format signature.
