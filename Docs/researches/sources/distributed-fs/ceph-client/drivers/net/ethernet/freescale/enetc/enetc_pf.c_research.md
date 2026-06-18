# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.c

## Purpose
Implements the original ENETC rev1 PF driver. It initializes PF hardware, partitions resources for VFs, manages MAC/VLAN filters, handles SR-IOV mailbox commands, configures port MAC/phylink behavior, initializes RSS/RFS command memory, and registers the PF netdev.

## Important APIs, Types, and Functions
Important functions include `enetc_pf_probe`, `enetc_pf_remove`, `enetc_psi_create`, `enetc_psi_destroy`, `enetc_configure_port`, `enetc_pf_set_rx_mode`, `enetc_msg_handle_rxmsg`, `enetc_sriov_configure`, `enetc_pf_setup_tc`, `enetc_pl_mac_link_up`, `enetc_pl_mac_link_down`, `enetc_init_port_rfs_memory`, and `enetc_init_port_rss_memory`. It defines `enetc_ndev_ops`, `enetc_mac_phylink_ops`, `enetc_psi_ops`, and `enetc_pf_ops`.

## Control Flow
Probe first attempts IERB registration, creates the PF SI through generic PCI setup and CBDR initialization, clears RFS/RSS tables, initializes PF private state/VF state, sets MAC addresses, configures port/SI registers, allocates netdev resources/MSI-X, reads `phy-mode`, creates MDIO/PCS/phylink, and registers the netdev. Link-up sets Qbv speed, optional forced RGMII speed/duplex, pause behavior, RX BDR congestion mode, MAC pause registers, enables MAC, and notifies MAC Merge. Removal disables SR-IOV, unregisters netdev, destroys phylink/MDIO, frees MSI-X/resources/netdev/VF state, tears down CBDR, and removes PCI state.

## State and Persistence
Hardware state includes primary MAC registers for PF/VFs, SI configuration, RFS/RSS tables, VLAN promisc/isolation/filter registers, exact/hash MAC filters, port MAC mode, flow control, pause thresholds, and port enable. Software state includes VF flags, filter caches, VLAN bitmaps, phylink/PCS/MDIO pointers, capability flags, active offloads, and `num_vfs`.

## Dependencies and Integration Points
Uses common PF helpers, IERB, CBDR, `pcs-lynx`, phylink, MDIO, SR-IOV PCI core, mailbox support in `enetc_msg.c`, QoS offload functions, ethtool ops, XDP and hwtstamp paths from the shared driver. A PCI fixup runs `enetc_psi_create`/destroy for disabled functions to clear RSS/RFS.

## Risks
Risks include resource partitioning for VFs, mailbox MAC override policy, exact-to-hash filter fallback, VLAN isolation errata, phylink PCS creation failures, cleanup ordering across many probe labels, and link-mode assumptions for RGMII/SGMII/USXGMII. CBDR commands are synchronous and can fail mid-probe.

## Test Signals
Exercise PF probe/remove, disabled-device PCI fixup, SR-IOV enable/disable, VF MAC/VLAN/spoofchk controls, unicast/multicast/promisc modes, VLAN filter toggling, link-up/down across supported PHY modes, Qbv/Qbu/CBS/ETF/PSFP setup, RSS/RFS initialization, and IERB absent/deferred cases.
