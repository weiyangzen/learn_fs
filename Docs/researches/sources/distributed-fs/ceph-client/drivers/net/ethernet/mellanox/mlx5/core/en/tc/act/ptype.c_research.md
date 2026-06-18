# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/ptype.c

Purpose: Parses skbedit packet type action needed by redirect-to-ingress internal-port offload.

Important API: `mlx5e_tc_act_ptype` accepts only `PACKET_HOST` and sets `parse_state->ptype_host`.

Control flow and state: No persistent state; parse-state flag is later required by `redirect_ingress.c`.

Dependencies and integration: Uses action parser interface and `tc_priv`. Available in the FDB action table.

Risks and tests: Tests should verify non-host ptype is rejected and redirect_ingress fails unless ptype host was parsed earlier.
