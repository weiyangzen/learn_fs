# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.c

## Purpose
`ixgbe_sriov.c` implements SR-IOV PF-side management for ixgbe. It enables and disables VFs, allocates per-VF policy state, handles PCI SR-IOV configuration, dispatches VF mailbox commands, programs VF MAC/VLAN/multicast/RSS/link/rate/spoofing state, reacts to VF resets and malicious driver detection, and exposes netdev `ndo_set_vf_*` controls.

## Important APIs and functions
SR-IOV lifecycle functions include `ixgbe_enable_sriov`, `__ixgbe_enable_sriov`, `ixgbe_disable_sriov`, `ixgbe_pci_sriov_configure`, `ixgbe_pci_sriov_enable`, and `ixgbe_pci_sriov_disable`. VF device references are tracked by `ixgbe_get_vfs`, and extra VF MACVLAN filter storage is allocated by `ixgbe_alloc_vf_macvlans`.

Mailbox handling centers on `ixgbe_msg_task`, `ixgbe_rcv_msg_from_vf`, `ixgbe_vf_reset_msg`, `ixgbe_rcv_ack_from_vf`, `ixgbe_ping_vf`, and `ixgbe_ping_all_vfs`. Command handlers cover VF MAC, multicast, VLAN, LPE/MTU, MACVLAN, API negotiation, queue discovery, RETA/RSS key reads, xcast mode, link state, PF link state, feature negotiation, and IPsec SA add/delete.

Administrative netdev APIs include `ixgbe_ndo_set_vf_mac`, `ixgbe_ndo_set_vf_vlan`, `ixgbe_ndo_set_vf_bw`, `ixgbe_ndo_set_vf_spoofchk`, `ixgbe_ndo_set_vf_rss_query_en`, `ixgbe_ndo_set_vf_trust`, `ixgbe_ndo_get_vf_config`, and `ixgbe_ndo_set_vf_link_state`. Helper functions program hardware state in VFTA/VLVF/VLVFB, VMVIR, VMOLR, VFTE/VFRE, QDE, MAC filters, MTA multicast tables, and rate-control registers.

## Control flow
Enabling SR-IOV rejects XDP coexistence, sets SR-IOV/VMDq flags, allocates `adapter->vfinfo`, initializes default VF policy, sets VMDq offsets, enables VEB switching, limits traffic classes based on VF count, disables RSC, optionally creates PCI VFs, resets/reinitializes the adapter, and takes references to VF PCI devices. Disabling first sets `num_vfs` to zero under `vfs_lock`, releases VF PCI references, frees `vfinfo` and MACVLAN storage, disables MDD and PCI SR-IOV where safe, updates VMDq/RSS limits, and waits for cleanup.

The mailbox task first checks MDD, then under `vfs_lock` scans each VF for reset, message, and ACK events. Reset events clear VLANs and multicast state, restore PF-assigned VLANs, reset offloads and anti-spoofing, clear IPsec state and MACVLAN filters, reset API revision, restart VF queues, clear the mailbox, program VF MAC, enable drop behavior, set clear-to-send, and reply with ACK/NACK plus the permanent MAC payload. Non-reset messages are rejected until `clear_to_send` is true. After dispatch, the PF replies with ACK or NACK plus CTS.

Administrative `ndo_set_vf_*` calls validate VF index and arguments, update `adapter->vfinfo`, program hardware filters/registers, and often require VF reload or ping/reset to apply. Trust and link-state changes clear `clear_to_send` and ping the VF so the guest rebuilds state.

## State and persistence
Core runtime state is in `adapter->num_vfs`, `adapter->vfinfo[]`, `adapter->vf_mvs`, `adapter->mv_list`, `adapter->flags`, `adapter->flags2`, `adapter->ring_feature`, `adapter->bridge_mode`, `adapter->dcb_cfg`, `adapter->vf_rate_link_speed`, `adapter->fwd_bitmask`, and `adapter->vfs_lock`. Per-VF state includes MAC address, PF-set MAC flag, PF VLAN/QoS, spoof checking, trust, RSS-query permission, link state/link enable, xcast mode, TX rate, multicast hashes, VF API revision, clear-to-send, and PCI VF device pointer. Hardware state persists in filter tables and VF enable/drop/rate/spoofing registers until reset or explicit cleanup.

## Dependencies and integration points
The file depends on PCI SR-IOV APIs, Linux netdev VF configuration APIs, mailbox transport from `ixgbe_mbx.c`, ixgbe MAC ops for anti-spoofing/MDD/VFTA, core filter helpers such as `ixgbe_add_mac_filter`, `ixgbe_del_mac_filter`, `ixgbe_set_rx_mode`, `ixgbe_full_sync_mac_table`, VLAN promisc helpers, IPsec VF helpers, DCB/traffic-class state, XDP state, and reset/reinit paths such as `ixgbe_sriov_reinit`.

## Risks and edge cases
SR-IOV state spans PCI, PF software, VF software, and hardware tables. Risks include races with VF teardown, freeing `vfinfo` while events are pending, inability to disable assigned VFs, mailbox commands before reset completion, RAR/MTA/VLVF exhaustion, stale PF-assigned VLAN restrictions, anti-spoofing interactions with MACVLAN filters, link-speed changes invalidating rate limits, and MDD recovery requiring guest VF queue rebuild. XDP and SR-IOV are explicitly incompatible here.

## Test signals
Validation should cover enabling/disabling VFs via module parameter and PCI sysfs, pre-existing VF adoption, assigned VF disable failure, VF reset handshake, every mailbox opcode with ACK/NACK paths, admin MAC/VLAN/link/trust/spoof/RSS/rate changes, VF reload requirements, multicast restore after PF multicast changes, VLAN table cleanup, max VF limits under 1/4/8 traffic classes and offloaded macvlans, MDD detection/restoration, XDP rejection, and rate-limit disable after link-speed changes.
