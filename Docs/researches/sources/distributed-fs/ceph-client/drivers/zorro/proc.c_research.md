<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/proc.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/proc.c

## Purpose
`proc.c` provides legacy procfs inspection for Zorro devices under `/proc/bus/zorro`.

## Important APIs, types, and functions
It defines binary per-slot read/lseek operations, seq operations for `/proc/bus/zorro/devices`, `zorro_proc_attach_device`, and `zorro_proc_init`.

## Control flow
At `device_initcall`, Amiga systems with Zorro hardware create `bus/zorro`, a `devices` seq file, and one binary proc entry per autoconfig slot. Per-device reads synthesize an Amiga `ConfigDev` from `struct zorro_dev`.

## State and persistence
Proc entries mirror boot-time `zorro_autocon` state. No data is persisted; reads construct data on demand.

## Dependencies and integration points
The file depends on procfs, Amiga hardware detection, endian conversions, setup/autoconfig globals, and user-copy helpers.

## Risks and test signals
Risks include proc entry creation failures being mostly ignored, bounds mistakes in fixed-size binary reads, and stale data if device registration partially failed. Test signals include `/proc/bus/zorro/devices`, per-slot read offsets, non-Amiga boot, and procfs-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/proc.c -->
