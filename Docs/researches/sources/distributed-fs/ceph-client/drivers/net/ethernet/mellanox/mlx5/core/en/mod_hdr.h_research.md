# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.h

Purpose: defines the public modify-header action buffer and cached handle API used by mlx5e TC offloads.

Important APIs/types: `struct mlx5e_tc_mod_hdr_acts`, opaque `struct mlx5e_mod_hdr_handle`, `DECLARE_MOD_HDR_ACTS_ACTIONS`, `DECLARE_MOD_HDR_ACTS`, allocation/deallocation helpers, attach/detach/get helpers, table init/destroy, and `mlx5e_mod_hdr_max_actions`.

Control flow: callers build action arrays, append entries with `mlx5e_mod_hdr_alloc`, attach the completed action list to get a cached firmware handle, use `mlx5e_mod_hdr_get` in flow rule construction, then detach and deallocate actions.

State and persistence: tracks whether an actions array is static or heap-backed. Cached firmware object state lives in the implementation.

Dependencies and integration: includes mlx5 flow namespace definitions and uses FDB vs kernel namespace capability fields to determine maximum actions.

Risks: callers must increment `num_actions` consistently after writing allocated action slots and must not free static action storage through normal `kfree`.

Test signals: compile-time static action declarations, namespace capability variation, and TC pedit/action offload flows.
