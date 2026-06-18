<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads_termtbl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads_termtbl.c

## Purpose

This file implements shared e-switch offload termination tables for cases where an FDB rule cannot express all actions directly at its original flow level. It creates a one-entry unmanaged FDB flow table that performs the terminating action list, then rewrites the original destination to forward into that table. The main callers are TC/e-switch offload paths that need RX VLAN push on devices without native support or hairpin-to-uplink termination behavior.

## Important APIs, types, and functions

- `struct mlx5_termtbl_handle` is the cache object stored in `esw->offloads.termtbl_tbl`. It owns the termination flow table, the single rule inside it, copied `flow_act`/vport destination identity, a hash node, and a manual `ref_count`.
- `mlx5_eswitch_termtbl_hash()` and `mlx5_eswitch_termtbl_cmp()` define cache identity from action bits, VLAN push state, destination vport/vhca, and optional packet reformat content.
- `mlx5_eswitch_termtbl_create()` allocates a `MLX5_FLOW_TABLE_TERMINATION | MLX5_FLOW_TABLE_UNMANAGED | MLX5_FLOW_TABLE_TUNNEL_EN_REFORMAT` table in the FDB namespace and installs one forwarding rule.
- `mlx5_eswitch_termtbl_get_create()` serializes cache lookup/creation under `termtbl_mutex`; `mlx5_eswitch_termtbl_put()` decrements the handle and destroys the table/rule when the last user leaves.
- `mlx5_eswitch_termtbl_required()` is the policy gate. It requires termination-table and ignore-flow-level FDB capabilities, excludes skip actions, requires uplink/internal-port source, and returns true for unsupported VLAN-push-on-RX or hairpin-to-uplink patterns.
- `mlx5_eswitch_add_termtbl_rule()` mutates destinations from vport to flow-table destinations and installs the original FTE with `FLOW_ACT_IGNORE_FLOW_LEVEL`.

## Control flow

The caller first checks `mlx5_eswitch_termtbl_required()`. If true, `mlx5_eswitch_add_termtbl_rule()` moves VLAN push actions from the original `flow_act` into a local terminating action, handles per-destination encapsulation reformat, and gets or creates one termination table per unique action/destination tuple. It then changes each vport destination to `MLX5_FLOW_DESTINATION_TYPE_FLOW_TABLE` and adds the actual FDB rule. On any failure, it reverses the action move, restores destination vport metadata, drops acquired termination-table references, and falls back to adding the original rule directly.

## State and persistence

All persistent state is runtime kernel state and firmware flow-steering state. The hash table stores live termination table handles keyed by action/destination identity. Each handle owns firmware flow table and rule objects until `ref_count` reaches zero. No on-disk state exists. The code mutates caller-owned `flow_act`, `dest`, and `attr->dests[*].termtbl` during setup, so rollback correctness matters.

## Dependencies and integration points

This file depends on mlx5 flow steering (`mlx5_create_auto_grouped_flow_table`, `mlx5_add_flow_rules`, `mlx5_destroy_flow_table`), e-switch offload metadata (`struct mlx5_eswitch`, `struct mlx5_esw_flow_attr`), TC flags, and FDB capabilities from device firmware. It integrates with rule deletion through `mlx5_eswitch_termtbl_put()` calls by the owning e-switch/TC cleanup path.

## Risks

Cache key correctness is critical: missing a field can cause rules with different VLAN/reformat/vport semantics to share a termination table. The hash uses `sizeof(dest->vport.num)` when hashing `vhca_id`, which should be reviewed if the field widths differ. Fallback after partial mutation must keep `attr->dests` and `dest[]` aligned. Concurrent lifetime is protected by `termtbl_mutex`, but destruction occurs after unlock, so callers must not use a handle after put.

## Test signals

Useful signals include TC offload tests for VLAN push on RX, hairpin-to-uplink, encapsulated vport destinations, multi-destination rollback, and shared-rule deletion. Hardware tests should cover devices with and without `VLAN_PUSH_ON_RX`, `termination_table`, and `ignore_flow_level` capabilities. Leak checks should verify firmware table/rule objects are destroyed when the last referencing flow is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads_termtbl.c -->
