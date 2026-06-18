# sources/distributed-fs/ceph-client/drivers/net/pcs/Makefile

Purpose: Lists PCS driver objects and composes the multi-file XPCS module.

Important APIs, types, and functions: `pcs_xpcs-$(CONFIG_PCS_XPCS)` combines `pcs-xpcs.o`, `pcs-xpcs-plat.o`, `pcs-xpcs-nxp.o`, and `pcs-xpcs-wx.o`. `obj-$(CONFIG_PCS_XPCS)`, `obj-$(CONFIG_PCS_LYNX)`, `obj-$(CONFIG_PCS_MTK_LYNXI)`, and `obj-$(CONFIG_PCS_RZN1_MIIC)` select the final objects.

Control flow: Kbuild compiles helper libraries and platform drivers according to Kconfig symbols. The XPCS module links core, platform MDIO/MMIO frontend, and vendor PMA helpers together.

State and persistence behavior: No runtime state; build artifact composition only.

Dependencies and integration points: It integrates PCS objects into `drivers/net/pcs` and ensures vendor helpers are available for core XPCS compatibility tables.

Risks and edge cases: Removing a helper from `pcs_xpcs` would leave unresolved symbols for NXP/WangXun PMA callbacks. Hidden helper configs require consumers to select them correctly.

Test signals: Module and built-in builds for each PCS config, modpost unresolved-symbol checks, and verifying `pcs_xpcs.ko` includes platform and vendor helper code.
