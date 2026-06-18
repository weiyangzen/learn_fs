# `sources/distributed-fs/ceph-client/include/linux/mlx5/fs.h`

## Purpose

`fs.h` is the public mlx5 flow-steering API. It defines namespaces, table types, table attributes, match specifications, destinations, actions, groups, counters, modify-header/reformat objects, match definers, root namespace handling, and helper constants used by Ethernet, RDMA, vDPA, eswitch, IPsec, MACsec, LAG, and packet-classification paths.

## Important APIs, Types, and Constants

- General constants include `MLX5_FS_DEFAULT_FLOW_TAG`, `MLX5_RDMA_TRANSPORT_BYPASS_PRIO`, `MLX5_FS_MAX_POOL_SIZE`, `LEFTOVERS_RULE_NUM`, `MLX5_FS_VLAN_DEPTH`, and `MLX5_DECLARE_FLOW_ACT()`.
- `enum mlx5_flow_destination_type` covers no destination, vport, flow table, TIR, sampler, uplink, port, counter, flow-table number, range, table type, and VHCA RX.
- Action flags extend firmware flow actions with `MLX5_FLOW_CONTEXT_ACTION_FWD_NEXT_PRIO`, encrypt/decrypt, and forward-next-namespace. Flow-table flags describe tunnel reformat/decap, termination, unmanaged tables, other/uplink vports, and other eswitch ownership.
- `enum mlx5_flow_namespace_type` defines the high-level steering namespaces for NIC RX/TX, MACsec, LAG, offloads, ethtool, kernel, leftovers, FDB, eswitch ingress/egress, sniffer, RDMA RX/TX, port select, counters, IPsec, MACsec, and RDMA transport.
- FDB priority constants such as `FDB_DROP_ROOT`, `FDB_TC_OFFLOAD`, `FDB_BR_OFFLOAD`, and `FDB_SLOW_PATH` define ordering within FDB steering.
- `enum fs_flow_table_type` maps software table classes to firmware op-mod table types: NIC RX/TX, eswitch ACLs, FDB, sniffer, RDMA, port select, FDB RX/TX, and RDMA transport.
- `struct mlx5_flow_context` carries flow tag/source flags; `struct mlx5_flow_spec` carries match criteria enable bits plus match mask/value arrays sized to `fte_match_param`.
- `struct mlx5_flow_destination` is a tagged union for all destination forms, including table pointers/numbers, TIR, counters, vport fields with VHCA ID and packet reformat, range hit/miss tables, sampler ID, and VHCA RX ID.
- `struct mlx5_flow_table_attr` defines priority, maximum FTEs, level, flags, UID, vport, eswitch owner VHCA ID, optional next table, and autogroup sizing/reserved entries.
- Table and group APIs include namespace lookup (`mlx5_get_flow_namespace()`, `mlx5_get_fdb_sub_ns()`, `mlx5_get_flow_vport_namespace()`), table creation variants (`mlx5_create_flow_table()`, `mlx5_create_auto_grouped_flow_table()`, `mlx5_create_vport_flow_table()`, `mlx5_create_lag_demux_flow_table()`), `mlx5_destroy_flow_table()`, `mlx5_create_flow_group()`, and `mlx5_destroy_flow_group()`.
- `struct mlx5_flow_act` combines action bits, modify-header object, packet-reformat object, crypto parameters, flags, VLAN stack, IB counters, selected flow group, and ASO execution data.
- Rule APIs include `mlx5_add_flow_rules()`, `mlx5_del_flow_rules()`, and `mlx5_modify_rule_destination()`.
- Counter APIs include `mlx5_fc_create()`, local counter create/destroy/get/put, cached and raw query helpers, synchronous query, ID lookup, and last-use query.
- Object APIs include RX underlay QPN add/remove, modify-header alloc/dealloc, match definer create/destroy/ID lookup, packet reformat alloc/dealloc, `mlx5_flow_table_id()`, root namespace lookup, and `mlx5_fs_set_root_dev()`.

## Control Flow and Lifetimes

The normal flow-steering lifecycle is: get a namespace, create a flow table with attributes, optionally create flow groups from firmware inbox criteria, allocate supporting objects such as counters, modify headers, packet reformat objects, definers, or crypto objects, then add rules with a match spec, action, and destination array. `mlx5_add_flow_rules()` returns an opaque handle that must be deleted with `mlx5_del_flow_rules()`. Tables and groups must be destroyed after all dependent rules are removed. Counter objects and packet transformation objects have their own create/destroy or get/put lifetimes.

Autogrouped tables move group selection into flow-steering internals using `ft_attr.autogroup`, while explicit groups require caller-provided firmware inbox data containing start/end flow indexes and match criteria. Forwarding can target next priority/namespace, explicit destination tables, vports, uplink, TIRs, counters, ranges, or no destination for drop/terminal/action-only rules depending on action bits and namespace semantics.

## State and Persistence Behavior

Most objects are opaque handles backed by firmware resources and flow-steering software state: namespaces, tables, groups, rules, counters, modify headers, match definers, and packet reformats. They persist until explicit destruction. `struct mlx5_flow_spec`, `struct mlx5_flow_act`, and `struct mlx5_flow_destination` are caller-owned setup descriptors. Counters can have cached state (`mlx5_fc_query_cached*()` and last-use data), local reference state, and synchronous firmware query state.

## Dependencies and Integration Points

The header depends on `driver.h` and `mlx5_ifc.h` for device, firmware structure sizes, and action constants. It is heavily used by mlx5 Ethernet receive/transmit steering, TC offloads, eswitch ACL/bridge/offload tables, MACsec and IPsec crypto steering, RDMA and RDMA transport steering, LAG demux, vDPA multicast/unicast filters, ethtool flow rules, accelerated RFS, and root namespace ownership transitions. `lag.h` uses `mlx5_flow_table_attr`; `eswitch.h` returns `mlx5_flow_handle` objects created through this API.

## Risks and Edge Cases

- Match masks and values are raw firmware-layout arrays; wrong `match_criteria_enable`, mask width, or field packing can make rules too broad, too narrow, or invalid.
- Destination union fields must match `type`; misuse can pass table IDs where pointers or vport metadata are expected.
- Rule/table/group/object destruction ordering is critical. Rules generally must be removed before groups, groups before tables, and actions/counters/reformat objects after dependent rules are gone.
- Multi-destination, crypto, modify-header, VLAN, ASO, and range flows combine several subsystems and need capability checks in callers.
- Flow levels/priorities and FDB priority constants affect packet path ordering. Incorrect levels can shadow security, MACsec/IPsec, bridge, TC, or slow-path rules.
- Counter cached queries may lag hardware state; callers needing exact packet/byte values must use synchronous query paths.

## Test Signals

Validation should include compile coverage for all mlx5 users, create/add/delete/destroy cycles under error unwinds, flow rule matching tests for NIC RX/TX, FDB, eswitch ACL, RDMA RX/TX, RDMA transport, LAG demux, IPsec/MACsec crypto paths, counter query tests including cached and synchronous modes, modify-header/reformat allocation failures, namespace root-device changes, and hardware traffic tests verifying priority ordering and destination behavior.
