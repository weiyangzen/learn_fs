# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.h

Purpose: Declares the eswitch indirection-table API and provides stubs when `CONFIG_MLX5_CLS_ACT` is disabled.

Important APIs/types/functions: Declares init/destroy, get/put, `needed()`, and `decap_vport()` helpers. Stubs return NULL, `ERR_PTR(-EOPNOTSUPP)`, false, or 0 as appropriate when TC action offload support is not compiled.

Control flow and integration: TC offload code can call the API unconditionally and rely on the compile-time branch to either use real indirection tables or decline support. The real implementation in `indir_table.c` is available only with CLS_ACT.

State and persistence: The header owns no state, but its opaque `struct mlx5_esw_indir_table` pointer is stored under eswitch FDB offloads state by callers.

Risks and test signals: Risks include callers not checking `ERR_PTR(-EOPNOTSUPP)` in stub builds or mismatching get/put. Test signals include build coverage with and without `CONFIG_MLX5_CLS_ACT`, TC flower flows that require indirection, and graceful rejection when unsupported.
