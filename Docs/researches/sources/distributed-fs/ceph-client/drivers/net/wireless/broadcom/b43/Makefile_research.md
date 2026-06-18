# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Makefile

This Makefile composes the `b43.o` driver from mandatory and optional objects. Mandatory objects include `main.o`, `bus.o`, `phy_common.o`, `sysfs.o`, `xmit.o`, `dma.o`, `pio.o`, `rfkill.o`, and `ppr.o`. Optional groups add G-PHY (`phy_g.o tables.o lo.o wa.o`), N-PHY tables/radios/PHY, LP-PHY, HT-PHY, LCN, AC, LED, SDIO, and debugfs support.

kbuild expands `b43-y` and `b43-$(CONFIG_...)` according to `.config`, links selected objects into `b43.o`, then builds it in or as `b43.ko` through `obj-$(CONFIG_B43) += b43.o`. There is no runtime state in this file.

The Makefile integrates tightly with `b43/Kconfig` and source-level optional stubs. Risks are missing optional objects, including feature code without its dependencies, or grouping code under the wrong config. Test signals are modpost/compile success across feature combinations and expected presence/absence of optional objects.
