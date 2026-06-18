# `sources/distributed-fs/ceph-client/include/linux/mlx5/lag.h`

## Purpose

`lag.h` exposes the public mlx5 LAG demultiplexing API. It lets consumers initialize and clean up a LAG demux flow table, add and delete per-vport demux rules, and query the device sequence used to identify the local device position in a LAG setup.

## Important APIs, Types, and Constants

- The header forward-declares `struct mlx5_core_dev`, `struct mlx5_flow_table`, and `struct mlx5_flow_table_attr`.
- `mlx5_lag_demux_init()` initializes LAG demux resources for a device using flow table attributes.
- `mlx5_lag_demux_cleanup()` releases those resources.
- `mlx5_lag_demux_rule_add()` installs a rule mapping a vport number to a vport index.
- `mlx5_lag_demux_rule_del()` removes a demux rule by vport index.
- `mlx5_lag_get_dev_seq()` returns a device sequence/index value for the current mlx5 device.

## Control Flow and Lifetimes

Callers initialize demux resources before loading representor or RDMA paths that need vport demultiplexing. After initialization, they add rules for vports as representors are loaded or peer paths become active, and delete those rules before the vport/representor disappears. Cleanup destroys the demux flow table and supporting firmware state after all rules have been removed. Usage references show RDMA main initialization calling `mlx5_lag_demux_init()`/cleanup and IB representor load/unload adding/deleting demux rules.

## State and Persistence Behavior

The header exposes no structs, but implementation state includes a LAG demux flow table and per-vport rule handles stored in mlx5 LAG private state. Rules persist in hardware flow steering until deleted or cleanup occurs. `vport_index` is the stable key used for deletion.

## Dependencies and Integration Points

The API depends on `mlx5_core_dev` and flow-steering table attributes from `fs.h`. Implementation references in this tree live under `drivers/net/ethernet/mellanox/mlx5/core/lag/lag.c`, with additional internal declarations in the LAG core header. It integrates with RDMA representors (`drivers/infiniband/hw/mlx5/ib_rep.c`) and RDMA device startup (`drivers/infiniband/hw/mlx5/main.c`), and it uses flow tables created through the mlx5 flow-steering API.

## Risks and Edge Cases

- Add/delete pairing is index-based. Reusing or miscomputing `vport_index` can remove the wrong rule or leak a rule.
- Demux initialization may choose firmware or flow-table paths depending on capabilities in implementation; callers must not assume a specific backend.
- Cleanup while rules are active risks dangling handles or traffic steering loss.
- LAG state is topology-sensitive; tests must cover active/inactive LAG, representor reload, and multiport cases.

## Test Signals

Validate RDMA startup/shutdown with LAG enabled, representor load/unload rule add/delete, error unwind after partial rule creation, active bond changes, multiport device sequence values from `mlx5_lag_get_dev_seq()`, and builds against the 2026 NVIDIA LAG API header.
