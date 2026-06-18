# File Research: sources/block-storage/parted/libparted/fs/r/fat/bootsector.h

Resize-library FAT boot-sector header. It defines the same packed `FatBootSector` and `FatInfoSector` layouts as the probe copy, plus boot message/jump/code constants and FAT32 info-sector magic values.

In addition to read/type/analyze declarations, this resize version declares mutating helpers: `fat_boot_sector_set_boot_code()`, `fat_boot_sector_generate()`, `fat_boot_sector_write()`, `fat_info_sector_read()`, `fat_info_sector_generate()`, and `fat_info_sector_write()`. These are used by FAT resizing code to rewrite BPB fields, backup boot sectors, and FSInfo metadata.

Compared with `fs/fat/bootsector.h`, this header omits `FAT_BOOT_CODE_LENGTH` but exposes the generation/write API needed by `libparted-fs-resize`.
