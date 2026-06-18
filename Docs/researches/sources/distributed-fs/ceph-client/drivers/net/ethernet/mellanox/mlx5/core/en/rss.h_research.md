# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.h

Purpose: Public interface for mlx5e RSS contexts, including init modes, parameters, TIR/RQT accessors, RSS hash/indirection configuration, and refcounting.

Important types: `enum mlx5e_rss_init_type` selects lazy/no-TIR or precreated TIR initialization. `struct mlx5e_rss_init_params` passes packet merge parameters and channel sizing. `struct mlx5e_rss_params` carries inner FT support, drop RQN, and self-loopback block. The opaque `struct mlx5e_rss` hides implementation details.

Control flow and state: Callers create an RSS object with `mlx5e_rss_init()`, optionally enable it with live RQNs/vHCA IDs, query TIRNs for flow steering, and mutate RSS via ethtool-facing methods. Cleanup returns `-EBUSY` if references remain.

Dependencies and integration: Includes `rqt.h`, `tir.h`, and `fs.h`; consumed by RX resource manager, reporters, and flow-steering code needing RSS TIRNs.

Risks and test signals: Because the struct is opaque, correctness rests on callers honoring lifecycle, reference count, and enabled-state expectations. Tests should validate compile-time call sites under `CONFIG_*` variants, cleanup error handling, and that callers do not request inner TIRs without support.
