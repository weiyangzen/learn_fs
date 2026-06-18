# sources/distributed-fs/ceph-client/drivers/phy/broadcom/Makefile

Purpose: Maps Broadcom PHY Kconfig symbols to their compiled objects.

Important APIs and types: Each `obj-$(CONFIG_...)` line adds a driver object. `CONFIG_PHY_BRCM_USB` builds the composite `phy-brcm-usb-dvr.o` from `phy-brcm-usb.o`, `phy-brcm-usb-init.o`, and `phy-brcm-usb-init-synopsys.o`.

Control flow and integration: The Makefile is the build graph for the Broadcom PHY subtree. It links platform, MDIO, and composite STB USB support into the kernel or modules according to Kconfig.

State and persistence: Build-only; no runtime behavior.

Dependencies: It depends on Kconfig symbols from the sibling file and corresponding C sources. Composite object ordering matters for shared init-operation symbols.

Risks and test signals: Test all Broadcom PHY symbols in module and built-in configurations, especially that `phy-brcm-usb-dvr` resolves helper symbols across the three source files and that removed/renamed sources do not leave stale object references.
