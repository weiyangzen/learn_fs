# File Research: sources/block-storage/parted/libparted/fs/fat/bootsector.h

Defines packed FAT boot-sector and FAT32 info-sector layouts for the non-resize FAT support. It includes boot message/jump/code constants, FAT32 FSInfo magic values, and declarations for read, type-probe, and analysis functions.

`FatBootSector` models the BIOS parameter block and FAT16/FAT32 union fields, ending with `boot_sign` at byte `0x1fe`. `FatInfoSector` models FAT32 free-cluster and next-cluster metadata. This version also defines `FAT_BOOT_CODE_LENGTH 128`, used as a compile-time size constant by related code.

The header is layout-critical: `fat.c` checks `sizeof(FatBootSector) == 512` before registering FAT probes.
