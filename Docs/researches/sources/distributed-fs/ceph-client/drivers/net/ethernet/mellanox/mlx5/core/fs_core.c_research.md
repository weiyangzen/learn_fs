<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.c

## Purpose

This file is the main mlx5 flow steering object manager. It builds namespace trees for NIC RX/TX, FDB, sniffer, port selection, RDMA, RDMA transport, and per-vport ACL flows; allocates and destroys flow tables/groups/entries/rules; maintains rule sharing and duplicate-match behavior; keeps firmware miss chains/root tables synchronized; and exposes resource helpers for modify headers, packet reformat, match definers, and underlay QPN roots.

## Important APIs, types, and functions

- Static `init_tree_node` topologies describe root namespace layouts and capability requirements.
- Generic tree helpers (`tree_init_node`, `tree_add_node`, `tree_get_node`, `tree_put_node`, `tree_remove_node`) manage refcounted nodes with per-node semaphores.
- Object allocators create flow tables, flow groups, FTEs, rules, and handles; rhashtable/rhltable indexes accelerate group and FTE lookup.
- Public APIs include `mlx5_create_flow_table`, `mlx5_create_auto_grouped_flow_table`, `mlx5_create_flow_group`, `mlx5_add_flow_rules`, `mlx5_del_flow_rules`, `mlx5_destroy_flow_table`, `mlx5_destroy_flow_group`, namespace getters, vport ACL add/remove, `mlx5_fs_core_alloc/init/cleanup/free`, underlay QPN add/remove, modify-header/reformat/definer helpers, namespace peer/mode setters, and `mlx5_fs_get_capabilities`.
- Chain helpers find adjacent flow tables, connect previous priorities to new tables, update root flow tables, and rewrite `FWD_NEXT_*` rules when next tables change.

## Control flow

Allocation initializes flow-counter stats, table-size pools, steering mode, and slab caches. Initialization registers the devlink flow-steering-mode parameter and creates only the root namespaces supported by device capabilities. Flow table creation validates priority/level, creates firmware table through the root command provider, connects previous miss paths and root table if managed, then inserts the table into the tree sorted by level. Rule insertion validates match masks, destinations, and action conflicts; finds matching flow groups/FTEs; appends to existing FTEs when allowed; handles duplicate-match `NO_APPEND` through pending duplicate state; or creates autogroups/FTEs as needed. Deletion removes rule nodes under the FTE lock, updates firmware if destinations remain, or deletes the FTE and releases parent references when empty.

## State and persistence

All state is runtime kernel and firmware state. `struct mlx5_flow_steering` owns root namespace pointers, steering mode, slab caches, FDB sub-namespace arrays, vport ACL xarrays, and RDMA transport root arrays. Root namespaces own command providers, root table pointer, underlay QPN list, and `chain_lock`. Flow tables own group hash tables, autogroup accounting, level/type/vport/flags, and forward-next rule lists. Flow groups own FTE hash tables and IDA index allocation. FTEs own match values, actions/destinations, optional duplicate pending state, and child rule nodes.

## Dependencies and integration points

The file depends on `fs_cmd.h` providers, `fs_ft_pool`, mlx5 capabilities, e-switch total-vport information, devlink parameters, DR/HWS support probes and command providers, Linux xarray/rhashtable/IDA/refcount/rwsem primitives, and tracepoints. It is consumed by mlx5 Ethernet, RDMA, e-switch, TC, IPsec/MACsec, sniffer, and steering-mode management paths.

## Risks

This is a high-concurrency, high-blast-radius file. Refcount/lock ordering bugs can leak nodes, delete live firmware objects, or deadlock; the nested lock classes are important. Firmware chain synchronization must remain correct when first/last tables in a priority are created or destroyed. Autogroup sizing and IDA allocation errors can produce `-ENOSPC` despite table capacity if accounting drifts. Duplicate-match pending rules are subtle: pending children are committed only when the active FTE is deleted. Namespace mode changes are only safe at init time and currently restricted to root FDB namespaces. `mlx5_fs_set_root_dev()` requires empty RDMA transport namespaces before root device migration.

## Test signals

Core tests should cover namespace creation under varied capability sets, flow table create/destroy ordering, root update with underlay QPN lists, flow group creation and autogroup allocation, FTE append and `NO_APPEND` duplicate behavior, rule deletion with counters and forwarding destinations, `FWD_NEXT_PRIO/NS` rewrites, vport ACL namespace add/remove, devlink mode validation/set/get, modify-header/reformat/definer lifecycle, RDMA transport root device migration, and cleanup leak detection. Lockdep, KASAN, fault injection on command providers, and firmware command tracing are especially useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.c -->
