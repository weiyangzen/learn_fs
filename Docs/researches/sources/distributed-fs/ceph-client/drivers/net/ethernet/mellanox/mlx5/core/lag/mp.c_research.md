# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.c

Purpose: Implements mlx5 LAG multipath offload driven by IPv4 FIB notifications. It activates `MLX5_LAG_MODE_MULTIPATH` when suitable two-port routes appear, tracks the selected `fib_info`, and adjusts port affinity as nexthops are added or removed.

Important APIs and flow: `mlx5_lag_mp_init()` creates a single-thread workqueue and registers a FIB notifier; `mlx5_lag_fib_event()` filters AF_INET route/nexthop events and queues `mlx5_lag_fib_update()`; route handling chooses one or two LAG netdev nexthops, activates LAG on first multipath route, and calls `mlx5_lag_set_port_affinity()` for normal, P1-only, or P2-only forwarding. `mlx5_lag_is_multipath()`, `mlx5_lag_mp_reset()`, and `mlx5_lag_mp_cleanup()` expose mode state and lifecycle.

State and dependencies: `ldev->lag_mp.fib` stores a borrowed/staleness-prone route identity, priority, destination, and prefix length; FIB work takes explicit `fib_info_hold()` references until processed under RTNL. It depends on eswitch multipath prerequisites, LAG mode helpers, netdev-to-LAG index mapping, notifier chains for port-affinity events, and `mlx5_modify_lag()`.

Risks and test signals: Race handling relies on workqueue flush during notifier unregister and RTNL during updates. Watch route delete/missed-event paths, stale `mfi` reset on reinit, duplicate nexthops on one device, priority/prefix comparisons, and only-two-port support. Useful tests are IPv4 ECMP add/replace/delete, nexthop add/delete, single-nexthop fallback affinity, cleanup while events are queued, and unsupported eswitch/port-count configurations.
