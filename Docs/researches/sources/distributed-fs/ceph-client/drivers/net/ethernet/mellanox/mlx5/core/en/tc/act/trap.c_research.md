# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/trap.c

Purpose: Parses TC trap action by forwarding matching packets to the eswitch slow FDB table.

Important API: `mlx5e_tc_act_trap` sets FWD_DEST and assigns `attr->dest_ft = mlx5_eswitch_get_slow_fdb()`.

Control flow and state: No persistent state; it mutates the current flow attr.

Dependencies and integration: Depends on eswitch slow FDB accessor and common action parser.

Risks and tests: Tests should verify trap routes to slow path and coexists with parser termination rules in the higher-level action loop.
