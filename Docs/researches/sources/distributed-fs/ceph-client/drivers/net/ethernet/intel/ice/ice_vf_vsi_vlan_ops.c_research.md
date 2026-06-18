# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.c

## Purpose
Configures the VLAN operation tables for VF VSIs. It maps generic inner/outer VSI VLAN operations to behavior appropriate for port VLANs, single VLAN mode, double VLAN mode, and legacy VFs that negotiated only the older VLAN offload.

## Important APIs and Functions
- `ice_vf_vsi_init_vlan_ops()` initializes a VF VSI's VLAN op tables based on DVM/SVM and whether the VF has a port VLAN.
- `ice_vf_vsi_enable_port_vlan()` and `ice_vf_vsi_disable_port_vlan()` switch operation tables when host port VLAN configuration changes.
- `ice_vf_vsi_cfg_dvm_legacy_vlan_mode()` configures DVM behavior for older VFs without VLAN v2 support.
- `ice_vf_vsi_cfg_svm_legacy_vlan_mode()` disables Rx VLAN filtering for old SVM VFs using legacy VLAN offload.
- Local no-op functions allow successful no-op behavior where the PF must not expose an operation to a VF.

## Control Flow
`ice_port_vlan_on()` disables VF add/delete VLAN on inner VLANs in DVM, assigns outer port VLAN set/clear operations, prevents disabling Rx filtering, and allows Rx filtering enable. In SVM it binds port VLAN operations to inner VLAN helpers. `ice_port_vlan_off()` enables normal add/delete and stripping/insertion operations, selecting outer ops under DVM and inner ops under SVM; Rx filtering enable may become a no-op unless `ICE_FLAG_VF_VLAN_PRUNING` is set.

Legacy DVM mode disables both Rx and Tx VLAN filtering and outer/inner offloads so old VFs can use software VLAN handling when no port VLAN is present. Legacy SVM mode only disables Rx VLAN filtering.

## State and Persistence
The file mutates function pointers in `vsi->inner_vlan_ops` and `vsi->outer_vlan_ops`; it does not directly store hardware state except by invoking the selected operations. Port VLAN state is read from `vsi->vf->port_vlan_info`; global mode is read from cached `hw->dvm_ena`.

## Dependencies and Integration Points
Depends on `ice_vsi_vlan_ops.h`, `ice_vsi_vlan_lib.h`, `ice_vlan_mode.h`, `ice_sriov.h`, VF state from `ice_vf_lib.h`, and PF flags. Used during VSI initialization, VF reset/rebuild, and host port VLAN changes.

## Risks
- Operation-table mutation must remain synchronized with actual hardware port VLAN state.
- Legacy DVM path assigns inner `dis_stripping`/`dis_insertion` to outer disabling helpers, which is unusual and should be regression-tested.
- No-op success functions intentionally hide unsupported operations from some call paths; misuse can mask missing hardware programming.

## Test Signals
Test SVM and DVM with VF port VLAN on/off, legacy VLAN-only VFs, VLAN v2 VFs, `ICE_FLAG_VF_VLAN_PRUNING` enabled/disabled, priority-only port VLANs, and reset rebuild preserving operation tables.
