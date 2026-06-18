# File Research: sources/block-storage/util-linux/libblkid/src/partitions/partitions.c

## Purpose
Core implementation of libblkid’s partition probing chain, binary partition object model, partition NAME=value result generation, nested subprobe support, and public partition accessor APIs.

## Main Components
- Defines the partition chain driver `partitions_drv`.
- Registers partition probers in detection order: AIX, SGI, Sun, DOS, GPT, PMBR, Mac, Ultrix, BSD, UnixWare, Solaris, Minix, Atari, and DASD.
- Defines private opaque-backed structs for `blkid_parttable`, `blkid_partition`, and `blkid_partlist`.
- Public controls:
  - `blkid_probe_enable_partitions()`
  - `blkid_probe_set_partitions_flags()`
  - filter reset/invert/type APIs
  - `blkid_probe_get_partitions()`
- Internal partlist/table management:
  - `partitions_init_data()`
  - `reset_partlist()`
  - `partitions_free_data()`
  - `blkid_partlist_new_parttable()`
  - `blkid_partlist_add_partition()`
  - part-number and parent tracking helpers
- `idinfo_probe()` performs device-size/NOSCAN checks, magic lookup, prober dispatch, buffer pruning, error reset, and magic result recording.
- `partitions_probe()` runs the prober loop, applies filters, sets `PTTYPE`, and optionally gathers partition-entry details.
- `blkid_partitions_do_subprobe()` clones a probe over a parent partition’s byte range and lets nested parsers append to the same partition list.
- `blkid_partitions_probe_partition()` maps the current partition device back to the whole-disk partition list and emits `PART_ENTRY_*` values.
- `blkid_probe_is_covered_by_pt()` checks whether a byte range is covered by any parsed partition.
- Public lookup/accessor APIs expose known partition types, table counts, table metadata, partition lookup by index/number/start/devno, table IDs, names, UUIDs, starts, sizes, numeric/string types, flags, and primary/extended/logical classification.
- Setter helpers are used by format-specific probers to fill names, UUIDs, type strings/UUIDs, flags, PTUUIDs, and pseudo MBR partition UUIDs.

## Behavior
Binary partition access uses `blkid_probe_get_binary_data()` and causes the partition chain to allocate/reset a reusable `blkid_partlist`. Non-binary probing instead emits values such as `PTTYPE`, `PTUUID`, and optionally `PART_ENTRY_*`.

Nested partition probing clones the parent probe, restricts dimensions to the parent partition, points the clone at the parent’s partition list, sets the parent pointer for new tables, runs the nested idinfo prober, then restores state. This lets MBR-contained BSD/Solaris/UnixWare/Minix labels appear in the same binary list while preserving their owning table.

Partition starts and sizes are represented in 512-byte sectors across the binary API. Table offsets are bytes. `blkid_partlist_devno_to_partition()` correlates sysfs `start`/`size` data, with a kpartx/device-mapper fallback based on `dm/uuid` prefixes like `partN`.

## Dependencies and Interactions
This file is the hub for all partition prober files in this group and is exposed through `blkid.h.in`. It depends on probe-chain internals in `blkidP.h`, sysfs path helpers, string utilities, MBR constants, and util-linux list infrastructure.

## Research Notes
The detection order matters. PMBR must follow GPT, DOS rejects GPT protective MBRs, and format-specific probers use `blkid_partitions_need_typeonly()` to avoid expensive detail parsing for NAME=value-only detection.
