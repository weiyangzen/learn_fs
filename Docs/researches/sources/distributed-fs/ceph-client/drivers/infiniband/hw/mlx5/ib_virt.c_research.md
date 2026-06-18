# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_virt.c

## Purpose
`ib_virt.c` implements RDMA-core SR-IOV VF management operations for mlx5 IB devices. It lets the PF query or set VF link-state policy, query VF traffic counters, and set/get VF node and port GUIDs.

## Important APIs, Types, And Functions
Public entry points are `mlx5_ib_get_vf_config()`, `mlx5_ib_set_vf_link_state()`, `mlx5_ib_get_vf_stats()`, `mlx5_ib_set_vf_guid()`, and `mlx5_ib_get_vf_guid()`. Helper converters `mlx_to_net_policy()` and `net_to_mlx_policy()` map between mlx5 `enum port_state_policy` and netlink `IFLA_VF_LINK_STATE_*` constants. Private helpers `set_vf_node_guid()` and `set_vf_port_guid()` write the selected GUID field.

## Control Flow
Get-config allocates an HCA vport context, queries `vf + 1` as an "other vport", translates the policy, and fills `struct ifla_vf_info`. Set-link-state validates the requested netlink policy, sets `MLX5_HCA_VPORT_SEL_STATE_POLICY`, modifies the HCA vport context, and mirrors the policy into `mdev->priv.sriov.vfs_ctx[vf]` on success. Stats allocate a firmware output buffer, query vport counters, and map selected unicast and multicast packet/octet counters into `ifla_vf_stats`. GUID setters update firmware and mark cached `node_guid_valid` or `port_guid_valid` in `vfs_ctx`. GUID getter returns cached GUIDs or zero when not valid.

## State And Persistence Behavior
Firmware vport context is the authoritative state for policy and GUID programming. The driver mirrors successful policy/GUID writes into the in-memory SR-IOV VF context under `mdev->priv.sriov.vfs_ctx`. Statistics are queried on demand and not stored.

## Dependencies And Integration Points
These functions are installed in `main.c` as `mlx5_ib_dev_sriov_ops` when the device is a PF. They depend on mlx5 vport commands, `struct mlx5_vf_context`, RDMA `ib_device` container conversion, and Linux netlink VF structures.

## Risks
The file assumes RDMA-core validation of VF index and port arguments; direct misuse could index `vfs_ctx` out of range. Firmware and cache must remain consistent: cache updates occur only after successful modify commands. `mlx5_ib_get_vf_config()` returns `-EINVAL` if firmware returns an unknown policy translation.

## Test Signals
Use PF SR-IOV tests for setting VF link states disable/enable/auto, reading them back, setting node and port GUIDs and verifying cached get behavior, querying stats under traffic, and negative testing invalid policy values and firmware command failures.
