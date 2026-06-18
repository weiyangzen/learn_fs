# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.h

Purpose: defines mlx5e queue parameter data structures and declares the parameter calculation/building API.

Important APIs/types: `struct mlx5e_xsk_param`, `mlx5e_rq_opt_param`, `mlx5e_cq_param`, `mlx5e_rq_param`, `mlx5e_sq_param`, `mlx5e_channel_param`, `mlx5e_create_sq_param`, MPWRQ dynamic helpers, RX layout helpers, CQ/SQ/RQ builders, validation helpers, and `mlx5e_params_print_info`.

Control flow: channel open code fills these parameter structs through build functions, then passes the embedded firmware contexts and workqueue parameters to queue creation functions. Optional `rq_opt` carries XSK or per-queue page-size settings.

State and persistence: structures are per-channel/per-queue configuration snapshots. Inline helpers only read or format fields; no global state is held.

Dependencies and integration: includes `en.h` and depends on mlx5 firmware context sizes, mlx5e params, netdev queue config, and XSK metadata.

Risks: callers must zero structs before use where required and must pass matching `params`/`rq_opt` to calculations and builders. `mlx5e_params_print_info` calls MPWRQ helpers even for cyclic RQ to print stride size, so capability assumptions still matter.

Test signals: compile coverage across feature flags, channel parameter construction, XSK channel construction, and validation failures for unsupported MPWRQ settings.
