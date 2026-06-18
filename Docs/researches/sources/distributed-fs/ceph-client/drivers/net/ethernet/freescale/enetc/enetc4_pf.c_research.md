# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_pf.c

## Purpose
Implements the ENETC rev 4.x physical-function PCI driver. It discovers NETC/ENETC4 port capabilities, configures SI/VSI resources, initializes NTMP command access, creates the PF netdev, wires phylink/MDIO, and handles generation-specific MAC filtering, VLAN promiscuity, loopback, pause, speed, and graceful MAC stop/start.

## Important APIs, Types, and Functions
Important entry points are `enetc4_pf_probe`, `enetc4_pf_remove`, `enetc4_pf_init`, `enetc4_pf_netdev_create`, `enetc4_link_init`, and the `enetc4_ndev_ops` netdev operations. Capability and resource setup is split across `enetc4_get_port_caps`, `enetc4_default_rings_allocation`, `enetc4_set_si_msix_num`, and `enetc4_configure_port_si`. MAC receive-mode programming uses `enetc4_psi_do_set_rx_mode`, `enetc4_pf_set_uc_exact_filter`, MAFT helpers, and hash-filter fallback. Phylink callbacks are `enetc4_pl_mac_config`, `enetc4_pl_mac_link_up`, and `enetc4_pl_mac_link_down`.

## Control Flow
Probe calls generic `enetc_pci_probe`, verifies PF-only register blocks, reads revision and driver data, initializes `struct enetc_pf`, programs MAC addresses, creates the NTMP CBDR, configures port/SI defaults, gets SI capabilities, allocates and registers a netdev, then creates debugfs. Link-up control programs port speed, RGMII/RMII fixed speed when in-band autoneg is absent, half-duplex flow control, pause thresholds, and enables RX/TX. Link-down performs graceful RX and TX stops with polling for empty MAC queues.

## State and Persistence
Persistent hardware state includes primary MAC registers, SI ring counts, MSI-X allocation registers, VLAN/MAC promiscuity bits, PM/IF mode registers, port speed, pause thresholds, MAFT entries, RSS key/table, and NTMP command ring registers. Software state is stored in `struct enetc_pf` capabilities and `num_mfe`, `struct enetc_si` workqueue and NTMP user, and `struct enetc_ndev_priv` speed/offload/link data.

## Dependencies and Integration Points
Depends on generic ENETC PCI/SI setup in `enetc.c`, common PF helpers in `enetc_pf_common.c`, register definitions in `enetc4_hw.h` and `enetc_hw.h`, NTMP functions from `ntmp.c`, phylink, MDIO bus helpers, clocks, debugfs, and the driver-data table selecting `enetc4_pf_ethtool_ops` or PPM ethtool ops. It expects `netc_blk_ctrl.c` platform initialization to have configured NETCMIX/IERB before PCI child probing on i.MX NETC systems.

## Risks
Risk concentrates around resource partitioning math for rings/MSI-X, MAFT update windows, async receive-mode work running during teardown, pseudo-MAC handling, link-down graceful-stop timeouts, and different register layouts between ENETC4 PF and PPM devices. `cancel_work` rather than `cancel_work_sync` in destroy depends on workqueue teardown ordering.

## Test Signals
Useful signals are PF probe/remove, link mode matrix tests for RGMII/RMII/SGMII/XGMII/USXGMII, `ip link set promisc/allmulti`, unicast list overflow to hash fallback, VLAN filter toggling, loopback feature toggling, ethtool RSS operations through NTMP, debugfs MAFT visibility, suspend/resume after NETC block reinit, and traffic tests around link down/up transitions.
