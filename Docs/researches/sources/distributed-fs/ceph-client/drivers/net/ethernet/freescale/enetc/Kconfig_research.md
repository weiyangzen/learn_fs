# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Kconfig

Purpose: Declares Kconfig symbols for the NXP/Freescale ENETC and NETC Ethernet driver family. It controls which common libraries, PF/VF drivers, MDIO/PTP/QoS helpers, ENETC4 support, and NETC block-control modules can be built.

Important symbols: `FSL_ENETC_CORE` builds shared ENETC core functionality. `NXP_ENETC_PF_COMMON` builds shared PF code across controller versions. `NXP_NETC_LIB` provides NTMP, tc flower, and debugfs support selected by `NXP_NTMP`. `FSL_ENETC` selects the original ENETC PF driver and dependencies such as PCI MSI, phylink, PCS Lynx, MDIO, IERB, DIMLIB, and core code. `NXP_ENETC4` selects ENETC revision 4 PF support and NTMP. `FSL_ENETC_VF`, `FSL_ENETC_IERB`, `FSL_ENETC_MDIO`, `FSL_ENETC_PTP_CLOCK`, `FSL_ENETC_QOS`, and `NXP_NETC_BLK_CTRL` gate the VF, IERB, MDIO, PTP clock, TSN QoS, and NETC block control modules.

Control flow and state: Kconfig has no runtime flow. Its state is build-time configuration, which determines object inclusion and whether runtime code has PTP, QoS, NTMP, debugfs, phylink, or MDIO support.

Dependencies and integration points: Integrates with kernel networking, PCI MSI, PTP, phylink, PHYLIB, MDIO, DIMLIB, traffic control schedulers, and NETC timer support. Selected symbols align with object lists in the ENETC `Makefile`.

Risks: Missing dependencies cause link failures or unavailable runtime features. `FSL_ENETC_PTP_CLOCK` defaults to y when ENETC PF or VF and QorIQ PTP are available, so timestamp behavior can vary by kernel config. `FSL_ENETC_QOS` is bool and depends on selected qdisc support, so TSN code may compile out even when hardware supports it.

Test signals: `olddefconfig`/`allyesconfig` build coverage, module build checks for each advertised module name, and runtime smoke tests for PF, VF, ENETC4, MDIO, PTP, QoS, and block-control combinations.
