# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Makefile

## Purpose
This Makefile maps Tehuti Kconfig symbols to kernel objects. It builds the legacy single-file driver and the newer multi-object TN40xx module.

## Important APIs, Types, and Functions
`obj-$(CONFIG_TEHUTI) += tehuti.o` builds the legacy driver. `tn40xx-y := tn40.o tn40_mdio.o tn40_phy.o` defines the composite module contents, and `obj-$(CONFIG_TEHUTI_TN40) += tn40xx.o` enables that module when selected.

## Control Flow and State
There is no runtime behavior. Build state controls linkage boundaries: `tn40.c` owns PCI/netdev/data path, `tn40_mdio.c` owns MDIO bus and software-node setup, and `tn40_phy.c` owns phylink callbacks and PHY registration. Those objects share `tn40.h` declarations and are linked into one module.

## Dependencies and Integration Points
The file depends on symbols from `Kconfig` and on the kernel kbuild convention for composite `*-y` objects. It integrates with module firmware annotations from `tn40.c` and `tn40_mdio.c`; both object files must be linked for all firmware declarations and exported intra-module functions to resolve.

## Risks and Test Signals
The highest risk is object list drift: removing `tn40_mdio.o` or `tn40_phy.o` would leave unresolved `tn40_mdiobus_init`, `tn40_swnodes_cleanup`, `tn40_phy_register`, or `tn40_phy_unregister`. Test signals are module builds for `CONFIG_TEHUTI_TN40=m`, built-in builds, and `modinfo tn40xx` showing expected firmware references.
