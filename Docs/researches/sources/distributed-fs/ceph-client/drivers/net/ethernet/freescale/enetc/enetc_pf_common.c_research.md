# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf_common.c

## Purpose
Provides generation-neutral PF helper code for MAC address setup, netdev feature initialization, MDIO bus creation/destruction, phylink creation/destruction, default RSS key setup, and VLAN hash filter maintenance.

## Important APIs, Types, and Functions
Exports `enetc_pf_set_mac_addr`, `enetc_setup_mac_addresses`, `enetc_pf_netdev_setup`, `enetc_mdiobus_create`, `enetc_mdiobus_destroy`, `enetc_phylink_create`, `enetc_phylink_destroy`, `enetc_set_default_rss_key`, `enetc_vlan_rx_add_vid`, and `enetc_vlan_rx_del_vid`. Important internals are `enetc_setup_mac_address`, `enetc_mdio_probe`, `enetc_imdio_create`, `enetc_port_has_pcs`, `enetc_vid_hash_idx`, and `enetc_set_si_vlan_ht_filter`.

## Control Flow
MAC setup tries device-tree MAC, then hardware-programmed MAC, then random MAC, and writes it back through PF ops. Netdev setup initializes standard offload features, ethtool ops, MTU, XDP features for rev1, active offload flags, and optional PSFP hardware TC feature. MDIO creation registers an external child MDIO bus if present and creates an internal MDIO/PCS bus when the PHY interface requires PCS. VLAN add/delete updates active VLAN bitmap, recomputes the 64-bit VLAN hash, and writes rev1 or rev4 SI hash registers.

## State and Persistence
Persistent hardware state includes primary MAC addresses, RSS hash key, MDIO controller registration, internal PCS device, phylink instance, and VLAN hash filters. Software state includes `priv` netdev fields, feature flags, `pf->mdio`, `pf->imdio`, `pf->pcs`, `pf->active_vlans`, and `pf->vlan_ht_filter`.

## Dependencies and Integration Points
Depends on PF operation hooks from `enetc_pf.h`, MDIO callbacks from `enetc_mdio.c`, Lynx PCS creation through PF ops, Open Firmware helpers, phylink, netdev features, ethtool ops, and revision helpers. Used by both rev1 PF and ENETC4 PF.

## Risks
Risk areas include inconsistent MAC address source priority, failure unwinding when internal PCS creation fails after external MDIO registration, unsupported PCS on interfaces that require it, VLAN hash collisions inherent in the 64-entry filter, and enabling advanced features only on supported revisions.

## Test Signals
Probe with DT MAC, bootloader MAC, and missing MAC; external MDIO child present/absent; PCS-required and non-PCS PHY modes; VLAN add/delete/filter toggling; rev1/rev4 VLAN hash register selection; and netdev feature advertisement for RSS, loopback, XDP, PSFP, and checksum/TSO offloads.
