# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Kconfig

## Purpose
This Kconfig file exposes VIA Ethernet support and the driver options for VIA Rhine Fast Ethernet and VIA Velocity Gigabit Ethernet hardware.

## Important APIs, types, and functions
There are no C APIs. `NET_VENDOR_VIA` gates the submenu. `VIA_RHINE` is a tristate that supports PCI and selected OF/platform configurations, depends on I/O ports and DMA, and selects `CRC32` and `MII`. `VIA_RHINE_MMIO` is a boolean tuning option under `VIA_RHINE` that switches Rhine PCI access toward MMIO. `VIA_VELOCITY` is a tristate depending on PCI or OF address/IRQ plus DMA, and selects `CRC32`, `CRC_CCITT`, and `MII`.

## Control flow and integration
Configuration choices drive the local Makefile: `CONFIG_VIA_RHINE` builds `via-rhine.o`, and `CONFIG_VIA_VELOCITY` builds `via-velocity.o`. `VIA_RHINE_MMIO` affects conditional code in `via-rhine.c` that sets `rqNeedEnMMIO` for PCI devices.

## State and persistence behavior
Selections persist in `.config` and determine build inclusion and module availability. No runtime state is created here.

## Dependencies and integration points
Dependencies mirror the source files: Rhine needs PCI or platform IRQ/iomap support, port I/O for PCI-era devices, DMA, CRC hashing for multicast filters, and MII helpers. Velocity needs PCI or OF-mapped platform resources, DMA, CRC helpers for multicast/WOL, and MII helpers.

## Risks and edge cases
`VIA_RHINE_MMIO` changes low-level access mode and can expose hardware/firmware issues on older revisions. The Rhine dependencies are more restrictive than pure platform operation because `HAS_IOPORT` is required. Build coverage should include both PCI and platform paths where possible.

## Test signals
Kconfig tests should confirm expected prompts and dependencies. Build matrices should cover Rhine with and without `VIA_RHINE_MMIO`, Velocity as module and built-in, and `COMPILE_TEST` platform coverage.
