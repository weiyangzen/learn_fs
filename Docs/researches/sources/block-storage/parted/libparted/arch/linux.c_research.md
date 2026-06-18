# File Research: sources/block-storage/parted/libparted/arch/linux.c

This is the main Linux backend for libparted device discovery, geometry probing, I/O, cache flushing, partition naming, mount/busy checks, kernel partition-table synchronization, device-mapper integration, and topology-based alignment.

Major structures and constants:
- Uses `LinuxSpecific` from `arch/linux.h`, storing fd, major/minor, optional device-mapper target type, optional s390 fields, and optional blkid topology handles.
- Defines Linux ioctl constants locally for block size, disk size, flushing, odd last sectors, BLKPG partition operations, and old IDE/SCSI geometry.
- Classifies many block device families by major number: IDE, SCSI, DAC960, Compaq Smart Array, I2O, UBD, DASD, virtio, loop, md, blkext/NVMe, RAM, pmem, device-mapper, and others.

Device classification and initialization:
- `_device_probe_type()` uses `stat()`, `major()`, `minor()`, `/proc/devices`, and optional libdevmapper to assign `dev->type`.
- `linux_new()` allocates `PedDevice` and `LinuxSpecific`, initializes flags, optionally enables device-mapper udev synchronization, probes type, then dispatches to a type-specific initializer.
- `init_ide()` uses `HDIO_GET_IDENTITY` to get the IDE model and warns about multiple logical sectors per physical sector.
- `init_scsi()` uses `SCSI_IOCTL_GET_IDLUN`, sysfs vendor/model files, and fallback SCSI inquiry.
- `init_file()` handles regular files and test sector-size override via `PARTED_SECTOR_SIZE`.
- `init_generic()` is used for most modern or less-specific block devices and probes geometry through ioctl paths.
- `init_nvme()` reads the sysfs `model` field when available.
- s390 builds include DASD-specific initialization and alignment handling.

Geometry and length:
- `_device_set_sector_size()` uses `BLKSSZGET` for logical sector size and optional blkid topology for physical sector size.
- `_device_get_length()` prefers `PARTED_TEST_DEVICE_LENGTH`, then `BLKGETSIZE64`, then legacy `BLKGETSIZE`.
- `_device_probe_geometry()` sets length, BIOS geometry, and hardware geometry. For non-s390, it prefers sector-size ioctl data over old `HDIO_GETGEO`.

Open, close, cache, and sync:
- `_device_open()` tries requested flags, then falls back to read-only with a warning.
- `linux_open()` opens read-write through `_device_open()`.
- `_device_open_ro()` is used during probing and increments `open_count` itself.
- `linux_close()` flushes dirty devices, then `fsync()`s and closes.
- `_flush_cache()` issues `BLKFLSBUF` on the main device and unmounted partition devices. It skips read-only and RAM devices.
- `linux_sync()` performs `fsync()` then full cache flushing; `linux_sync_fast()` only performs `fsync()`.

I/O behavior:
- `linux_read()` and `linux_write()` seek by sector, use sector-aligned buffers from `posix_memalign()`, handle partial reads/writes, and route errors through libparted exceptions.
- Old kernels before 2.6 receive special handling for reading/writing the last sector on odd-sized block devices through `BLKGETLASTSECT`/`BLKSETLASTSECT`.
- `linux_check()` returns the number of readable sectors from a range.

Device discovery:
- `linux_probe_all()` probes standard `/dev/hd[a-h]` and `/dev/sd[a-f]` names, optional device-mapper dmraid devices, then `/sys/block`, falling back to `/proc/partitions`.
- `_probe_sys_block()` skips `dm-`, loop, ram, fd, `.` and `..` entries and converts sysfs `!` back to `/`.
- `_probe_proc_partitions()` uses a heuristic to skip partition entries and probe whole devices.

Partition naming and busy checks:
- `_device_get_part_path()` handles devfs `/disc` to `/partN`, appends `p` when needed for names ending in digits or certain controller types, and canonicalizes device-mapper names via `/dev/mapper`.
- `linux_partition_get_path()` returns the whole device path for `loop` disk labels.
- Mount/busy checks search `/proc/mounts`, `/proc/swaps`, and `/etc/mtab` by device number.
- `linux_is_busy()` checks the whole device and up to 32 partition paths.
- `linux_partition_is_busy()` checks active partitions and recursively checks logical partitions inside extended partitions.

Kernel partition-table synchronization:
- `_disk_sync_part_table()` implements a two-pass sync:
  1. Remove old kernel partition entries.
  2. Add or resize current libparted partitions.
- For regular block devices it uses BLKPG add/remove and optional BLKPG resize.
- For device-mapper devices it creates/removes/reloads linear maps and synchronizes with udev cookies.
- Existing kernel partition start/length is read from sysfs, HDIO geometry, BLKGETSIZE64, or device-mapper tables.
- `linux_disk_commit()` requires BLKPG for non-file devices and calls `_disk_sync_part_table()`.

Alignment:
- With blkid topology enabled, `linux_get_minimum_alignment()` uses topology alignment offset and minimum I/O size or physical sector size.
- `linux_get_optimum_alignment()` prefers Parted’s default 1 MiB alignment when it is compatible with topology I/O sizes, otherwise uses optimal or minimum I/O alignment.
- On s390, DASD-like devices use minimum alignment for optimum alignment.

Notable implementation risks:
- Some fallback ioctl success tests in `_kernel_get_partition_start_and_length()` appear suspicious because ioctl success convention is zero, but the code checks truthy return values in places.
- Several paths depend on old kernel ioctls and legacy geometry behavior, so modern correctness depends mostly on sysfs, blkid topology, and BLKPG/device-mapper paths.
- Device probing and busy checks are heuristic-heavy and intentionally conservative on allocation/path failures.
