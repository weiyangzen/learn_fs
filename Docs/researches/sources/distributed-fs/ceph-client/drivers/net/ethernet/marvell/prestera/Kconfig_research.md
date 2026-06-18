# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Kconfig

## Purpose
`Kconfig` defines build-time configuration symbols for the Marvell Prestera switch ASIC driver and its PCI transport.

## Important APIs, Types, and Definitions
`CONFIG_PRESTERA` is a tristate switch ASIC driver depending on `NET_SWITCHDEV`, `VLAN_8021Q`, and either bridge support or bridge disabled, selecting `NET_DEVLINK` and `PHYLINK`. `CONFIG_PRESTERA_PCI` is a tristate PCI interface driver depending on `PCI`, `HAS_IOMEM`, and `PRESTERA`, defaulting to the base driver state.

## Control Flow
No runtime flow exists. The configuration controls which objects from the Prestera Makefile are built and whether the PCI transport module is available.

## State and Persistence
State is build configuration only. Module names exposed in help text are `prestera` and `prestera_pci`.

## Dependencies and Integration Points
This file integrates with the kernel Kconfig system and gates the source files in the same directory. The selected devlink/phylink dependencies match APIs used by `prestera.h` and implementation files.

## Risks and Edge Cases
Bridge dependency uses `depends on BRIDGE || BRIDGE=n`, allowing non-bridge builds while preventing incompatible modular combinations. Missing selected symbols would cause build failures across switchdev/devlink/phylink users.

## Test Signals
Build `PRESTERA=y/m/n`, `PRESTERA_PCI=y/m`, bridge built-in/module/disabled combinations, and minimal configs to verify dependency propagation and module names.
