# sources/distributed-fs/ceph-client/drivers/pnp/system.c

## Purpose
`system.c` is the PnP system resource reservation driver. It binds generic motherboard/system-resource PnP IDs and reserves their I/O and memory ranges in the kernel resource tree so later allocation avoids firmware-described fixed resources.

## Important APIs, Types, and Functions
The driver table matches `PNP0c02` for general system resources and `PNP0c01` for memory controllers. Important functions are `reserve_range()`, `reserve_resources_of_dev()`, `system_pnp_probe()`, and `pnp_system_init()`. The `system_pnp_driver` uses `PNP_DRIVER_RES_DO_NOT_CHANGE` so the PnP core does not reassign these resources.

## Control Flow
At `fs_initcall` time, the driver registers with PnP. Probe iterates each I/O resource, skips disabled, zero-start, sub-0x100 PC legacy ranges, and invalid ranges, then calls `request_region()`. It also iterates memory resources and calls `request_mem_region()`. Successful reservations have `IORESOURCE_BUSY` cleared so they remain reserved as firmware/system regions but do not look like active driver claims.

## State and Persistence Behavior
Persistent state is in the global kernel resource trees. `reserve_range()` allocates a small region-name string and intentionally leaves it attached to successful resource reservations; failed reservations free the string. No per-device private state is stored. Reservation survives for kernel lifetime because there is no remove path for these system PnP resources.

## Dependencies and Integration Points
It depends on PnP driver registration, the PnP resource helpers from `resource.c`, kernel I/O and memory resource management, and firmware PnP device enumeration. It is deliberately ordered after PCI BAR claims but before uninitialized PCI resource assignment.

## Risks and Edge Cases
Reservation failures are usually benign and logged because other quirks may already reserve the same range. Clearing `IORESOURCE_BUSY` is subtle: it prevents false ownership while still occupying the resource span. I/O resources below `0x100` are skipped because standard PC resources are reserved elsewhere; this assumption is PC-platform-specific. The allocated region name is intentionally not freed on success.

## Test Signals
Boot systems with PNP0c01/PNP0c02 firmware resources, verify `/proc/iomem` and `/proc/ioports` reservations, test overlapping PCI quirk reservations, invalid/disabled resource skips, low I/O range skips, and init ordering relative to PCI assignment.
