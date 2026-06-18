# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_dmfs.c

Purpose: Provides the direct/legacy mlx5 TC rule backend for CT flow steering.

Important API: `mlx5_ct_fs_dmfs_ops_get()` returns ops whose init/destroy are no-ops and whose add/delete/update wrap `mlx5_tc_rule_insert()` and `mlx5_tc_rule_delete()`.

Control flow: Rule add allocates `mlx5_ct_fs_dmfs_rule`, inserts a TC rule, stores attr, and returns the embedded base. Update inserts a replacement rule first, deletes the old rule, then swaps handle/attr. Delete removes the stored rule and frees the wrapper.

State and dependencies: Per-rule state is only flow handle and attr pointer. Depends on netdev-private `mlx5e_priv`, `en_tc.h`, and `tc_ct` definitions.

Risks and tests: Update is not fully atomic if insertion succeeds and deletion has side effects, but it avoids deleting before replacement. Tests should cover add allocation failure, insert failure, update insert failure preserving old rule, update success, and delete.
