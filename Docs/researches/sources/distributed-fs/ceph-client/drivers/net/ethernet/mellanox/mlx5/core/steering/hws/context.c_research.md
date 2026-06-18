# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.c

## Purpose
`context.c` manages HWS context lifetime. It queries capabilities, decides whether HWS/BWC are supported, allocates protection domains and shared pools, opens send queues, starts action STE pools, registers debugfs dumping, initializes vport state, and tears everything down in reverse order.

## Important APIs, Types, And Functions
Public functions are `mlx5hws_context_open()`, `mlx5hws_context_close()`, `mlx5hws_context_set_peer()`, `mlx5hws_context_cap_dynamic_reparse()`, and `mlx5hws_context_get_reparse_mode()`. Internal helpers initialize/uninitialize pools, private PDs, and HWS resources. `hws_context_check_hws_supp()` validates required capabilities: WQE-based insertion, e-switch manager mode, reparse support, 8DW STE format, hash/offset RTC update modes, and select definer support.

## Control Flow And State
Open allocates and initializes the context, creates locks/xarrays, queries caps, initializes vports, initializes HWS if supported, and registers debugfs. HWS initialization allocates a private PD, pattern and definer caches, an FDB STC pool, sets BWC support, opens send queues, starts the per-queue action STE pool, and initializes the table list. If capability checks fail, the context can still be returned without HWS support rather than treating unsupported hardware as an allocation failure.

Close removes debugfs, uninitializes HWS resources only if HWS support was set, uninitializes vports, frees caps, destroys xarrays/locks, and frees the context. Peer contexts are stored by VHCA ID under `ctrl_lock`.

## Dependencies And Integration Points
This file integrates command capability queries, vport setup, core PD allocation, pattern and definer caches, STC and action STE pools, send queues, debugfs, and BWC support. All HWS table/matcher/action paths depend on `struct mlx5hws_context` state initialized here.

## Risks And Test Signals
Risks include partial-init unwind ordering, returning a context without HWS support to callers that assume BWC support, queue-count assumptions in BWC, peer xarray lifetime, and reparse-mode fallback behavior. Test signals include unsupported capability combinations, allocation failures at each init step, open/close stress, peer insertion errors, and verifying delayed action STE cleanup is canceled before pool memory is freed.
