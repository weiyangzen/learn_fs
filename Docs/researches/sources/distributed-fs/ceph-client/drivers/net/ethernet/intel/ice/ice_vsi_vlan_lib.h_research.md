# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.h

## Purpose
Declares low-level VSI VLAN manipulation functions and the saved VLAN-info structure used to restore state after port VLAN removal.

## Important APIs and Types
`struct ice_vsi_vlan_info` stores `sw_flags2`, `inner_vlan_flags`, and `outer_vlan_flags`. The prototypes cover add/delete VLAN, inner stripping/insertion, inner port VLAN, Rx/Tx filtering, outer stripping/insertion, outer port VLAN, and generic port VLAN clearing.

## Control Flow and State
The header has no control flow. It defines the common low-level surface that mode/type-specific operation tables bind to.

## Dependencies and Integration Points
Includes Linux types and `ice_vlan.h`; forward-declares `struct ice_vsi`. Consumed by PF/VF/SF VLAN op setup and host VF reset rebuild.

## Risks
Because functions are low-level, callers should normally use `ice_vsi_vlan_ops` rather than direct calls so SVM/DVM and VSI type semantics are respected.

## Test Signals
Compile all operation-table users and validate direct callers intentionally bypass mode dispatch only where documented.
