# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.c

## Purpose
`cmd.c` is the firmware command marshalling layer for HWS. It translates HWS-internal attributes into mlx5 command mailboxes for flow tables, flow groups, FTEs, RTCs, STCs, STEs, definers, packet reformat contexts, send queues, generated WQEs, capability queries, and GVMI lookup.

## Important APIs, Types, And Functions
The file exports create/modify/query/destroy wrappers for flow tables, RTCs, STCs, STE pools, definers, header modify arguments and patterns, packet reformat contexts, generated WQEs, forward tables, and FTEs. `hws_cmd_stc_modify_set_stc_param()` is the central STC action switch and covers counters, TIR/FT jumps, modify-header lists, header insert/remove, modify actions, vport/uplink jumps, ASO, jump-to-STE-table, remove words, IPsec crypto, and trailer actions. `mlx5hws_cmd_query_caps()` performs several capability queries and fills `struct mlx5hws_cmd_query_caps`.

## Control Flow And State
Most functions build zeroed command input buffers with `MLX5_SET`, execute `mlx5_cmd_exec*()`, copy IDs or queried fields from output buffers, and unwind allocated memory. `mlx5hws_cmd_forward_tbl_create()` composes multiple commands: create flow table, create flow group, set FTE, then stores IDs for later destruction in reverse order. `mlx5hws_cmd_set_fte()` dynamically sizes its command buffer based on destination format and emits optional packet reformat, crypto, and extended destination data.

Capability querying proceeds through general device caps, general device 2 caps, NIC flow table caps, WQE-based flow table caps when supported, and e-switch caps when the device is an e-switch manager. The resulting caps drive context support checks, definer selection, queue setup, and BWC behavior.

## Dependencies And Integration Points
This layer depends on mlx5 PRM field macros, core command execution, flow destination enums, vport GVMI helpers, and HWS headers that define command attribute structures. It is used by context initialization, table/matcher/action code, action STE pool creation, definer cache allocation, debug queries, and BWC isolated-table setup.

## Risks And Test Signals
Risks are wrong PRM field names or units, missing destroy on partial create, destination-format mismatches when extended destinations are enabled, capability fields queried under the wrong op_mod, and silent destroy failures because several destroy helpers ignore return values. Test signals include firmware command failure injection at every create step, capability matrices with and without WQE-based update/e-switch support, FTEs with vport/TIR/table/sampler destinations, STC modify coverage for each action type, and generated-WQE status error handling.
