# File Research: sources/block-storage/parted/libparted/fs/fat/fat.h

Main FAT support header for libparted’s probe-oriented FAT code. It defines `FatCluster`, `FatFragment`, `FatType`, FAT table state, packed directory-entry layout, and the `FatSpecific` per-filesystem state structure.

`FatSpecific` stores boot/info sectors, logical and physical sizing, CHS fields, total sectors, cluster counts and offsets, FAT type/count/size, serial number, root directory details, FAT32 info/backup sector offsets, FAT table and cluster-info pointers, buffer sizing, and fragment mapping. Macros define directory attributes, cluster-count thresholds for FAT12/FAT16/FAT32, and root directory defaults.

The header also declares public helper functions for allocation, free, buffer allocation, and resize. Some declarations are implemented outside this file group, so this header is shared with broader FAT support.
