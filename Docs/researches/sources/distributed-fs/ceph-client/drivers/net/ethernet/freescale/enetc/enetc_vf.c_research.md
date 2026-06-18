# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_vf.c

## Purpose
Implements the ENETC virtual-function PCI netdev driver. It initializes a VF SI, configures shared SI resources, exposes basic netdev/ethtool operations, and sends mailbox requests to the PF for primary MAC address changes.

## Important APIs, Types, and Functions
Important functions are `enetc_vf_probe`, `enetc_vf_remove`, `enetc_vf_netdev_setup`, `enetc_vf_set_mac_addr`, `enetc_msg_vsi_send`, `enetc_msg_vsi_set_primary_mac_addr`, and `enetc_vf_setup_tc`. It defines VF `net_device_ops` and `enetc_vsi_ops` for legacy RSS table access.

## Control Flow
Probe performs generic PCI SI setup, fixes revision to ENETC rev1, reads driver data/capabilities, allocates the netdev, initializes features, ring parameters, CBDR, SI resources, hardware SI configuration, MSI-X vectors, registers netdev, and starts with carrier off. MAC changes allocate a coherent mailbox message, populate command header/action and sockaddr, wait for mailbox availability, install the DMA message pointer, trigger send, poll completion, and apply the netdev MAC on success. Remove unregisters, frees MSI-X/resources/CBDR/netdev, removes PCI state, and frees the last saved mailbox DMA buffer.

## State and Persistence
Hardware state includes SI registers, BDR/CBDR configuration, mailbox send registers, RSS/RFS tables, and VF primary MAC programmed by the PF. Software state includes `si->msg` for the last DMA message, netdev features, ring resources, interrupt vectors, and classifier/RSS state inherited from common code.

## Dependencies and Integration Points
Depends on the PF mailbox implementation, generic ENETC PCI/SI/resource code, CBDR legacy commands, ethtool VF ops, hwtstamp helpers, mqprio offload, and PF-assigned SI capabilities. It does not manage phylink because link ownership belongs to the PF.

## Risks
Mailbox polling can time out, PF may reject commands, and freeing the previous message before sending the next assumes hardware is no longer using it after mailbox status clears. VF revision is hard-coded to rev1. Failure unwinding must free CBDR and netdev state in the right order.

## Test Signals
Create VFs through PF SR-IOV, probe/remove VF driver, set VF MAC from the guest/host, test busy and timeout mailbox behavior, run traffic with VLAN/checksum/TSO/RSS, configure mqprio, inspect ethtool VF stats/RSS, and unload VF while a previous mailbox buffer exists.
