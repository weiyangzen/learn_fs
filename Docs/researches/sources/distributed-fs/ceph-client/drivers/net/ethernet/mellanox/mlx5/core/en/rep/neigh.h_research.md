# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/neigh.h

Purpose: declares representor neighbour tracking APIs with stubs when TC action offload support is disabled.

Important APIs/functions: neighbour init/cleanup, lookup/create/release of `mlx5e_neigh_hash_entry`, and queueing neighbour stats work.

Control flow: TC tunnel encap code attaches flows to neighbour entries, netevent code updates them, and cleanup removes notifier/table state. Disabled builds return success or no-op for lifecycle functions.

State and persistence: no header-owned state; implementation stores hash/list/refcount state under `mlx5e_rep_priv`.

Dependencies and integration: includes `en.h` and `en_rep.h`; guarded by `CONFIG_MLX5_CLS_ACT`.

Risks: callers in enabled builds must release looked-up/created entries and hold required locks described in the implementation.

Test signals: build with and without `CONFIG_MLX5_CLS_ACT`, encap-neighbour reference balancing, and stats work scheduling.
