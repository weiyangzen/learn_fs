<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/sriov.h

## Purpose
Provides inline netdevice SR-IOV wrapper functions for the Siena driver variant, translating Linux `ndo_set_vf_*` calls into NIC type operations when `CONFIG_SFC_SIENA_SRIOV` is enabled.

## Important APIs, Types, And Functions
- Inline wrappers: `efx_sriov_set_vf_mac()`, `efx_sriov_set_vf_vlan()`, `efx_sriov_set_vf_spoofchk()`, `efx_sriov_get_vf_config()`, and `efx_sriov_set_vf_link_state()`.
- VLAN validation enforces `VLAN_VID_MASK`, `VLAN_PRIO_MASK`, and only `ETH_P_8021Q` protocol.

## Control Flow
Each wrapper obtains `struct efx_nic *` with `netdev_priv()`, checks whether the current NIC type supplies the relevant SR-IOV operation, validates wrapper-level arguments when needed, and returns `-EOPNOTSUPP`, `-EINVAL`, or `-EPROTONOSUPPORT` before dispatch when unsupported or invalid.

## State And Persistence Behavior
The header owns no state. It gates access to per-NIC SR-IOV state owned by the underlying NIC type implementation.

## Dependencies And Integration Points
Integrated directly with Siena `net_device_ops` and the `siena_a0_nic_type` SR-IOV function pointers. It depends on VLAN and Ethernet protocol definitions from kernel networking headers through `net_driver.h`.

## Risks And Test Signals
Because wrappers are inline and compiled only under `CONFIG_SFC_SIENA_SRIOV`, disabled builds must not reference missing symbols. Test signals include netlink VF MAC/VLAN/spoof-check/config calls returning expected validation errors and dispatching to Siena-specific handlers when VFs are initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/sriov.h -->
