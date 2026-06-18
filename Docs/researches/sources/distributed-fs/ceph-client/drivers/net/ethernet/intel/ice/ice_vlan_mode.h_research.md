# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.h

## Purpose
Declares the VLAN mode control surface for hardware-level SVM/DVM behavior.

## Important APIs
`ice_is_dvm_ena()` returns cached DVM status, `ice_set_vlan_mode()` programs the hardware mode during initialization, and `ice_post_pkg_dwnld_vlan_mode_cfg()` applies post-DDP-download VLAN-mode configuration.

## Control Flow and State
The header exposes mode state only through `struct ice_hw *`; actual state lives in `hw->dvm_ena` and hardware/firmware configuration.

## Dependencies and Integration Points
Forward-declares `struct ice_hw`; consumed by VLAN ops, VSI setup, and initialization paths after package download.

## Risks
Callers must not assume `ice_set_vlan_mode()` guarantees DVM; it can legitimately return success while SVM remains active if DVM is unsupported.

## Test Signals
Build users with only the forward declaration and validate mode-dependent call sites under both cached SVM and DVM.
