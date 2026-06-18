# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.h

## Purpose
`fs_core.h` is the internal object model for mlx5 flow steering. It defines the namespace/prio/table/group/FTE/destination tree, shared flow counter structures, flow-table sizing constants, steering modes, resource-owner variants for firmware/software/HWS steering, and traversal helpers used by the rest of `mlx5/core`.

## Important APIs, Types, And Functions
- `struct mlx5_flow_steering` stores the root namespaces for NIC RX/TX, FDB, sniffer, RDMA, port selection, and eswitch ACL roots.
- `struct fs_node` is the common intrusive tree node with parent/root pointers, child list, rw semaphore, refcount, active flag, delete callbacks, and version.
- `struct mlx5_flow_table`, `mlx5_flow_group`, `fs_fte`, `mlx5_flow_rule`, and `mlx5_flow_handle` define the software representation of hardware flow-table entities.
- `struct mlx5_flow_root_namespace` carries steering mode, DR/HWS domain context, table type, root flow table, chain lock, underlay QPN list, and command vtable.
- `struct mlx5_fc`, `mlx5_fc_bulk`, and `mlx5_fc_cache` define flow-counter identity, pooling/local ownership, cached packet/byte/lastuse state, and HWS action refcount data.
- Declared APIs include flow steering lifecycle (`mlx5_fs_core_alloc/init/cleanup/free`), vport ACL namespace add/remove, root lookup, namespace mode/peer setup, flow-counter stats work control, and packet reformat ID lookup.

## Control Flow And State
The header has no implementation, but it encodes the control-flow hierarchy used by flow creation and teardown. Callers traverse from namespace to priority to flow table to group to FTE to destination using the `fs_for_each_*` helpers, and root namespaces serialize flow-table chaining through `chain_lock`. FTEs may carry duplicate destination/action state through `struct fs_fte_dup`, while tables track forward rules pointing at them.

## Dependencies And Integration Points
It depends on Linux refcounting, xarrays/rhashtables, mlx5 public flow-steering UAPI, and steering backends in `steering/sws` and `steering/hws`. It integrates with firmware command implementations, DR/HWS software steering, eswitch FDB/ACL namespaces, RDMA namespaces, IPoIB underlay QPN handling, flow counters, and ethtool/tc steering consumers.

## Risks And Edge Cases
The main risk is lifetime and locking correctness across a deep shared tree: node deletion callbacks, refcounts, hash entries, and table chaining must stay synchronized. Capability macros map many flow-table types to distinct device capability blocks; adding a table type requires updating `MLX5_CAP_FLOWTABLE_TYPE` and the build-time terminal check. Counter structures mix pooled, single, and local ownership and must not be released through the wrong path.

## Test Signals
Useful signals include successful creation/destruction of flow tables/groups/rules across NIC, FDB, RDMA, and ACL namespaces; no refcount or rhashtable leaks under rule churn; correct behavior in DMFS/SMFS/HMFS modes; underlay QPN rules working for IPoIB; and flow-counter cache updates surviving create/destroy races.
