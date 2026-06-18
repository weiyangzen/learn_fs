# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_pf.c

### Purpose
`qlcnic_sriov_pf.c` implements PF-side SR-IOV control. It enables/disables PCI VFs, allocates and configures PF/VF vports, partitions firmware resources, proxies validated VF mailbox commands, handles VF FLR cleanup, and exposes netdev VF administration for MAC, VLAN, spoof-check, and rate limits.

### Important APIs, Types, And Functions
Important entry points are `qlcnic_pci_sriov_configure()`, `qlcnic_sriov_pf_cleanup()`, `qlcnic_sriov_pf_disable()`, `qlcnic_sriov_pf_process_bc_cmd()`, `qlcnic_sriov_pf_handle_flr()`, `qlcnic_sriov_pf_reset()`, `qlcnic_sriov_pf_reinit()`, `qlcnic_sriov_set_vf_mac()`, `qlcnic_sriov_set_vf_vlan()`, `qlcnic_sriov_set_vf_tx_rate()`, `qlcnic_sriov_get_vf_config()`, and `qlcnic_sriov_set_vf_spoofchk()`. Internal handler tables whitelist back-channel commands and firmware mailbox commands.

### Control Flow
Enable checks MSI-X, brings the interface down under RTNL, sets SR-IOV PF opmode, initializes SR-IOV state, creates the FLR workqueue, enables VLAN filtering/eswitch/vport/back-channel events, allocates VLAN arrays, restores the interface, and calls `pci_enable_sriov()`. Disable refuses assigned VFs, disables PCI SR-IOV, brings the interface down, frees VLANs, tears down PF SR-IOV state, reconfigures normal opmode, and restores the interface. VF channel init creates a VF vport, assigns default resources/ACL, and marks the VF channel active; channel term clears VLAN state and destroys the vport.

### State, Persistence, And Dependencies
PF state lives in `qlcnic_sriov`, `qlcnic_vport`, per-VF context IDs, VLAN arrays, and PF opmode flags. Dependencies include PCI SR-IOV APIs, qlcnic mailbox commands for vport/NIC/eswitch/MAC-VLAN/context programming, RTNL/netdev lifecycle functions, FLR workqueues, and the common back-channel transaction engine.

### Integration Points
The file is the policy gate for VF requests sent through `qlcnic_sriov_common.c`. It validates VF context IDs, vport handles, interrupt configuration, MTU, RSS, LRO, interrupt coalescing, MAC/VLAN operations, guest VLAN commands, and allowed passthrough commands before issuing firmware mailbox commands as the PF.

### Risks
Resource partitioning arithmetic must leave enough queues and filters for PF and VFs. VF mailbox validation is the security boundary; missing checks could let a VF operate on another function's vport or context. FLR and soft-FLR paths cancel work and delete contexts while mailbox traffic may be in flight. Netdev VF attribute changes are rejected while the VF driver is loaded, so state consistency depends on `QLC_BC_VF_STATE`.

### Test Signals
Exercise enable/disable success and rollback, assigned-VF disable rejection, VF channel init/term, all whitelisted mailbox handlers with invalid context/vport inputs, hardware and soft FLR, PF reset/reinit, VF MAC duplicate checks, VLAN modes including guest/PVID/no VLAN, spoof-check, rate validation, and `ip link show` VF config reporting.
