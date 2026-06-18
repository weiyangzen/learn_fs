# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_common.c

### Purpose
`qlcnic_sriov_common.c` provides the common PF/VF SR-IOV infrastructure, with most VF-side behavior. It initializes SR-IOV state, implements the back-channel mailbox transaction engine, installs VF hardware/nic ops, handles VF firmware reset polling, and manages VF guest VLAN tracking.

### Important APIs, Types, And Functions
Public functions include `qlcnic_sriov_init()`, `qlcnic_sriov_cleanup()`, `qlcnic_sriov_vf_init()`, `qlcnic_sriov_vf_set_ops()`, `qlcnic_sriov_vf_register_map()`, `qlcnic_sriov_handle_bc_event()`, `qlcnic_sriov_cfg_bc_intr()`, `qlcnic_sriov_vf_set_multi()`, and VLAN allocation/add/delete helpers. Core internals include `qlcnic_sriov_prepare_bc_hdr()`, `__qlcnic_sriov_send_bc_msg()`, `qlcnic_sriov_process_bc_cmd()`, `__qlcnic_sriov_issue_cmd()`, and the VF IDC state handlers.

### Control Flow
Initialization allocates `qlcnic_sriov`, per-VF records, transaction and async workqueues, list heads, completions, locks, and PF-side default vports where needed. VF bringup waits for device-ready, configures rings and interrupts, creates the back channel, initializes vport/NIC info, fetches ACL/VLAN policy, sets up the netdev, and schedules IDC polling. Mailbox commands are wrapped as back-channel transactions with sequence IDs and fragments; events complete channel-free waits, deliver requests/responses, or schedule FLR handling. VF IDC polling detaches, reinitializes, or fails the VF according to firmware state.

### State, Persistence, And Dependencies
State is in `adapter->ahw->sriov`, per-VF transaction lists, completions, workqueues, async command lists, VLAN arrays, and adapter reset flags. Dependencies include qlcnic 83xx mailbox/register APIs, PCI SR-IOV function mapping, netdev multicast/unicast lists, qlcnic MAC filter helpers, delayed work, and firmware IDC registers.

### Integration Points
VF hardware ops replace normal mailbox command submission with `qlcnic_sriov_issue_cmd()`. PF builds call into `qlcnic_sriov_pf_process_bc_cmd()` for received VF commands. Netdev multicast programming and guest VLAN configuration are integrated with qlcnic MAC filter lists and promiscuous mode programming.

### Risks
The transaction engine is concurrency-sensitive: channel ownership, `send_cmd`, response completions, pending/active lists, async no-wait commands, and FLR cleanup all interact. Timeouts set `need_fw_reset` and clear mailbox readiness, so retry behavior affects VF recovery. VLAN list validation must prevent disallowed or duplicate guest VLAN programming. Cleanup order must flush workqueues before freeing transactions and per-VF memory.

### Test Signals
Test channel init/term, mailbox response timeout, multi-fragment command/response, async no-wait commands, PF reset during VF mailbox traffic, IDC ready/init/quiescent/failed transitions, VF multicast programming with and without guest VLANs, guest VLAN validation, shutdown/resume, and workqueue cleanup under active transactions.
