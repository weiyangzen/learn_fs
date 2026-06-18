# File Research: sources/block-storage/parted/libparted/fs/r/fat/bootsector.c

FAT boot-sector implementation for the resize library under `fs/r/`. It shares read/type/analyze logic with the probe-only FAT copy, but adds write/generation support when `DISCOVER_ONLY` is not defined.

`fat_boot_sector_read()` validates signature and core BPB fields. `fat_boot_sector_probe_type()` classifies FAT32 by zero root-entry count and FAT12/FAT16 by computed cluster count. `fat_boot_sector_analyse()` fills `FatSpecific` and rejects FAT12. Unlike the non-resize copy, invalid CHS geometry offers `FIX`, `IGNORE`, or `CANCEL`; choosing fix updates sector/heads fields in the boot sector and writes it back through `fat_boot_sector_write()`.

Resize-specific helpers generate boot code, synthesize FAT16/FAT32 boot sectors from `FatSpecific`, write the primary boot sector and FAT32 backup boot sector, read/generate/write the FAT32 info sector, and populate free-cluster/last-allocation values from FAT table statistics. This file is therefore both a parser and mutator for FAT resize operations.
