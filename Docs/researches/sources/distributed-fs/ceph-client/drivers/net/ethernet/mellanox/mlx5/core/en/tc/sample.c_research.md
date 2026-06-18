# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/sample.c

Purpose: Implements the full TC psample offload model for eswitch/FDB flows using sampler objects, termination table, restore mappings, optional post-action table, and per-vport default tables.

Important APIs: `mlx5e_tc_sample_init()`/`cleanup()`, `mlx5e_tc_sample_offload()`/`unoffload()`, and `mlx5e_tc_sample_skb()`.

Control flow: Init creates a termination table forwarding sampled packets to the manager vport and initializes sampler/restore hash locks. Offload allocates a sample flow, selects post-action table or per-vport default table, gets or creates a sampler object keyed by rate and default table, maps sample restore data in reg_c0 object pool, gets or creates a restore modify-header/rule, creates a pre-rule that points to the sampler object and writes restore metadata, and stores pointers in `attr->sample_attr`. Unofoffload deletes the pre-rule first, then restore mapping, sampler, optional post rule, attrs, and wrapper. `mlx5e_tc_sample_skb()` sends restored packets to psample with truncation metadata.

State and persistence: `mlx5e_tc_psample` owns eswitch, termination table/rule, sampler hash, restore hash, locks, and post_act. Samplers are refcounted by `(ratio, default_table_id)`. Restore contexts are refcounted by object id and own modify header plus restore rule. Per-flow state links sampler, restore, pre/post attrs/rules.

Dependencies and integration: Uses psample, eswitch vport tables, mapping API, post-action subsystem, mod-header register setters, sampler general object commands, termination table capability, and TC sample action parser state.

Risks: Delete order is firmware-sensitive and documented as fixed. Restore count is checked outside the lock after decrement, which relies on no resurrection after zero. `mlx5e_tc_sample_skb()` pushes MAC header before sampling and should be tested for skb layout assumptions. Tests should cover capability failures, sampler reuse/refcount, restore reuse/refcount, reg_c preserve vs per-vport default path, decap path, encap slow-path source-port clearing, error unwinds at every allocation/offload step, and sample skb truncation.
