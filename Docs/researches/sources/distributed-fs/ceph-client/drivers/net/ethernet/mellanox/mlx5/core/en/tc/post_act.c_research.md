# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.c

Purpose: Implements post-action steering: a global table matching a generated FTE id in a register and applying deferred TC rule actions.

Important APIs: `mlx5e_tc_post_act_init()`/`destroy()`, `add()`/`del()`, `offload()`/`unoffload()`, `get_ft()`, and `set_handle()`.

Control flow: Init requires ignore-flow-level support, creates a global chains table, and initializes an xarray allocator. `add()` normalizes the post attr to chain/prio zero, strips decap, sets no-in-port, resets FDB split count, and allocates a handle id. `offload()` creates a spec matching `FTEID_TO_REG` to handle id and offloads the rule. `set_handle()` emits a modify-header action that writes the handle id into the register.

State and persistence: `mlx5e_post_act` owns namespace, chains, global FT, priv, and xarray ids. Each handle owns namespace, attr, rule, and id. Hardware table/rules persist until unoffload/destroy.

Dependencies and integration: Uses fs chains, register mapping helpers, TC rule offload/unoffload, mod-header actions, and firmware flow-table capabilities. It is used by sample, meter, and multi-table action chaining.

Risks and tests: The xarray id limit is derived from register bit width; exhaustion returns errors. Destroy assumes handles/rules are already cleaned up. Tests should cover unsupported firmware, id allocation/free/reuse, FDB split reset, decap stripping, set_handle mod-header failure, and offload/unoffload ordering.
