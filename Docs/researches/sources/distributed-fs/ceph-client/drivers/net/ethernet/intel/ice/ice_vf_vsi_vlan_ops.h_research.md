# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_vsi_vlan_ops.h

## Purpose
Declares VF-specific VSI VLAN operation setup and mode-adjustment APIs. It separates always-declared legacy mode helpers from SR-IOV-gated init/port-VLAN operation functions.

## Important APIs
Exports `ice_vf_vsi_cfg_dvm_legacy_vlan_mode()` and `ice_vf_vsi_cfg_svm_legacy_vlan_mode()` unconditionally. Under `CONFIG_PCI_IOV`, exports `ice_vf_vsi_init_vlan_ops()`, `ice_vf_vsi_enable_port_vlan()`, and `ice_vf_vsi_disable_port_vlan()`; otherwise provides empty stubs.

## Control Flow and State
The header itself contains no state. It allows generic VSI initialization code to call VF VLAN setup only when relevant and lets non-SR-IOV builds avoid linking VF-specific operation setup.

## Dependencies and Integration Points
Includes `ice_vsi_vlan_ops.h` for the operation-table type and is included by generic VSI VLAN ops code and VF VLAN implementation.

## Risks
The closing include guard comment names `_ICE_PF_VSI_VLAN_OPS_H_`, which is cosmetic but misleading. Unconditional declarations for legacy helpers require their implementation to be available in build configurations that include the object.

## Test Signals
Compile SR-IOV and non-SR-IOV builds, verifying that generic VSI VLAN setup links correctly and that empty stubs do not alter non-IOV behavior.
