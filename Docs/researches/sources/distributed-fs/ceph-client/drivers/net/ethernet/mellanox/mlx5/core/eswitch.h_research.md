# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch.h

## Purpose
Defines the mlx5 E-Switch internal ABI: core data structures, flags, vport and FDB state, offload attributes, iterator macros, exported function prototypes, devlink hooks, and no-op stubs when `CONFIG_MLX5_ESWITCH` is disabled. It is the shared contract between core eswitch code, offloads, legacy ACLs, representors, TC, bridge, QoS, devlink, IPsec, LAG, and SF support.

## Important APIs, Types, and Functions
Key types include `struct mlx5_eswitch`, `struct mlx5_vport`, `struct mlx5_eswitch_fdb`, `struct mlx5_esw_offload`, `struct mlx5_vport_info`, ingress/egress ACL structures, `struct mlx5_esw_flow_attr`, `struct mlx5_vport_tbl_attr`, and `struct esw_vport_tbl_namespace`. Important enums and flags describe mapped object types, vport events, egress ACL kind, metadata features, FDB-created state, destination flags, VLAN action flags, flow match levels, and xarray vport marks. The header declares lifecycle, vport config, offloaded rule, term table, restore, devlink mode/inline/encap, representor, VHCA map, mode lock, block/unblock, IPsec, LAG demux, and QoS entry points.

## Control Flow and State
Executable logic is mostly inline helpers and iterator macros. `mlx5_esw_allowed()` gates operations to eswitch-manager devices. Helpers classify manager/owner vports, translate devlink port indexes, test FDB creation, derive first host vport, and dispatch xarray iteration over all, VF, host-function, ECVF, and representor entries. Compile-time stubs preserve callers when eswitch support is disabled, returning success/no-op for lifecycle calls and capability-style errors for unsupported flow operations.

## State and Persistence Behavior
`struct mlx5_eswitch` is the persistent in-kernel owner for an eswitch instance: it stores the core device, notifier, legacy and offloads FDB union, multicast table, debugfs root, workqueue, vports xarray, mode and flags, locks, QoS domain, bridge/offload state, enabled counts, host function state, devcom pairing, IPsec count, and operation-in-progress flag. `struct mlx5_vport` persists per-vport address lists, promisc/allmulti rules, ACL tables, metadata, VHCA ID, adjacent/delegated info, admin info, QoS nodes, enabled state, xarray index, and devlink port. `struct mlx5_esw_flow_attr` carries TC offload per-rule state including input reps, VLAN edits, destinations, packet reformats, tunnel and decap data.

## Dependencies and Integration Points
Includes kernel networking/devlink/xarray headers, mlx5 device/vport/flow steering public headers, MPFS and fs-chains libraries, SF support, TC connection tracking, and TC sample support. It is included by `eswitch.c`, `eswitch_offloads.c`, `esw/vporttbl.c`, ACL modules, bridge/offload modules, representor code, TC offload code, IPsec offload paths, and devlink port-function handlers. The fallback stubs are integration-critical for builds without eswitch support.

## Risks and Test Signals
Because this is a broad internal ABI, layout or semantic changes can break many subsystems at once. Risks include stale comments versus lock requirements, exhausting xarray marks, incorrect vport iteration bounds on ECPF/ECVF systems, destination array overflow relative to `MLX5_MAX_FLOW_FWD_VPORTS`, metadata bit-field collisions with TC internal ports or tunnel marks, and stub behavior diverging from real behavior. Test signals include `allyesconfig` and no-eswitch builds, sparse/compile coverage for all users, switchdev TC offload tests, devlink port-function tests, multiport/LAG pairing, SF and ECPF topologies, and lockdep around mode and QoS locks.
