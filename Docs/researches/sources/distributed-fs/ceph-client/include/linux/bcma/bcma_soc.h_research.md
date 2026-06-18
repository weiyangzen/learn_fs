# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_soc.h

## Purpose
Declares the SoC-host wrapper for registering BCMA buses embedded in Broadcom SoCs.

## Important APIs, types, and functions
- `struct bcma_soc` contains an embedded `bcma_bus` and parent `device`.
- `bcma_host_soc_register()` registers an SoC-hosted BCMA bus.
- `bcma_host_soc_init()` initializes SoC-host BCMA state.
- `bcma_bus_register()` registers an already prepared bus.

## Control flow and state
SoC platform code initializes a `bcma_soc`, sets up mappings/device context, calls the SoC init/register helpers, and the common BCMA bus then enumerates cores.

## State and persistence behavior
State is runtime bus/platform state. The embedded `bcma_bus` holds discovered cores and chipcommon/PCI/MIPS/etc. driver state.

## Dependencies and integration points
Depends on `bcma.h`. Integrated by Broadcom SoC platform initialization and shared BCMA bus registration.

## Risks
The wrapper assumes the SoC host has mapped MMIO and device context before registration. Calling common `bcma_bus_register()` too early can expose incomplete core state to drivers.

## Test signals
Boot supported SoC hosts, verify bus enumeration and device binding, test init/register ordering, and validate error cleanup for failed registration.
