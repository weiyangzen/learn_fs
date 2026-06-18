# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-bcma.c

Purpose: Implements the BCMA bus front-end for the shared Broadcom GMAC core driver. It discovers BCMA GMAC cores, derives MAC/PHY resources from DT or SPROM, sets feature flags by chip/revision/package, registers optional MDIO, and delegates netdev operation to `bgmac.c`.

Important APIs/functions: Bus callback shims include `bcma_bgmac_read/write()`, IDM accessors, clock enable, chipcommon maskset, bus clock, and common-core PHY control. `bcma_phy_connect()` tries DT `of_phy_get_and_connect()`, then registered MDIO by SPROM PHY address, then fixed PHY. `bgmac_probe()` performs all BCMA-specific setup and calls `bgmac_enet_probe()`. `bgmac_remove()` unregisters MDIO and shared netdev. Module init/exit register a `bcma_driver`.

Control flow: Probe allocates `struct bgmac`, reads MAC address from DT or SPROM, validates common core availability, derives `phyaddr`, possibly registers MDIO, rejects unsupported PCI host setup, computes feature flags, installs callback table, then enters the shared probe. Removal reverses MDIO and shared driver state.

State/persistence: State added here lives inside the shared `struct bgmac`: `bcma.core`, `bcma.cmn`, `dma_dev`, IRQ, `phyaddr`, `has_robosw`, feature flags, callback pointers, and possibly `mii_bus`. SPROM/NVRAM-derived hardware policy persists for the device lifetime.

Dependencies/integration: Integrates Linux BCMA, SPROM, bcm47xx NVRAM indirectly through `bgmac.c`, Broadcom PHY flags, OF net/MDIO, phylib, and exported shared `bgmac` APIs.

Risks/test signals: Feature flag selection is chipset-specific and high risk for regressions. Probe error paths must unregister MDIO correctly. Test DT MAC fallback, SPROM MAC/PHY selection for core units 0-2, BCM4706 common-core path, BCM53573 PHY flags, roboswitch-warning path, module unload, and traffic after suspend/resume via shared core.
