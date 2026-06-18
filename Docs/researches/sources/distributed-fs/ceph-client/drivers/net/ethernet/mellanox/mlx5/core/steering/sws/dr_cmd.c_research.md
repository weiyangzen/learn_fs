# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_cmd.c

Purpose: wraps mlx5 firmware command mailbox construction for SWS steering capabilities, flow tables/groups/FTEs, vport context, reformat/modify-header objects, definers, samplers, GIDs, and sync-steering.

Important APIs/functions: query helpers (`mlx5dr_cmd_query_device`, `mlx5dr_cmd_query_esw_caps`, `mlx5dr_cmd_query_esw_vport_context`, `mlx5dr_cmd_query_gvmi`, `mlx5dr_cmd_query_flow_table`, `mlx5dr_cmd_query_flow_sampler`, `mlx5dr_cmd_query_gid`), object helpers (`mlx5dr_cmd_create_flow_table`, `destroy_flow_table`, `create_empty_flow_group`, `destroy_flow_group`, `alloc/dealloc_modify_header`, `create/destroy_reformat_ctx`, `create/destroy_definer`, `create/destroy_modify_header_arg`), FTE helpers (`mlx5dr_cmd_set_fte`, `set_fte_modify_and_vport`, `del_flow_table_entry`), and `mlx5dr_cmd_sync_steering`.

Control flow: each function creates stack or kvzalloc command buffers, fills PRM fields with `MLX5_SET/GET`, executes via `mlx5_cmd_exec*`, copies returned IDs/addresses into DR structs, and frees temporary buffers. `mlx5dr_cmd_set_fte()` builds variable-size destination arrays, handles extended destination format when multiple forwarding destinations include encapsulation, encodes counters separately, and fills match values/action metadata.

State/persistence: this file owns no long-lived state; it creates, modifies, queries, or destroys firmware/device objects on behalf of higher layers. Returned IDs become persistent firmware resources until destroy helpers are called.

Dependencies/integration: depends on mlx5 command interface, capability macros, eswitch/vport helpers, flow-table PRM layouts, and DR command data structures. It is the low-level bridge used by action, domain, definer, firmware helper, and ICM argument code.

Risks: mailbox layouts are sensitive to table type, destination type, opmod, and variable-length sizing. Extended-destination support must match firmware caps or FTE creation fails. Some destroy helpers ignore command errors, which can hide firmware cleanup failures. `sync_steering` intentionally no-ops during internal error state.

Test signals: command-buffer field validation with firmware simulators, capability-query matrix across NIC/FDB devices, FTE creation with counters/vports/uplink/flow tables/samplers/extended encap, reformat and definer lifecycle, and destroy paths after partial create failures.
