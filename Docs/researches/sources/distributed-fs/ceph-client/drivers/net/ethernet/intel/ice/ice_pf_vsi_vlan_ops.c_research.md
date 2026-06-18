# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_pf_vsi_vlan_ops.c

## Purpose
`ice_pf_vsi_vlan_ops.c` initializes the VLAN operation vector for a PF VSI. It chooses whether VLAN add/delete, stripping, insertion, and filtering operations should be wired to the VSI's outer-VLAN or inner-VLAN operation table based on whether Double VLAN Mode is enabled.

## Important APIs, Types, and Functions
- `ice_pf_vsi_init_vlan_ops(struct ice_vsi *vsi)` is the only function.
- It fills `struct ice_vsi_vlan_ops` function pointers with `ice_vsi_add_vlan()`, `ice_vsi_del_vlan()`, outer or inner stripping/insertion helpers, and shared RX VLAN filtering helpers.
- It selects `vsi->outer_vlan_ops` when `ice_is_dvm_ena(&vsi->back->hw)` is true, otherwise `vsi->inner_vlan_ops`.

## Control Flow
The function reads the hardware VLAN mode through the PF back pointer. In DVM mode, it points the active operation table at outer VLAN operations. In non-DVM/SVM mode, it points at inner VLAN operations. Add/delete and RX filtering functions are common in both branches; stripping and insertion functions differ by inner vs outer VLAN context.

## State and Persistence
The function mutates function pointers inside the `ice_vsi` instance. It does not directly program hardware, persist settings, or allocate memory. Later VLAN operations persist or clear hardware state through the selected function pointers.

## Dependencies and Integration Points
It depends on `ice_vsi_vlan_ops.h`, `ice_vsi_vlan_lib.h`, `ice_vlan_mode.h`, `ice.h`, and its own header. It integrates with VSI setup paths that need the correct VLAN behavior before netdev or switchdev VLAN operations are invoked.

## Risks
The function assumes `vsi`, `vsi->back`, and `vsi->back->hw` are valid. If called before VLAN mode is finalized or after a mode transition without reinitialization, later operations may target the wrong inner/outer VLAN context. Function pointer initialization is partial to one table per mode, so users must call the correct table for the active mode.

## Test Signals
Tests should verify that DVM mode initializes `outer_vlan_ops` with outer stripping/insertion functions and SVM mode initializes `inner_vlan_ops` with inner functions. Integration signals include successful VLAN add/delete, RX filtering enable/disable, and insertion/stripping behavior on PF VSIs in both VLAN modes.
