# sources/distributed-fs/ceph-client/drivers/phy/sunplus/Makefile

Purpose: object mapping for Sunplus USB2 PHY support.

Important APIs, types, and functions: `obj-$(CONFIG_PHY_SUNPLUS_USB) += phy-sunplus-usb2.o`.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY make system.

Risks: low; direct mapping.

Test signals: module/object inclusion and modpost checks.
