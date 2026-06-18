# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dcbnl.c

Purpose: implements mlx5e DCB netlink operations for IEEE and CEE DCBX, ETS, PFC, DSCP app mappings, max-rate, and port buffer configuration.

Important APIs, types, and functions: `mlx5e_dcbnl_build_netdev()` attaches `dcbnl_ops`. IEEE ops include get/set ETS, PFC, APP, maxrate, and buffer. CEE ops include setall, PG/PFC config, capability queries, and state. Initialization functions are `mlx5e_dcbnl_initialize()`, `mlx5e_dcbnl_init_app()`, and `mlx5e_dcbnl_delete_app()`. Internal helpers build TC groups and bandwidth arrays, validate ETS, switch DCBX host/auto mode, change trust state, set DSCP-to-priority, initialize ETS defaults, and query buffer cell size.

Control flow: initialization reads trust state and DSCP mappings, normalizes stale DSCP app state, computes inline mode constraints, reads DCBX mode, sets capability flags, computes max-rate limits, and initializes ETS to vendor TSA defaults. Set-ETS validates priority mappings and ETS bandwidth sum, translates IEEE TSA into mlx5 TC groups and bandwidth, and writes port registers. Set-PFC writes PFC enable bits, toggles link, and may recompute manual port buffers. DSCP app set switches trust to DSCP, writes firmware mapping, updates dcb app table and counters; delete restores mapping and trust to PCP when no DSCP apps remain. Trust-state changes may safely switch channel params if TX min inline mode changes.

State and persistence: driver state lives in `priv->dcbx`, `priv->dcbx_dp`, and CEE config arrays. Firmware persists ETS/PFC/rate/trust/DSCP mappings. DCB app entries are registered with the kernel DCB subsystem and mirrored by `dscp_app_cnt`.

Dependencies and integration points: depends on mlx5 port register helpers, port buffer management, netdevice DCBNL ops, devlink/firmware capabilities, channel safe-switch params, and pport stats.

Risks: DCB changes can require channel reset due to inline mode changes. ETS zero-bandwidth handling maps Linux semantics onto mlx5 group semantics and is easy to regress. DSCP app error paths try to restore PCP trust but can leave kernel app entries and firmware mappings temporarily inconsistent. Manual buffer updates depend on buffer ownership and MTU.

Test signals: get/set ETS with strict/vendor/ETS and zero bandwidth, PFC enable and cable length, DSCP app add/delete and trust transitions, host/auto DCBX mode, maxrate unit conversion and limits, buffer get/set with SW ownership, CEE setall, and devices lacking individual capabilities.
