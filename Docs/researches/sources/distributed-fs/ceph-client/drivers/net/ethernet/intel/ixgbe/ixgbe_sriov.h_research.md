# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_sriov.h

## Purpose
`ixgbe_sriov.h` declares the PF-side SR-IOV management interface used by the ixgbe core driver and defines VF-count limits for different traffic-class configurations. It also provides a small inline helper for programming VF default VLAN insertion.

## Important APIs and constants
`IXGBE_MAX_VFS_DRV_LIMIT` caps driver-created VFs at one less than the hardware VF function count so the PF retains resources. `IXGBE_MAX_VFS_1TC`, `IXGBE_MAX_VFS_4TC`, and `IXGBE_MAX_VFS_8TC` express VF limits based on traffic-class count.

The header declares SR-IOV lifecycle (`ixgbe_enable_sriov`, `ixgbe_disable_sriov`, `ixgbe_pci_sriov_configure`), mailbox/event work (`ixgbe_msg_task`, `ixgbe_ping_all_vfs`, `ixgbe_set_all_vfs`, `ixgbe_check_mdd_event`), VF PCI callbacks (`ixgbe_vf_configuration`), multicast restore, link/rate helpers, and netdev VF controls for MAC, VLAN, bandwidth, spoof checking, RSS query, trust, config retrieval, and link state.

`ixgbe_set_vmvir` writes `IXGBE_VMVIR(vf)` with VLAN ID, QoS priority, and `IXGBE_VMVIR_VLANA_DEFAULT` to configure VF transmit VLAN insertion.

## Control flow and integration
Core ixgbe probe, remove, reset, watchdog, netdev ops, and PCI SR-IOV callbacks include this header to invoke the implementation in `ixgbe_sriov.c`. The inline VMVIR helper is used by reset and VLAN configuration paths to keep VLAN insertion programming consistent.

## State and persistence
The header has no state. Its APIs manipulate adapter-level VF state and hardware registers through `struct ixgbe_adapter` and `struct ixgbe_hw`. The inline helper directly persists VLAN insertion configuration in the VMVIR hardware register until reset or a later write.

## Dependencies
It relies on ixgbe core type declarations being available before inclusion, including `struct ixgbe_adapter`, `struct pci_dev`, `struct net_device`, and VLAN constants. Some declarations are gated by `CONFIG_PCI_IOV`.

## Risks and edge cases
VF limit constants are policy-sensitive because they protect PF queues and VMDq pool resources. Incorrect VMVIR programming can force wrong VLAN tags on VF traffic. API declarations must stay synchronized with netdev ops and the implementation, especially around `CONFIG_PCI_IOV` builds.

## Test signals
Build tests should cover configurations with and without `CONFIG_PCI_IOV`. Runtime tests should verify VF count rejection at traffic-class limits, correct VMVIR VLAN/QoS insertion, and netdev VF operation wiring through the declarations in this header.
