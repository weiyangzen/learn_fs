<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Kconfig

Purpose: Defines the Intel XScale IXP Ethernet vendor menu, the IXP4xx Ethernet MAC driver option, and the optional IXP46x PTP clock support used for hardware timestamping.

Important APIs/types/functions: `NET_VENDOR_XSCALE` is a bool vendor gate depending on `NET_VENDOR_INTEL` and the ARM IXP4xx NPE/QMGR platform pieces. `IXP4XX_ETH` is the tristate Ethernet driver option; it depends on ARM IXP4xx, NPE, QMGR, and OF, and selects `PHYLIB`, `OF_MDIO`, and `NET_PTP_CLASSIFY`. `PTP_1588_CLOCK_IXP46X` is a bool depending on `IXP4XX_ETH` and compatible `PTP_1588_CLOCK` configuration, defaulting to yes.

Control flow: Kconfig exposes XScale IXP drivers only on the correct ARM/IXP4xx platform. Enabling `IXP4XX_ETH` compiles the Ethernet driver and its selected PHY/MDIO/PTP-classify dependencies. Enabling the PTP bool adds the IXP46x PTP clock object through the Makefile.

State and persistence behavior: No runtime state. It encodes build-time availability and ensures timestamp classification support is present for `ixp4xx_eth.c`.

Dependencies and integration points: Integrates the XScale Ethernet directory with the Intel vendor menu, IXP4xx platform NPE and queue manager subsystems, OF platform descriptions, phylib/OF MDIO, and the PTP core.

Risks and test signals: Build matrix should cover `IXP4XX_ETH=y/m/n`, `PTP_1588_CLOCK_IXP46X=y/n`, and PTP core combinations including `PTP_1588_CLOCK=y` or matching module linkage. The PTP option is bool despite help text mentioning a module, so build output should be checked against Makefile behavior. Dependency tests should verify the driver is hidden when NPE/QMGR/OF or `NET_VENDOR_INTEL` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Kconfig -->
