# File Research: sources/block-storage/parted/libparted/fs/fat/fat.c

FAT filesystem allocation, probing, registration, and cleanup. `fat_alloc()` allocates a `PedFileSystem`, its `FatSpecific` payload, initializes boot/info sector pointers, duplicates the geometry, and marks the filesystem unchecked. `fat_free()` frees boot sector, geometry, type-specific storage, and the filesystem object.

`fat_probe()` allocates a temporary filesystem, reads and analyzes the boot sector, returns the detected FAT type through an output parameter, and creates a geometry sized to the FAT sector count from the boot sector. `fat_probe_fat16()` and `fat_probe_fat32()` wrap it and accept only matching analyzed types, freeing mismatched probe geometries.

`ped_file_system_fat_init()` registers `fat16` and `fat32` only if the packed boot sector is exactly 512 bytes; otherwise it throws a bug exception and disables FAT support. This protects against compiler packing/layout problems.
