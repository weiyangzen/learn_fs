# File Research: sources/block-storage/parted/libparted/arch/gnu.c

This file implements the GNU/Hurd architecture backend using Hurd `store` objects.

Core responsibilities:
- Defines `GNUSpecific`, holding a `struct store *` and a `consume` flag indicating whether libparted owns that store.
- Supports both path/type based store opening and direct construction with `ped_device_new_from_store()`.
- Exports `ped_gnu_arch` with GNU/Hurd device and disk operation tables.

Device model:
- Sector size is fixed to `PED_SECTOR_SIZE_DEFAULT`.
- Device length is computed from `store->blocks * store->block_size`.
- Geometry is synthetic: BIOS heads/sectors are set to `255/63`, with cylinders derived from length.
- `init_file()` opens the device, probes geometry, sets `dev->model` to an empty string, and closes the device.

Opening and ownership:
- `gnu_new()` allocates a device and tries to open the store read-write, then read-only.
- `ped_device_new_from_store()` wraps an existing store without registering it in Parted’s global device list and does not consume it.
- `gnu_destroy()` frees the store only when `consume` is set.

I/O behavior:
- `gnu_read()` maps libparted sectors to Hurd store blocks, handles store block sizes larger than 512 bytes, and copies only the requested byte range into the user buffer.
- `gnu_write()` handles unaligned first and last store blocks with read-modify-write and writes aligned middle ranges directly.
- Read/write errors are routed through libparted exceptions with retry/ignore/cancel behavior.
- `gnu_check()` currently returns `count` without actually checking media.
- `gnu_sync()` uses `file_sync()` and remembers one path whose sync failure was ignored to avoid repeating the same prompt.

Partition synchronization:
- `_reread_part_table()` attempts to notify the kernel with `BLKRRPART` for device stores, then removes active parted-based translators for paths like `<dev>sN`.
- `gnu_partition_get_path()` formats partitions as `<device-path>s<num>`.
- `gnu_partition_is_busy()` always returns not busy.
- `gnu_disk_commit()` delegates to `_reread_part_table()`.

Probe behavior:
- `gnu_probe_all()` probes a fixed list of common Hurd disk names: `/dev/sd*`, `/dev/hd*`, `/dev/wd*`, and `/dev/ud*`.

Research notes:
- This backend is store-centric rather than file-descriptor-centric.
- It contains careful handling for store block sizes that differ from libparted’s logical sector size.
- Busy detection is effectively absent, so correctness depends on Hurd store/translator behavior during commit.
