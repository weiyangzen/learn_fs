# File Research: sources/block-storage/parted/libparted/labels/loop.c

This file implements libparted’s `loop` pseudo-label backend, representing an entire device as one partition.

Key behavior:
- `loop_probe()` succeeds if sector 0 contains `GNU Parted Loopback 0` or if a filesystem is detected across the whole device.
- `loop_alloc()` rejects devices shorter than 256 sectors, allocates a disk, and creates a single normal partition covering the full device.
- `loop_read()` clears partitions, checks for the loop signature, probes a whole-device filesystem, and creates partition 1 spanning the whole device.
- `loop_write()` writes the loop signature into sector 0 only when partition 1 has no filesystem type; existing whole-device filesystems are not overwritten.
- Partition operations support setting filesystem type, alignment to caller constraints, enumeration as partition 1, and no partition flags.
- Metadata allocation is a no-op.
- Maximum primary and supported partition counts are both 1.

Integration:
- Registers `PedDiskType` named `loop` with no special feature flags.
- Uses `ptt_read_sector()` for initial sector reads and libparted filesystem probing for whole-device detection.
- Uses `pt-common.h` operation initialization.

Risk notes:
- `loop_alloc()` uses assertions after `_ped_disk_alloc()`, `ped_geometry_new()`, and `ped_partition_new()`; in non-debug behavior allocation failure handling is limited.
- `loop_write()` uses `alloca()` with sector size and `strcpy()` of a fixed short signature, which is safe for normal sector sizes but assumes sector size is large enough.
