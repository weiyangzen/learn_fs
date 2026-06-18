# sources/distributed-fs/ceph-client/drivers/phy/apple/Makefile

Purpose: Connects the Apple PHY Kconfig symbol to its object file.

Important APIs and types: `obj-$(CONFIG_PHY_APPLE_ATC) += phy-apple-atc.o` adds the driver object when selected. `phy-apple-atc-y := atc.o` builds that composite object from `atc.c`.

Control flow and integration: Kernel build recursion in `drivers/phy/apple` uses this Makefile to produce the final built-in or module artifact named by Kconfig help as `phy-apple-atc`.

State and persistence: This file has no runtime state; it only controls build graph membership.

Dependencies: It depends on `CONFIG_PHY_APPLE_ATC` from the sibling Kconfig and the presence of `atc.c`.

Risks and test signals: Build tests should verify module name generation, `M=drivers/phy/apple` partial builds, and that future source splits add to `phy-apple-atc-y` rather than replacing the composite target.
