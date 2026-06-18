# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/vport.c

## Purpose
`vport.c` is the mlx5 core vport command helper layer. It marshals firmware command mailboxes for NIC and HCA vport state, MAC/MTU/filter lists, GUIDs, GID/P_Key tables, promiscuous and local loopback policy, RoCE enablement, vport counters, multiport affiliation, VHCA ID lookup, and other-function HCA capability get/set.

## Important APIs, types, and functions
The file exposes exported helpers such as `mlx5_query_vport_state()`, `mlx5_modify_vport_admin_state()`, `mlx5_modify_vport_max_tx_speed()`, `mlx5_query_nic_vport_mac_address()`, `mlx5_modify_nic_vport_mac_address()`, `mlx5_query_nic_vport_mtu()`, `mlx5_modify_nic_vport_mtu()`, `mlx5_query_nic_vport_mac_list()`, `mlx5_modify_nic_vport_mac_list()`, `mlx5_modify_nic_vport_vlans()`, `mlx5_query_hca_vport_gid()`, `mlx5_query_hca_vport_pkey()`, `mlx5_query_hca_vport_context()`, `mlx5_core_modify_hca_vport_context()`, `mlx5_core_query_vport_counter()`, and `mlx5_vport_get_other_func_cap()`. Shared state is mainly `struct mlx5_core_dev`, `struct mlx5_hca_vport_context`, `mdev->roce.roce_en`, and cached `mdev->sys_image_guid`. Command buffers use generated `MLX5_SET`, `MLX5_GET`, and `MLX5_ADDR_OF` accessors.

## Control Flow and State
Most functions allocate or stack-build an input mailbox, set opcode/op_mod/vport fields, optionally set `other_vport`, execute a firmware command through `mlx5_cmd_exec*()`, and copy selected fields into caller-owned objects. Capability gates protect cross-vport operations: non-manager attempts to query or modify other vports return `-EPERM` or `-EACCES`. List updates size buffers from firmware capability limits and fail with `-ENOSPC` if caller-supplied MAC/VLAN lists exceed supported sizes.

The main persistent behavior is firmware state mutation: vport admin state, speed cap, MAC address, MTU, allowed UC/MC/VLAN lists, promiscuous bits, local loopback disable bits, HCA vport context fields, RoCE enable bit, and multiport affiliation. Software state is small but important: `mlx5_roce_en_lock` serializes RoCE reference count transitions, multiport affiliation enables RoCE before setting affiliation and disables it on unwind, and `mlx5_query_nic_system_image_guid()` caches the queried GUID on `mdev`.

## Dependencies and Integration Points
The file integrates with mlx5 command infrastructure, generated IFC layouts, eswitch helpers for vport-to-function/VHCA ID mapping, SF support, InfiniBand GID/P_Key types, Ethernet address helpers, and exported symbols consumed by mlx5e, eswitch, RDMA, devlink, SR-IOV, and multiport code.

## Risks and Test Signals
Risks include incorrect `other_vport` selection, off-by-one VF/vport/function IDs, capability gating regressions, memory allocation failures in dynamic mailboxes, missed RoCE reference restoration on command failure, and firmware-visible list size mismatches. Useful tests are kernel build coverage, mlx5 probe with PF/VF/SF/eCPF variants, SR-IOV vport state and MAC/MTU changes, UC/MC/VLAN list programming, RoCE enable/disable nesting, multiport affiliate/unaffiliate rollback, devlink/eswitch counter queries, and negative tests for non-manager cross-vport access.
