# File Research: sources/block-storage/parted/libparted/fs/fat/bootsector.c

FAT boot-sector reader and analyzer for libparted’s non-resize FAT probe path. `fat_boot_sector_read()` reads sector zero of a geometry into a `FatBootSector`, then performs minimum sanity checks needed to avoid invalid arithmetic: boot signature `0xAA55`, nonzero sector size aligned to 512, nonzero cluster size, nonzero reserved sectors, and FAT count between 1 and 4.

`fat_boot_sector_probe_type()` deliberately ignores the textual FAT label. It treats zero root-directory entries as FAT32; otherwise it computes first data cluster location and cluster count to distinguish FAT12 from FAT16. `fat_boot_sector_analyse()` fills `FatSpecific` fields: logical sector size, CHS values, total sectors, FAT count and offsets, cluster sizing, FAT type, FAT size, serial, root directory placement, FAT32 info/backup sector offsets, and cluster count. FAT12 is explicitly rejected as unsupported.

This copy is read/probe oriented. Unlike the resize-library copy under `fs/r/`, it does not fix CHS fields or generate/write boot/info sectors.
