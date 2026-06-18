# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-nuss.h

## Purpose
Defines the shared data model and public interface for the AM65 CPSW NUSS driver cluster. The header is the contract between the main platform/netdev driver, QoS offload code, switchdev offload code, ethtool support, and CPTS timestamp integration.

## Important APIs, Types, and Functions
Key types are `struct am65_cpsw_common`, `struct am65_cpsw_port`, `struct am65_cpsw_host`, `struct am65_cpsw_slave_data`, `struct am65_cpsw_tx_chn`, `struct am65_cpsw_rx_chn`, `struct am65_cpsw_rx_flow`, `struct am65_cpsw_tx_swdata`, `struct am65_cpsw_swdata`, `struct am65_cpsw_pdata`, `struct am65_cpsw_devlink`, and `struct am65_cpsw_ndev_priv`. Public helpers/macros include netdev-to-private conversions, common port accessors, NAPI container helpers, `AM65_CPSW_IS_CPSW2G`, `am65_cpsw_nuss_set_p0_ptype`, `am65_cpsw_nuss_update_tx_rx_chns`, and `am65_cpsw_port_dev_check`.

## Control Flow
There is no executable control flow beyond macros and declarations. The file shapes runtime flow by defining ownership boundaries: `am65_cpsw_common` is shared platform state, `am65_cpsw_port` is per-external-port netdev/MAC state, `am65_cpsw_tx_chn` and `am65_cpsw_rx_chn` are DMA resources, and `am65_cpsw_ndev_priv` is the per-netdev bridge between Linux netdev callbacks and driver internals.

## State and Persistence
The header identifies which state survives across callbacks and suspend/resume. `am65_cpsw_common` persists port count, base addresses, ALE, DMA channels, CPTS pointer, EST/IET enable flags, switch/emac mode, bridge membership, default VLAN, switch id, and ALE context. `am65_cpsw_port` persists timestamp filter bits, QoS state, devlink port, XDP program, and VLAN context. Descriptor software data persists only while a DMA descriptor is owned by hardware or completion cleanup.

## Dependencies and Integration Points
Includes kernel netdevice/phylink/platform/devlink/XDP/K3 ring headers and `am65-cpsw-qos.h`, and forward-declares `struct am65_cpts`. It is consumed by `am65-cpsw-nuss.c`, `am65-cpsw-qos.c`, `am65-cpsw-switchdev.c`, ethtool code, and optional switchdev/CPTS modules.

## Risks and Test Signals
ABI drift in this header affects every module in the cluster. Risks include descriptor swdata size exceeding CPPI software-data limits, queue count assumptions exceeding `AM65_CPSW_MAX_QUEUES`, stale suspend context fields, and conditional feature fields being accessed when support is disabled. Test signals are all config combinations for QoS/CPTS/switchdev, `BUILD_BUG_ON` checks in the main file, sparse/smatch structure-use warnings, and runtime queue/XDP/timestamp exercises.
