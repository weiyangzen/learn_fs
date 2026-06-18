# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ct.c

Purpose: Bridges TC connection-tracking actions into mlx5 TC CT offload.

Important API: `mlx5e_tc_act_ct` validates, parses, post-parses, and marks CT as multi-table/missable except for clear actions. Parsing calls `mlx5_tc_ct_parse_action()`, post-parse calls `mlx5_tc_ct_flow_offload()`.

Control flow: Commit CT actions cannot be the last flow action. Parsing may reset eswitch split/output counts after CT processing, because CT creates a multi-table boundary. The post-parse hook performs actual CT flow offload only if `MLX5_ATTR_FLAG_CT` was set.

State and dependencies: Mutates `attr` flags and eswitch attr split state; uses `parse_state->ct_priv` and `en/tc_ct.h`. No independent persistent state.

Risks and tests: CT action ordering, clear-vs-non-clear behavior, and FDB split reset are subtle. Tests should cover CT commit last rejection, CT clear, CT with redirect destinations, post-parse errors, and missable/multi-table decisions.
