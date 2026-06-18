# File Research: sources/block-storage/util-linux/libblkid/src/partitions/aix.c

## Purpose
Detects AIX partition-table signatures for the libblkid partition chain.

## Main Components
- `probe_aix_pt()` returns success immediately for type-only probing.
- For binary probing, obtains the current partition list and creates an `aix` partition-table object at offset 0.
- `aix_pt_idinfo` declares the prober name and AIX magic from `aix.h`.

## Dependencies and Interactions
Used by the partition dispatcher before DOS probing. `dos.c` explicitly ignores disks with AIX magic to avoid false DOS recognition.

## Research Notes
The code does not parse AIX partition entries; it only records the table type because the on-disk structures are not implemented here.
