# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/fs_chains.c

Purpose: Implements dynamic flow-steering chains for TC/offload pipelines, mapping `(chain, priority, level)` to flow tables connected by explicit miss rules.

Important APIs and flow: `mlx5_chains_create()` initializes rhashtables, ranges, namespace, default/end flow tables, flags, and optional mapping context. `mlx5_chains_get_table()` validates ranges, recursively creates earlier levels, then creates or refs a `prio` object. Chain creation optionally allocates a chain mapping, restore rule, and modify-header action so miss-to-end can preserve chain identity. Prio creation builds a flow table, miss group, miss rule to the next level-0 table/end/default table, inserts it into sorted chain order, and rewires previous priority miss rules through `mlx5_chains_update_prio_prevs()`. Put/destroy reverses refs and rewiring.

State and dependencies: `struct mlx5_fs_chains` owns chain/prio rhashtables and mutex. `struct fs_chain` owns mapping/restore state and sorted prio list; `struct prio` owns FT, miss group, miss rule, next FT, and refcount. Dependencies include flow table pools/core, eswitch restore rules, TC register mappings, mapping contexts, and namespace-specific FDB/NIC RX behavior.

Risks and test signals: Rewiring miss rules in reverse order is delicate, especially on create failure and destroy. Range behavior changes with `MLX5_CHAINS_AND_PRIOS_SUPPORTED` and `IGNORE_FLOW_LEVEL`. Tests should cover sorted insertion, multi-level recursion unwinding, NF chain special case, global table creation, mapping default-flow-tag collision, FDB versus kernel namespace, tunnel flags, and unbalanced put warnings.
