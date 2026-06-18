# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.c

Purpose: Implements multiport e-switch LAG mode. MPESW lets multiple PFs share eswitch/offloads behavior by allocating per-uplink metadata, creating LAG in `MLX5_LAG_MODE_MPESW`, reloading IB representatives, and updating aggregate vport speed.

Important APIs and flow: `mlx5_lag_mpesw_enable()` and `mlx5_lag_mpesw_disable()` queue synchronous work on the LAG workqueue. The worker serializes against devcom and `ldev->lock`, rejects mode changes in progress, then calls `mlx5_lag_enable_mpesw()` or `mlx5_lag_disable_mpesw()`. Enable validates offloads mode, port-selection FT support, non-master-up capability, normal LAG prerequisites, and shared FDB support; it sets metadata with `mlx5_esw_match_metadata_alloc()` and ingress ACL updates, removes devices, activates LAG, rescans drivers, reloads IB reps, and updates aggregate speeds. `mlx5_lag_mpesw_do_mirred()` blocks forwarding to a bond in MPESW mode.

State and dependencies: `ldev->lag_mpesw.pf_metadata[]` persists firmware metadata IDs until cleanup. MPESW integrates with eswitch ACLs, devcom locking, LAG activation/deactivation, notifier chains (`MLX5_DEV_EVENT_MULTIPORT_ESW`), IB auxiliary-device rescans, and port-change events.

Risks and test signals: Enable has multi-step rollback across metadata, devices, drivers, eswitch reps, and LAG state; failures must leave devices re-added and metadata freed. Tests should cover unsupported caps, queue-work failure, concurrent mode changes returning `-EAGAIN`, port up/down speed updates, TC mirred rejection, and disable from active MPESW.
