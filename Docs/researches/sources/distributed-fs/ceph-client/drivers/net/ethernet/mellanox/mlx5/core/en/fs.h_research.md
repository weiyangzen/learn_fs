# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs.h

## Purpose

`en/fs.h` is the mlx5e Ethernet flow-steering interface. It defines flow table wrappers, L2/promisc/VLAN/TTC level constants, hash constants, steering object forward declarations, feature-specific stubs, and public APIs for creating, destroying, and accessing mlx5e flow-steering state.

## Important APIs, Types, and Functions

- `struct mlx5e_flow_table`, `mlx5e_l2_rule`, `mlx5e_promisc_table`, and `mlx5e_l2_table` model mlx5e flow table/group/rule state.
- Flow table level enums define TC, promisc, NIC, VLAN, L2, TTC, inner TTC, UDP/ANY redirect, TLS, ARFS, IPsec/PSP levels.
- ARFS APIs compile to real declarations or `-EOPNOTSUPP`/no-op stubs.
- Core APIs create/destroy TTC and flow steering, initialize/cleanup `mlx5e_flow_steering`, get/set submodules (VLAN, TC, TTC, ARFS, PTP, ANY, UDP, TLS), manage namespaces, set state flags, update RX mode, add/remove VLAN/MAC traps, and handle VLAN RX add/kill.
- Logging macros `fs_err/dbg/warn/warn_once` route through the owning mdev.

## Control Flow

mlx5e profile/netdev setup initializes flow steering, creates base flow tables, attaches TTC tables to RX resources, then optional features add tables at predefined levels. Runtime calls update L2 address lists, VLAN rules, traps, ARFS, ethtool steering, PTP FS, and redirect tables. Submodule setters/getters hide the private `mlx5e_flow_steering` layout.

## State and Persistence Behavior

Flow steering state persists in `struct mlx5e_flow_steering` and submodule pointers. Flow tables own firmware `mlx5_flow_table` objects, flow groups, rules, active VLAN bitmaps, L2 address hash lists, and feature-specific tables. State is hardware-resident and must be destroyed in reverse dependency order.

## Dependencies and Integration Points

Depends on mlx5 flow steering core, TTC library, mod header, RX resources, netdev, ethtool RXNFC, ARFS, TLS/IPsec/PSP optional features, traps, VLAN, and debugfs roots. It is the common interface for receive steering and many accelerators.

## Risks and Edge Cases

- Flow table level constants overlap intentionally for mutually exclusive optional features; additions must avoid unintended priority conflicts.
- ARFS stubs return `-EOPNOTSUPP` for enable/disable when disabled; callers must handle this.
- Submodule pointers are opaque; lifecycle mismatches can leave TTC destinations pointing at destroyed tables.
- Trap APIs rely on devlink trap IDs and TIR numbers being valid.

## Test Signals

Exercise netdev open/close flow steering creation/destruction, VLAN add/kill, promisc/allmulti, L2 address changes, TTC routing, ARFS/RXNFC enabled/disabled builds, PTP RX FS, traps, and accelerator tables. Use flow steering tracepoints to validate object order.
