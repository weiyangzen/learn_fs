# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/police.c

Purpose: Handles TC police action parsing, standalone action lifecycle, meter creation/update/destruction, stats, and branch control for conform/exceed decisions.

Important APIs: `mlx5e_tc_act_police` supplies validation, parse, multi-table marker, offload/destroy/stats callbacks, and `get_branch_ctrl`. It uses `mlx5e_tc_meter_get()`, `replace()`, `update()`, `put()`, and stats helpers.

Control flow: Validation permits only pipe/accept/jump/drop controls and rejects peakrate/avrate/overhead. `fill_meter_params_from_act()` converts byte rate to bit rate, packet rate, or MTU mode. Parsing either sets execute-ASO flow meter or MTU range-match forwarding. Standalone offload gets or creates a meter; destroy performs two puts, one for the lookup and one for cleanup; stats query meter counters.

State and dependencies: Mutates `attr->meter_attr.params`, action bits, ASO type, MTU flag, and branch-control outputs. Persistent state is owned by `meter.c`. Depends on flow meter capability, flow steering range-match capability for MTU, extack, and `flow_stats_update()`.

Risks and tests: Refcount pairing in destroy is easy to regress. MTU mode skips ASO allocation but still uses meter handles/counters differently. Tests should cover BPS, PPS, MTU, unsupported controls, unsupported peakrate/avrate/overhead, missing meter subsystem, meter update path, destroy refcount, and stats reporting.
