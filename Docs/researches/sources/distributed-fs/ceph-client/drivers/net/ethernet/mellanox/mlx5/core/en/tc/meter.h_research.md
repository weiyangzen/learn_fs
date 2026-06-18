# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/meter.h

Purpose: Declares flow meter parameter, handle, and meter attribute types plus lifecycle/update/stat APIs.

Important types: `enum mlx5e_flow_meter_mode` selects BPS or PPS. `struct mlx5e_flow_meter_params` carries police index, rate, burst, and MTU. `struct mlx5e_flow_meter_handle` owns flow-meter subsystem pointer, ASO object slot, refcount, params, hash node, action counter, and drop counter. `struct mlx5e_meter_attr` embeds params and post-meter linkage.

Control flow and state: Police parsing fills params, then offload code gets/replaces/updates handles and releases them via `put()`. Stats aggregate action and drop counters.

Dependencies and integration: Used by police action parser, post-meter steering, and TC private flow attrs. `mlx5e_flow_meter_get_base_id()` has a stub when class-act support is disabled.

Risks and tests: Callers must not dereference ASO fields for MTU-only meters. Tests should compile with `CONFIG_MLX5_CLS_ACT` on/off and validate get/put/refcount API usage.
