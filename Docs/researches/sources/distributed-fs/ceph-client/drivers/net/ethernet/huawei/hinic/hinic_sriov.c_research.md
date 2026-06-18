# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.c

## Purpose
Implements original HiNIC SR-IOV support for PF and VF roles. It manages VF lifecycle, PF-side VF policy state, mailbox command validation/dispatch, VF registration, forced link state, VF MAC/VLAN/trust/spoof-check/rate settings, and PCI SR-IOV enable/disable.

## Important APIs And Functions
Netdev VF operations are `hinic_ndo_set_vf_mac()`, `hinic_ndo_set_vf_vlan()`, `hinic_ndo_get_vf_config()`, `hinic_ndo_set_vf_trust()`, `hinic_ndo_set_vf_bw()`, `hinic_ndo_set_vf_spoofchk()`, and `hinic_ndo_set_vf_link_state()`. Lifecycle APIs are `hinic_vf_func_init()`, `hinic_vf_func_free()`, `hinic_pci_sriov_configure()`, and `hinic_pci_sriov_disable()`. Mailbox paths use `nic_pf_mbox_handler()`, `cfg_mbx_pf_proc_vf_msg()`, and command-specific handlers for VF register/unregister, MTU, MAC, and link state.

## Control Flow And State
PF init registers mailbox callbacks, allocates `vf_infos`, and applies the module parameter `set_vf_link_state`. VF init registers with the PF over mailbox. Enabling SR-IOV sets the `HINIC_SRIOV_ENABLE` bit, initializes VF WQ page size, calls `pci_enable_sriov()`, records `sriov_enabled` and `num_vfs`, then clears the state bit. Disabling handles assigned-VF refusal, disables PCI SR-IOV, clears hardware settings and VF state, and resets page sizes. `struct vf_data_storage` persists PF-selected MAC, VLAN/QoS, bandwidth, link force, spoof-check, trust, and registration state. PF mailbox dispatch validates commands and function IDs before either handling locally or forwarding to management firmware.

## Dependencies And Integration Points
It integrates PCI SR-IOV APIs, HiNIC mailbox, management command wrappers in `hinic_port.c`, hardware device capability data, and `hinic_main.c` netdev ops. Link events call `hinic_notify_all_vfs_link_changed()` from the main link handler.

## Risks And Test Signals
Risks include OS-VF versus hardware-VF off-by-one conversions, missing bounds checks, inconsistent indexing in trust/spoof state, stale PF policy after VF reload, mailbox validation gaps, and SR-IOV removal races. Tests should cover enabling/disabling varying VF counts, assigned-VF unload refusal, VF register/unregister, PF-set MAC/VLAN/rate/spoof/trust/link policies, VF driver reload, link flap propagation, and older firmware unsupported-command paths.
