# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_ops.h

## Purpose
Defines the VLAN operation-table interface used by VSI type-specific code to abstract add/delete filters, stripping/insertion, filtering, and port VLAN operations.

## Important APIs and Types
`struct ice_vsi_vlan_ops` contains function pointers for `add_vlan`, `del_vlan`, `ena/dis_stripping`, `ena/dis_insertion`, `ena/dis_rx_filtering`, `ena/dis_tx_filtering`, `set_port_vlan`, and `clear_port_vlan`. The header declares `ice_vsi_init_vlan_ops()` and `ice_get_compat_vsi_vlan_ops()`.

## Control Flow and State
No direct control flow; operation tables are stored in `struct ice_vsi` and initialized by `ice_vsi_vlan_ops.c` plus PF/VF/SF specializers.

## Dependencies and Integration Points
Includes `ice_type.h` and `ice_vsi_vlan_lib.h`; consumed throughout VLAN, VF reset, and netdev VLAN feature handling.

## Risks
All table fields must be initialized before use. API additions require coordinated updates to unsupported defaults and every type-specific initializer.

## Test Signals
Build-time checks for all initializer users and runtime tests that all operations are non-NULL and return expected mode/type-specific results.
