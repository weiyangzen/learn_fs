# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred_nic.c

Purpose: Handles NIC namespace redirect action by marking the flow as hairpin to another mlx5 netdev on the same hardware.

Important API: `mlx5e_tc_act_mirred_nic` validates only `FLOW_ACTION_REDIRECT`, requires matching netdev ops and same hardware device, stores target ifindex in `mirred_ifindex[0]`, sets flow flag `HAIRPIN`, sets FWD_DEST, and is terminating.

Control flow and state: No persistent state; it mutates parse attributes and flow flags.

Dependencies and integration: Uses `mlx5e_same_hw_devs()`, netdev operations, extack, and the NIC action table.

Risks and tests: Target device validity is crucial. Tests should cover redirect vs mirred action id, same/different mlx5 devices, non-mlx5 devices, NULL or stale device handling by caller, and hairpin flag propagation.
