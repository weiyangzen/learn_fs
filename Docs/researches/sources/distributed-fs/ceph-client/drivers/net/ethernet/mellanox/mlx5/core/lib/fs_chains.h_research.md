# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.h

Purpose: Declares the flow-steering chains API for TC classifier/action users.

Important APIs and types: `enum mlx5_chains_flags` advertises chain/prio support, ignore-flow-level support, and tunnel table support. `struct mlx5_chains_attr` carries namespace, base priority/level, flags, group count, default table, and optional mapping context. Exports feature queries, range queries, table get/put, TC end table access, global table create/destroy, chain mapping get/put, lifecycle create/destroy, end table setter, and debug info.

State and dependencies: The API is available when `CONFIG_MLX5_CLS_ACT` is enabled; otherwise many calls are stubs returning unsupported or no-op. It depends on mlx5 flow table types and the mapping context type from implementation users.

Risks and test signals: Callers must balance table get/put for all implicit lower levels and handle `ERR_PTR(-EOPNOTSUPP)` in non-CLS_ACT builds. Build tests should cover both config branches and users of all exported flags.
