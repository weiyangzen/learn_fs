# File Research: sources/block-storage/parted/libparted/arch/beos.c

This file implements the libparted architecture backend for BeOS/ZETA/Haiku-style device access.

Core responsibilities:
- Defines `BEOSSpecific`, containing the platform file descriptor used for I/O.
- Recursively scans `/dev/disk` and probes entries named `raw` as whole-disk devices.
- Initializes devices from either BeOS/ZETA ATA metadata, generic block-device geometry, or regular-file disk images.
- Provides the BeOS `PedDeviceArchOps` and `PedDiskArchOps` tables exported through `ped_beos_arch`.

Device initialization:
- `_device_init_ata()` is compiled for ZETA-era APIs and reads ATA identity/geometry through `B_ATA_GET_DEVICE_INFO`.
- `_device_init_generic_blkdev()` uses `B_GET_GEOMETRY` and optionally `B_GET_BIOS_GEOMETRY`.
- `_device_init_file()` treats a regular file as a disk image with default sector size and synthetic `4/32` geometry.
- `beos_new()` allocates `PedDevice`, path, and `BEOSSpecific`, initializes common flags, then delegates to `_device_init()`.

I/O behavior:
- `beos_open()` tries read-write first, falls back to read-only with a warning, and flushes cache.
- `beos_read()` and `beos_write()` use `lseek()` plus `read()`/`write()` loops, retrying or ignoring according to libparted exception responses.
- Writes set `dev->dirty` unless compiled with `READ_ONLY`.
- `beos_check()` reads a range and returns the number of sectors successfully read.
- `beos_sync()` and `beos_sync_fast()` are stubs that return success.

Disk/partition behavior:
- `beos_partition_get_path()` returns `NULL`.
- `beos_partition_is_busy()` returns `0`.
- `beos_disk_commit()` returns `0`, so kernel partition-table commit is effectively unsupported here.

Notable implementation risks:
- `_flush_cache()` checks `if ((fd=open(dev->path, O_RDONLY)) < 0)` before calling `ioctl(fd, B_FLUSH_DRIVE_CACHE)`, which appears inverted because it would call `ioctl` on a negative descriptor.
- Partition path and commit operations are placeholders, so this backend is mainly useful for raw device/file I/O and probing rather than full kernel partition synchronization.
