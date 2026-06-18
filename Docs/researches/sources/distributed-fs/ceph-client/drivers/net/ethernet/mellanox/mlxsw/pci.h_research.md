# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.h

## Purpose
`pci.h` declares PCI device IDs for Mellanox Spectrum ASIC generations and exposes the optional common PCI backend registration interface.

## Important APIs, Types, and Functions
- Defines `PCI_DEVICE_ID_MELLANOX_SPECTRUM`, `SPECTRUM2`, `SPECTRUM3`, and `SPECTRUM4`.
- When `CONFIG_MLXSW_PCI` is enabled, declares `mlxsw_pci_driver_register()` and `mlxsw_pci_driver_unregister()`.
- When disabled, provides no-op-ish stubs: register returns `0`, unregister does nothing.

## Control Flow
The header is compile-time glue only. Chip drivers pass their `struct pci_driver` to the common registration helper so `pci.c` can install probe/remove/shutdown/error handlers.

## State and Persistence
No runtime state exists in this header.

## Dependencies and Integration Points
It depends on `<linux/pci.h>` and is included by mlxsw PCI chip drivers and `pci.c`. The IDs connect modalias matching to supported Spectrum devices.

## Risks
The disabled registration stub returns success, unlike the I2C stub, so callers must be aware that a build without `CONFIG_MLXSW_PCI` may appear to register successfully at compile-time abstraction level. New Spectrum IDs must be added consistently with chip-specific driver ID tables.

## Test Signals
Build with PCI enabled/disabled and verify chip drivers compile. Runtime PCI modalias matching should bind supported Spectrum IDs to drivers that use this backend.
