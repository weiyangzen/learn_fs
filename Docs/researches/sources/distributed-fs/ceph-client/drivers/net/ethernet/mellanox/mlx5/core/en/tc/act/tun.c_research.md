# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/tun.c

Purpose: Parses tunnel encap/decap TC actions into parse-state flags consumed by later actions.

Important APIs: `mlx5e_tc_act_tun_encap` validates non-null tunnel info and sets `parse_state->tun_info`/`encap`. `mlx5e_tc_act_tun_decap` sets `parse_state->decap`.

Control flow and state: No persistent state. Encap parsing defers actual destination/tunnel duplication to mirred parsing; decap affects goto/sample/MPLS behavior later.

Dependencies and integration: Uses TC tunnel encap data, extack, and downstream tunnel encap/offload code.

Risks and tests: Action order is critical. Tests should cover null tunnel rejection, encap followed by redirect, decap followed by goto rejection, and sample with decap.
