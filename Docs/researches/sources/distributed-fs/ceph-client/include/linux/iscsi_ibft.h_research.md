# sources/distributed-fs/ceph-client/include/linux/iscsi_ibft.h

## Purpose
`iscsi_ibft.h` declares discovery and reservation support for the iSCSI Boot Firmware Table physical memory region.

## Important APIs, types, and functions
It declares global `phys_addr_t ibft_phys_addr`, conditionally declares `reserve_ibft_region`, and defines the legacy search bounds `IBFT_START` and `IBFT_END` when `CONFIG_ISCSI_IBFT_FIND` is enabled.

## Control flow
Early boot code searches 512 KiB through 1 MiB for the iBFT, reserves the physical region, and records its address in `ibft_phys_addr`. Disabled builds compile `reserve_ibft_region` to a no-op.

## State and persistence
Runtime state is the discovered physical address. The underlying table is firmware-provided memory and persists only according to platform firmware behavior.

## Dependencies and integration points
It depends on physical address types and integrates early memory reservation with iSCSI boot sysfs export.

## Risks and test signals
Risks include missing the table outside legacy bounds, failing to reserve memory before reuse, and disabled configs losing boot data. Tests should cover systems with and without iBFT, memory reservation maps, malformed tables, and disabled finder builds.
