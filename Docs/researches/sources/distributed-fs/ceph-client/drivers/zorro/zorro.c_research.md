<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro.c

## Purpose
`zorro.c` enumerates Amiga Zorro AutoConfig devices, registers them with the Linux device model, manages resources, and tracks unused Zorro II RAM chunks.

## Important APIs, types, and functions
Exports include `zorro_find_device`, `zorro_num_autocon`, `zorro_autocon`, and `zorro_unused_z2ram`. Core helpers are `mark_region`, `zorro_find_parent_resource`, `amiga_zorro_probe`, and `amiga_zorro_init`.

## Control flow
The platform probe allocates a flexible `zorro_bus`, registers the bus device, copies firmware/autoconfig records into `zorro_dev` entries, derives IDs and names, requests resource ranges, sets DMA masks based on Zorro II/III type, registers each device, then marks available/used Zorro II RAM chunks.

## State and persistence
Boot-time state includes the global autoconfig array, per-device resources, and `zorro_unused_z2ram` bitmap. It persists for the running kernel but is not stored on disk.

## Dependencies and integration points
It depends on Amiga hardware setup globals, platform devices, resource management, DMA masks, Zorro name lookup, and driver-core bus registration from `zorro-driver.c`.

## Risks and test signals
Risks include address-space collisions, GVP EPC quirk reads, incorrect DMA masks, resource parent selection, and bitmap mismatch for Zorro II RAM. Test signals include Amiga boot enumeration, resource collision logs, Zorro II RAM consumers, and `zorro_find_device` iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.c -->
