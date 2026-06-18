# File Research: sources/block-storage/parted/libparted/fs/r/fat/fat.h

Umbrella header for the FAT implementation.

Defines:
- Core FAT scalar types: `FatCluster`, `FatFragment`, `FatType`.
- Packed on-disk `FatDirEntry`.
- `FatSpecific`, the per-filesystem state containing boot/info sectors, geometry, FAT type, offsets, table, cluster info, and shared buffers.
- FAT constants for attributes, root directory size, and max cluster counts.

Includes:
- `table.h`, `bootsector.h`, `context.h`, `fatio.h`, `traverse.h`, `calc.h`, `count.h`, `clstdup.h`.

Exports:
- FAT filesystem types.
- Allocation/free/buffer functions.
- `fat_resize()`.
- Fragment-size setter.

Role:
- Central compile-time coupling point for the FAT resizer.
