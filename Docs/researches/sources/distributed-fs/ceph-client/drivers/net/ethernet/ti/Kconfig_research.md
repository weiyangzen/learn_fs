# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Kconfig

## Purpose
This Kconfig fragment defines the Texas Instruments ethernet driver menu and build options for DaVinci EMAC/MDIO, CPSW, K3 AM65 CPSW NUSS, CPTS timestamping, QoS offload, Keystone NETCP, ThunderLAN, ICSSG, ICSS IEP, and PRU Ethernet drivers.

## Important APIs, Types, and Functions
Important symbols include `NET_VENDOR_TI`, `TI_DAVINCI_EMAC`, `TI_DAVINCI_MDIO`, `TI_CPSW`, `TI_CPSW_SWITCHDEV`, `TI_CPTS`, `TI_K3_CPPI_DESC_POOL`, `TI_K3_AM65_CPSW_NUSS`, `TI_K3_AM65_CPSW_SWITCHDEV`, `TI_K3_AM65_CPTS`, `TI_AM65_CPSW_QOS`, `TI_KEYSTONE_NETCP`, `TI_KEYSTONE_NETCP_ETHSS`, `TLAN`, `TI_ICSSG_PRUETH`, `TI_ICSSG_PRUETH_SR1`, `TI_ICSS_IEP`, and `TI_PRUETH`.

## Control Flow and State
There is no runtime control flow. Build-time state determines which driver objects compile and which helper subsystems are selected. For the researched `am65-cpsw-ethtool.c`, the critical parent is `TI_K3_AM65_CPSW_NUSS`, which selects `NET_DEVLINK`, `TI_DAVINCI_MDIO`, `PHYLINK`, `PAGE_POOL`, and `TI_K3_CPPI_DESC_POOL`; optional timestamping and QoS behavior are controlled by `TI_K3_AM65_CPTS` and `TI_AM65_CPSW_QOS`.

## Dependencies and Integration Points
The file models architecture and subsystem requirements for many TI ethernet families. AM65 CPSW depends on `ARCH_K3`, OF, and TI UDMA glue, and conditionally integrates CPTS and QoS features. ICSSG/PRU options depend on remoteproc, switchdev, PTP optional support, and firmware-running PRU cores.

## Risks and Test Signals
Kconfig risk is dependency skew: missing `select`/`depends on` entries can break randconfig or expose unusable options. Optional QoS and CPTS dependencies affect ethtool code paths for timestamping and MAC Merge/IET. Tests should include randconfig, `COMPILE_TEST` where applicable, AM65 CPSW builds with and without CPTS/QoS/switchdev, and module/built-in combinations for shared objects.
