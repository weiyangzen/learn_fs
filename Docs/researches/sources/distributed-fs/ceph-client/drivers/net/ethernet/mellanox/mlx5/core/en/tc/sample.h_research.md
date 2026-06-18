# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.h

Purpose: Declares TC psample offload state, sample attributes embedded in flow attrs, and sampling APIs with disabled-config stubs.

Important types and APIs: `struct mlx5e_sample_attr` stores group number, rate, trunc size, restore object id, sampler id, and per-flow sample state pointer. APIs cover skb sampling, offload/unoffload, init, and cleanup.

Control flow and state: The action parser fills `mlx5e_sample_attr`; the offload implementation populates restore/sampler ids and per-flow state; teardown uses those fields to free hardware resources.

Dependencies and integration: Includes eswitch types and depends on `CONFIG_MLX5_TC_SAMPLE` for real implementations.

Risks and tests: Callers must handle `-EOPNOTSUPP` stubs when sample support is disabled. Tests should compile enabled/disabled configs and validate attr fields are initialized before offload.
