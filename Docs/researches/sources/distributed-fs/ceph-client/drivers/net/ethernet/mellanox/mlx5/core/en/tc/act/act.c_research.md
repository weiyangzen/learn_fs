# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.c

Purpose: Central dispatcher and helper implementation for mlx5e TC action parsing.

Important APIs: `mlx5e_tc_act_get()` maps `flow_action_id` to a `struct mlx5e_tc_act` table for FDB or NIC namespace. `mlx5e_tc_act_init_parse_state()` zeroes and seeds parser state. `mlx5e_tc_act_post_parse()` runs per-action `post_parse` hooks over a range. `mlx5e_tc_act_set_next_post_act()` writes a post-action handle into the modify-header action list and sets FWD_DEST/MOD_HDR.

Control flow: The parser obtains action vtables from `tc_acts_fdb` or `tc_acts_nic`; unsupported action ids return NULL to the caller. Post-parse walks the original `flow_action`, filters by index range, and invokes only actions with a hook.

State and dependencies: Static action tables are the key state. Parse state carries transient flags such as encap, decap, mpls, ptype_host, tunnel info, ifindexes, and CT private pointer. Depends on post-action register programming and TC private flow structs.

Risks and tests: Adding a new action requires namespace table updates and extern declarations. Array indexing relies on `act_id < NUM_FLOW_ACTIONS` from callers. Tests should cover FDB/NIC action table differences, post-parse ordering, unsupported actions, and chained post-action handle programming.
