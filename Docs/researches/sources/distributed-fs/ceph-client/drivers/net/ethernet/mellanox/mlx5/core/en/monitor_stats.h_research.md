# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.h

Purpose: declares the mlx5e monitor-counter lifecycle and capability API.

Important APIs/functions: `mlx5e_monitor_counter_supported`, `mlx5e_monitor_counter_init`, and `mlx5e_monitor_counter_cleanup`.

Control flow: callers check support before initializing monitor counters, then clean them up during device teardown.

State and persistence: no header-owned state; implementation stores notifier/work state in `mlx5e_priv` and firmware monitor configuration in the device.

Dependencies and integration: relies on `struct mlx5e_priv` from surrounding mlx5e headers.

Risks: the header documents no locking contract, so callers must follow the implementation expectation that init/cleanup are part of driver lifecycle.

Test signals: build coverage and feature-gated init/cleanup sequencing.
