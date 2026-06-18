# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Makefile

## Purpose
This Makefile wires the Sunplus SP7021 Ethernet driver into the kernel build. It maps `CONFIG_SP7021_EMAC` to the composite object `sp7021_emac.o` and lists the implementation objects that make up that module or built-in driver.

## Important APIs, Types, And Variables
- `obj-$(CONFIG_SP7021_EMAC) += sp7021_emac.o` includes the driver only when the Kconfig symbol is enabled.
- `sp7021_emac-objs := spl2sw_driver.o spl2sw_int.o spl2sw_desc.o spl2sw_mac.o spl2sw_mdio.o spl2sw_phy.o` declares the component objects for the composite target.

## Control Flow And State Behavior
The file has no runtime control flow. Build-time control is entirely driven by `CONFIG_SP7021_EMAC`. When enabled as `m`, the listed objects are linked into `sp7021_emac.ko`; when enabled as `y`, they are linked into the kernel image.

## Dependencies And Integration Points
It integrates with the Sunplus Kconfig file and the kernel kbuild composite-object convention. The object names indicate separate implementation areas for top-level driver logic, interrupts, descriptors, MAC programming, MDIO, and PHY handling.

## Risks And Edge Cases
- Any source rename or split must update `sp7021_emac-objs` or the build fails.
- The composite target name must remain aligned with the Kconfig help text's promised module name.
- Missing conditional objects may limit compile coverage if future features become optional.

## Test Signals
Build with `CONFIG_SP7021_EMAC=m` and `CONFIG_SP7021_EMAC=y`, verify the composite object links all six components, and run clean rebuilds after touching each component object dependency.
