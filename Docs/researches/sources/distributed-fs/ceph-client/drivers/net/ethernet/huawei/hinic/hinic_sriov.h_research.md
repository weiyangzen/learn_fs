# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.h

## Purpose
Declares original HiNIC SR-IOV state, VF policy records, mailbox payload structures, VF ID conversion macros, and public SR-IOV/netdev operation hooks.

## Important APIs And Types
`OS_VF_ID_TO_HW()` and `HW_VF_ID_TO_OS()` encode the hardware convention that VF IDs start at 1 while Linux-visible VF indexes start at 0. `enum hinic_sriov_state` defines bit positions for enable, disable, and function removal. `struct hinic_sriov_info` tracks the PF PCI device, hardware device, enable state, VF count, and state bits. `struct vf_data_storage` persists per-VF MAC, VLAN/QoS, bandwidth, forced link, spoof-check, trust, and registration fields. Command payloads include `hinic_register_vf`, `hinic_port_mac_update`, and `hinic_vf_vlan_config`.

## Control Flow And State
This header has no executable control flow, but it defines the state consumed by `hinic_sriov.c`. Public prototypes connect netdev VF ops, link notifications, PCI SR-IOV configuration, and VF function init/free into the rest of the driver.

## Dependencies And Integration Points
It includes `hinic_hw_dev.h` for hardware-device structures and is included by `hinic_main.c` and `hinic_sriov.c`. It also relies on Linux netdevice VF structures through function prototypes.

## Risks And Test Signals
The main risk is incorrect VF ID translation or state-bit interpretation, which can apply PF policy to the wrong VF. Structure layout changes affect mailbox ABI. Test signals include VF policy round trips through `ip link`, VF reload with PF-set MAC/VLAN, link forced/auto behavior, and SR-IOV enable/disable races during PF removal.
