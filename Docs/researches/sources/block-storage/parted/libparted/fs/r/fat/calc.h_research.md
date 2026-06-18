# File Research: sources/block-storage/parted/libparted/fs/r/fat/calc.h

Declares the FAT sizing and address-conversion interface implemented by `calc.c`.

Exports:
- Cluster size/count bound helpers.
- Reserved-sector count helper.
- General creation sizing and resize sizing calculators.
- Resize geometry viability check.
- Alignment calculation between old/new filesystems.
- Sector/fragment/cluster conversion helpers.

Role:
- Shared header for FAT create/open/check/resize code.
- Depends on FAT core types from `fat.h` inclusion ordering.
