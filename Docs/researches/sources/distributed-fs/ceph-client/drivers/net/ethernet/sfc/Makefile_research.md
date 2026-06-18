# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Makefile

Purpose: Defines object composition for the main `sfc` module and optional Solarflare subdrivers.

Important APIs and flow: `sfc-y` lists the core object files for EF10/EF100, channels, NIC, TX/RX, selftest, ethtool, PTP, MCDI, filters, monitoring, devlink, and reflash. `sfc-$(CONFIG_SFC_MTD)` adds MTD support. `sfc-$(CONFIG_SFC_SRIOV)` adds SR-IOV, representor, MAE, TC, counter, encapsulation, and conntrack support. `obj-$(CONFIG_SFC)` builds `sfc.o`, while Falcon and Siena directories are delegated to their own sub-Makefiles.

State and dependencies: It depends on Kconfig symbols from `sfc/Kconfig` and source files in the same directory. Link order matters because the single `sfc.o` aggregates many feature areas.

Risks and test signals: Adding a source without the right Kconfig guard can break non-SRIOV or non-MTD builds. Build tests should cover minimal SFC, SFC with MTD, SFC with SR-IOV/TC, built-in/module modes, and Falcon/Siena enabled independently.
