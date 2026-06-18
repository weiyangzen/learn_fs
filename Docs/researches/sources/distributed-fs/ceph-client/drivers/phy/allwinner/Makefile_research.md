# sources/distributed-fs/ceph-client/drivers/phy/allwinner/Makefile

Purpose: kbuild object mapping for Allwinner PHY drivers.

Important APIs, types, and functions: maps `CONFIG_PHY_SUN4I_USB` to `phy-sun4i-usb.o`, `CONFIG_PHY_SUN6I_MIPI_DPHY` to `phy-sun6i-mipi-dphy.o`, `CONFIG_PHY_SUN9I_USB` to `phy-sun9i-usb.o`, and `CONFIG_PHY_SUN50I_USB3` to `phy-sun50i-usb3.o`.

Control flow: when the parent PHY Makefile descends into `allwinner/`, kbuild includes objects whose config symbols are `y` or `m`.

State and persistence: no runtime state; build output depends on `.config`.

Dependencies and integration: paired with `drivers/phy/allwinner/Kconfig`; integrates the four Allwinner source files into the kernel or modules.

Risks: the file is small, so main risk is symbol/object drift if drivers are renamed or new Kconfig entries are added without object mappings. Test signals include `make drivers/phy/allwinner/` and checking modules appear under expected names.
