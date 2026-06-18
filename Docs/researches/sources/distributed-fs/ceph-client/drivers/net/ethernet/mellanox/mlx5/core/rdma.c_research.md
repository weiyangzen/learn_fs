# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.c

## Purpose

`rdma.c` enables and disables the default RoCE support needed by mlx5 when eswitch/RDMA steering is available. It programs the NIC vport RoCE state, installs a default RoCE GID derived from the MAC address, and creates an RDMA RX flow table that allows traffic from the eswitch manager source port.

## Important APIs, Types, and Functions

Public functions are `mlx5_rdma_enable_roce()` and `mlx5_rdma_disable_roce()`. Local helpers are `mlx5_rdma_enable_roce_steering()`, `mlx5_rdma_disable_roce_steering()`, `mlx5_rdma_make_default_gid()`, `mlx5_rdma_add_roce_addr()`, and `mlx5_rdma_del_roce_addr()`. Persistent objects are stored in `dev->priv.roce`: flow table, flow group, and allow rule.

## Control Flow

Enable first checks the generic RoCE capability. It enables RoCE on the NIC vport, constructs and installs a default link-local GID, then creates steering objects. Steering validates RDMA RX flow-table capabilities, allocates flow-group input and flow spec buffers, gets the RDMA RX kernel namespace, creates a one-entry flow table, creates a flow group scoped to source port, and adds an allow rule matching the eswitch manager vport. Any failure unwinds in reverse: destroy flow group/table, delete GID, disable vport RoCE.

Disable is idempotent on `roce->ft`: if steering was not created, it returns. Otherwise it deletes the allow rule, flow group, and flow table, removes the GID, and disables NIC vport RoCE.

## State and Persistence Behavior

Firmware state includes the vport RoCE enable bit, GID table entry 0 for RoCE v2, and RDMA RX flow-table objects. The driver caches the flow objects in `dev->priv.roce` but does not explicitly clear the pointers after destroy in this file, so higher-level lifecycle must prevent double-disable after the objects are destroyed or rely on object memory being cleared elsewhere.

## Dependencies and Integration Points

It depends on `CONFIG_MLX5_ESWITCH`, RDMA verbs `union ib_gid`, IPv6 EUI-48 address construction, vport RoCE helpers, flow steering APIs, and eswitch source-port match helpers. `rdma.h` compiles the API to no-ops when eswitch support is absent.

## Risks and Test Signals

Risk centers on partial enable cleanup and idempotency. Test RoCE enable/disable during probe, unload, eswitch mode changes, and firmware capability absence. Validate GID entry programming, RDMA RX namespace creation, source-port filtering, and that traffic from non-manager ports is not unintentionally allowed. Fault injection should cover namespace, table, group, rule, and GID programming failures.
