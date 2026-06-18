# sources/distributed-fs/ceph-client/drivers/phy/st/Makefile

Purpose: maps ST PHY Kconfig symbols to object files.

Important APIs, types, and functions: builds `phy-miphy28lp.o`, `phy-spear1310-miphy.o`, `phy-spear1340-miphy.o`, `phy-stih407-usb.o`, `phy-stm32-combophy.o`, and `phy-stm32-usbphyc.o` for their respective symbols.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY make system.

Risks: minor whitespace inconsistency is cosmetic. Object mapping is direct and low risk.

Test signals: module build and modpost coverage for each ST symbol.
