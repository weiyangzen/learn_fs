# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/Makefile

## Purpose
This Makefile wires the `atl1c` Ethernet driver into Kbuild. When `CONFIG_ATL1C` is enabled, it builds a single module or built-in object named `atl1c.o`.

## Important APIs, types, and functions
The file has no C APIs. Its important Kbuild declarations are `obj-$(CONFIG_ATL1C) += atl1c.o` and `atl1c-objs := atl1c_main.o atl1c_hw.o atl1c_ethtool.o`. These three objects form the driver: PCI/netdev lifecycle and packet paths in `atl1c_main.o`, hardware/PHY helper code in `atl1c_hw.o`, and ethtool operations in `atl1c_ethtool.o`.

## Control flow and state behavior
There is no runtime control flow. At build time, Kbuild includes the object when the kernel configuration enables the driver. The object list determines link order within the composite driver object and therefore which translation units must satisfy exported symbols such as `atl1c_driver_name`, `atl1c_reset_hw`, `atl1c_reinit_locked`, and `atl1c_set_ethtool_ops`.

## Dependencies and integration points
The Makefile depends on the kernel networking and PCI build environment and on the `CONFIG_ATL1C` Kconfig symbol being defined elsewhere. It integrates the source files with the surrounding `drivers/net/ethernet/atheros` build tree and determines what code is available to modpost and module loading.

## Risks
The object list is small but critical. Omitting `atl1c_ethtool.o` would leave the driver without its ethtool registration helper. Omitting `atl1c_hw.o` would break low-level symbol resolution. Adding source files without updating this list would make new code unused. Since `atl1c-objs` uses assignment, later Makefile edits in the same scope must avoid accidentally replacing the list.

## Test signals
Primary signals are a successful kernel build with `CONFIG_ATL1C=m` and `CONFIG_ATL1C=y`, no unresolved symbols at modpost, `modinfo atl1c` availability for module builds, and runtime probe of supported PCI IDs.
