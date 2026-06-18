# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.c

## Purpose
`wx_sriov.c` implements the PF-side SR-IOV control plane shared by Wangxun PF drivers. It enables and disables PCI SR-IOV, allocates per-VF state, configures VMDq pool layout, handles PF/VF mailbox requests, applies VF MAC/VLAN/multicast/MACVLAN/link policy, and broadcasts PF link state changes to active VFs.

## Important APIs, Types, and Functions
Public exports are `wx_disable_sriov()`, `wx_pci_sriov_configure()`, `wx_msg_task()`, `wx_disable_vf_rx_tx()`, `wx_ping_all_vfs_with_link_status()`, and `wx_set_all_vfs()`. Internal setup helpers include `__wx_enable_sriov()`, `wx_alloc_vf_macvlans()`, `wx_sriov_clear_data()`, and `wx_sriov_reinit()`. Mailbox handlers include `wx_vf_reset_msg()`, `wx_rcv_msg_from_vf()`, `wx_set_vf_mac_addr()`, `wx_set_vf_multicasts()`, `wx_set_vf_vlan_msg()`, `wx_set_vf_macvlan_msg()`, `wx_negotiate_vf_api()`, `wx_get_vf_queues()`, `wx_get_vf_link_state()`, `wx_get_fw_version()`, and `wx_update_vf_xcast_mode()`.

## Control Flow
`wx_pci_sriov_configure()` dispatches zero VF requests to disable and positive requests to `wx_pci_sriov_enable()`. Enable rejects active custom RXFH configuration, initializes VF state, sets VMDq/SR-IOV flags, programs VT count, resets traffic classes through `setup_tc()`, then calls `pci_enable_sriov()`. Disable refuses assigned VFs, calls `pci_disable_sriov()`, clears shared state, and reinitializes queues.

At runtime `wx_msg_task()` scans every configured VF for reset, message, and ack events. A VF reset replays PF VLAN, L2 receive mode, TX/RX enable, MAC filter, mailbox clear-to-send, and response payload. Normal messages are rejected until clear-to-send is established, then routed by opcode and acknowledged or nacked. Link state changes mark the VF not clear-to-send, ping it, and update VF TX/RX enable registers.

## State and Persistence Behavior
State is runtime-only in `struct wx`: `num_vfs`, `vfinfo`, `vf_mvs`, `mv_list`, `ring_feature[RING_F_VMDQ]`, PF flags, default priority, and hardware filter tables/registers. Hardware settings persist only until reset/remove. No disk persistence exists. The clear-to-send bit is the mailbox gate used to keep VFs from configuring before PF reset setup completes.

## Dependencies and Integration Points
The file depends on `wx_type.h` register definitions and `struct wx`, common hardware filter helpers (`wx_add_mac_filter`, `wx_del_mac_filter`, `wx_set_vfta`, `wx_set_rx_mode`), mailbox helpers from `wx_mbx.h`, PCI SR-IOV core APIs, rtnl/netdev TC APIs, VLAN definitions, and PF driver callbacks such as `wx->setup_tc`. PF drivers wire it through `.sriov_configure`, interrupt mailbox causes, and link notifications.

## Risks and Edge Cases
`__wx_enable_sriov()` leaks `vfinfo` if `wx_alloc_vf_macvlans()` fails unless callers unwind with `wx_sriov_clear_data()`. `wx_write_qde()` clears bits using `reg &= qde << i`; for `qde == 0` this clears the whole local register value, so queue disable behavior should be reviewed against hardware intent. Mailbox message sizes reuse the maximum mailbox buffer even for short replies. Promiscuous PF VLAN sharing has subtle cleanup logic that must preserve other pool membership. The shared-vector special case for seven `ngbe` VFs affects interrupt allocation.

## Test Signals
Exercise SR-IOV enable/disable with 0, 1, maximum, assigned, and failed `pci_enable_sriov()` cases; verify RXFH blocking. Test VF reset mailbox handshake, MAC set denial after PF-set MAC, VLAN add/remove with PF promiscuous mode, multicast hash programming, MACVLAN exhaustion, xcast transitions, and link enable/disable. Reset and remove tests should verify `vfinfo`, MACVLAN lists, VMDq offsets, RSC flags, and VF TX/RX enable registers are restored.
