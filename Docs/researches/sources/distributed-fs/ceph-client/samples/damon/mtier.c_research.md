# sources/distributed-fs/ceph-client/samples/damon/mtier.c

Purpose: DAMON physical-address sample for memory tiering. It migrates hot pages from node 1 to node 0 and cold pages from node 0 to node 1 while using DAMOS quota goals to target node 0 utilization/free ratios.

Important APIs/functions: module parameters configure node address ranges, node0 memory used/free basis points, `enabled`, and `detect_node_addresses`. Uses `damon_new_ctx`, `damon_set_attrs`, `damon_select_ops(DAMON_OPS_PADDR)`, `damon_new_target`, `damon_new_region`, `damon_new_scheme`, `damos_new_quota_goal`, `damos_new_filter`, `damon_start`, and `damon_stop`.

Control flow: enabling builds two contexts with `damon_sample_mtier_build_ctx`: one promote context for node 1 using `DAMOS_MIGRATE_HOT`, one demote context for node 0 using `DAMOS_MIGRATE_COLD`. Init starts them if `enabled` was preset. The parameter store toggles start/stop after validating `damon_initialized()`.

State and persistence: two global `damon_ctx *` pointers and module parameters. DAMON contexts and schemes persist until disabled or module removal; no on-disk state.

Dependencies and integration: depends on DAMON physical address operations, NUMA node metadata, DAMOS migration actions, and page young filtering.

Risks: incorrect physical ranges or node IDs can monitor the wrong memory. Migration actions can affect performance and placement. Error paths destroy contexts, but there is no module exit hook, so this sample relies on enable/disable semantics and DAMON lifecycle assumptions.

Test signals: enable on a two-node system with `detect_node_addresses=1` or explicit ranges, inspect DAMON activity and node memory balance, then disable and confirm `damon_stop` destroys both contexts.
