# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/redirect_ingress.c

Purpose: Parses FDB redirect-to-ingress actions for OVS internal ports.

Important API: `mlx5e_tc_act_redirect_ingress` validates OVS master destination, rejects redirect from an internal-port filter device, requires prior `ptype host`, requires no existing destinations, then programs internal-port ingress forwarding actions.

Control flow and state: Parsing sets FWD_DEST, calls `mlx5e_set_fwd_to_int_port_actions()` with `MLX5E_TC_INT_PORT_INGRESS`, resets `if_count`, and increments eswitch output count.

Dependencies and integration: Depends on OVS master netdev detection, internal-port helper code, extack, and parse-state `ptype_host`.

Risks and tests: It is valid only for a narrow ordered action sequence. Tests should cover missing ptype, non-OVS destination, source OVS filter dev, multiple destinations, internal-port creation failures, and metadata restore behavior.
