<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.c

## Purpose
Implements generic SFC netdevice SR-IOV operation wrappers that validate Linux netlink inputs and dispatch to the active NIC type's VF management callbacks.

## Important APIs, Types, And Functions
- Exported wrappers: `efx_sriov_set_vf_mac()`, `efx_sriov_set_vf_vlan()`, `efx_sriov_set_vf_spoofchk()`, `efx_sriov_get_vf_config()`, and `efx_sriov_set_vf_link_state()`.
- VLAN wrapper validates VID, QoS, and `ETH_P_8021Q` protocol before dispatch.

## Control Flow
Each function obtains `struct efx_nic *` with `efx_netdev_priv()`, checks the corresponding function pointer in `efx->type`, and either calls it or returns `-EOPNOTSUPP`. VLAN setup returns `-EINVAL` for out-of-range VID/QoS and `-EPROTONOSUPPORT` for non-802.1Q VLAN protocol.

## State And Persistence Behavior
This file does not store state. It is a dispatch/validation layer over NIC-specific SR-IOV state.

## Dependencies And Integration Points
Included in netdev ops for non-Siena SFC drivers and depends on `nic.h` type callbacks. It parallels the Siena inline wrapper header but is a compiled object under `CONFIG_SFC_SRIOV`.

## Risks And Test Signals
The wrappers only validate common input and rely on NIC implementations for VF index/lifetime checks. Test signals include netlink VF operations returning correct errors on unsupported NICs, invalid VLAN data, unsupported VLAN protocols, and successful dispatch on NICs that populate the callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.c -->
