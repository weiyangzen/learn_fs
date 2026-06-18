# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.h

Purpose: declares the mlx5e TIR builder API, RSS parameter structures, and TIR object wrapper used by RX setup paths.

Important APIs and types: `struct mlx5e_rss_params_hash` carries hash function, Toeplitz key, and symmetric hash flag. `struct mlx5e_rss_params_traffic_type` carries L3/L4 protocol selectors and selected hash fields. `struct mlx5e_tir` stores the core device, TIR number, and optional list node. Builder and lifecycle functions match the implementation in `tir.c`, and `mlx5e_tir_get_tirn` exposes the hardware TIR number.

Control flow: RX resource setup builds command input through a `mlx5e_tir_builder`, creates a `mlx5e_tir`, uses the TIR number in flow steering destinations or trap rules, and later modifies or destroys it. The header keeps builder internals opaque so callers cannot accidentally depend on firmware command layouts.

State and persistence: `struct mlx5e_tir` is the persistent runtime object. Builder state is opaque and temporary. The list node is meaningful only when init was called with registration enabled.

Dependencies and integration points: depends on Linux kernel types and forward-declared mlx5 core and packet merge types. Used by channel setup, RSS configuration, TLS RX, self-loopback controls, and trap queue creation.

Risks and test signals: callers must not use a destroyed TIR number or modify with a create-style builder. Test signals include compile coverage for all builder declarations, RSS reconfiguration, trap use of `mlx5e_tir_get_tirn`, and cleanup paths that destroy registered and unregistered TIRs.
