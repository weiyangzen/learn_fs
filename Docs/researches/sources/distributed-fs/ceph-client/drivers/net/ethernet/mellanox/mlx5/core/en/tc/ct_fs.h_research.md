# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs.h

Purpose: Defines an abstract connection-tracking flow-steering backend interface with DMFS, SMFS, and HMFS implementations.

Important types: `struct mlx5_ct_fs` holds netdev, device, and backend private storage. `struct mlx5_ct_fs_rule` is an opaque base. `struct mlx5_ct_fs_ops` supplies init/destroy, CT rule add/delete/update, and `priv_size`.

Control flow and state: CT owner selects a backend by calling `mlx5_ct_fs_dmfs_ops_get()`, `mlx5_ct_fs_smfs_ops_get()`, or `mlx5_ct_fs_hmfs_ops_get()`, allocates `struct mlx5_ct_fs` with `priv_size`, initializes against CT/CT-NAT/post-CT tables, then manages backend rules through the ops table.

Dependencies and integration: Conditional declarations depend on `CONFIG_MLX5_SW_STEERING` and `CONFIG_MLX5_HW_STEERING`. Backends integrate with legacy TC rule insertion, software steering DR, or hardware steering HWS.

Risks and tests: `mlx5_ct_fs_priv()` returns private flexible-array storage; allocation size must include `priv_size`. Tests should cover backend selection under config permutations and rule lifecycle through the abstract ops.
