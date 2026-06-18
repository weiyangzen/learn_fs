# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/Kconfig

## Purpose
This Kconfig entry exposes the Marvell OCTEON PCI Endpoint NIC VF driver as `CONFIG_OCTEON_EP_VF`.

## Important APIs, Types, And Functions
- `config OCTEON_EP_VF` declares a tristate driver option named "Marvell Octeon PCI Endpoint NIC VF Driver".
- Dependencies are `64BIT` and `PCI`.
- Help text identifies the module name as `octeon_ep_vf` and points readers to `Documentation/networking/device_drivers/ethernet/marvell/octeon_ep_vf.rst`.

## Control Flow
Kconfig controls whether the VF driver is omitted, built into the kernel, or built as a module. When enabled, the Makefile builds the object list for `octeon_ep_vf.o`.

## State And Persistence
There is no runtime state here. The selected configuration persists in the kernel build configuration and determines whether the VF driver is compiled.

## Dependencies And Integration Points
The entry integrates with the kernel networking/ethernet driver Kconfig tree. It depends on generic PCI support and a 64-bit build because the driver uses 64-bit DMA and MMIO register accesses.

## Risks And Edge Cases
- Documentation path must exist in the target kernel tree, or help text becomes stale.
- No explicit dependency on the PF driver exists; VFs can be built independently, but runtime operation still requires a compatible PF/firmware mailbox endpoint.
- Missing `PCI_MSI`-style dependency may be acceptable if PCI implies MSI-X availability in the target kernel configuration, but it is worth validating.

## Test Signals
Run Kconfig build matrix checks for `n`, `m`, and `y`, verify the module name, confirm dependency handling on non-PCI or non-64-bit configs, and ensure menu visibility from the parent Marvell Ethernet Kconfig.
