# sources/distributed-fs/ceph-client/include/uapi/linux/msdos_fs.h

## Purpose
Defines FAT/MS-DOS filesystem constants, on-disk boot/FSINFO/directory layouts, attribute bits, FAT limits, endian helpers, and VFAT/FAT ioctl ABI.

## Important APIs, Types, And Functions
Exports sector and directory sizing constants, attribute flags, FAT cluster markers, FSINFO signatures, `__fat_dirent`, VFAT/FAT ioctls, `fat_boot_sector`, `fat_boot_fsinfo`, `msdos_dir_entry`, and `msdos_dir_slot`.

## Control Flow
Filesystem code parses the boot sector, determines FAT variant by cluster count, reads FSINFO when signatures match, walks directory entries and long-name slots, and exposes ioctls for readdir compatibility, attributes, and volume ID.

## State, Persistence, And Dependencies
Structs map persistent disk bytes. Depends on `linux/types.h`, `linux/magic.h`, and byteorder helpers.

## Integration Points
Used by FAT/VFAT filesystem drivers, fsck/mkfs tools, mount utilities, and Android/Linux attribute utilities.

## Risks
On-disk fields are little-endian and packed by layout convention. Long filename slots and deleted/free markers are easy to misparse. FAT12/16/32 boundary constants determine variant behavior.

## Test Signals
Test FAT12/16/32 image parsing, FSINFO validation, long-name reconstruction, ioctl attribute get/set, volume ID query, deleted/free entries, and endian conversion.
