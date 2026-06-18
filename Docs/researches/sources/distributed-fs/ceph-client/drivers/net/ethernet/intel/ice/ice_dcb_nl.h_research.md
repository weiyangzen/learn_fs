# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb_nl.h

## Purpose
`ice_dcb_nl.h` declares the DCBNL integration surface for the ice driver and supplies empty fallbacks for non-DCB builds. It lets VSI setup, DCB reconfiguration, and MIB-change handling synchronize netdev DCB state without conditional call sites everywhere.

## Important APIs, Types, And Functions
With `CONFIG_DCB`, it declares `ice_dcbnl_setup()`, `ice_dcbnl_set_all()`, and `ice_dcbnl_flush_apps()`. Without DCB, all three are static inline no-ops. The declarations operate on `struct ice_vsi`, `struct ice_pf`, and `struct ice_dcbx_cfg` types from the broader ice headers.

## Control Flow
`ice_dcbnl_setup()` is expected during netdev/VSI setup to attach DCBNL ops. `ice_dcbnl_set_all()` is called after TC reconfiguration to publish APP state. `ice_dcbnl_flush_apps()` is used when DCBX config changes remove APP TLVs. In non-DCB builds, all flows intentionally do nothing.

## State And Persistence
The header stores no state. Real implementations mutate netdev DCBNL ops and DCB app tables; stubs leave netdev state unchanged.

## Dependencies And Integration Points
It is included by `ice_dcb_lib.c` and other VSI/DCB setup code. It bridges the DCB runtime library with Linux DCBNL when enabled.

## Risks
The main risk is silent no-op behavior in non-DCB builds if a caller expects userspace DCB state to exist. The header also relies on included upstream headers providing forward declarations or full definitions of PF/VSI/DCBX structures.

## Test Signals
Build coverage with `CONFIG_DCB` enabled and disabled, netdev setup verification that `dcbnl_ops` is assigned only when capable, and MIB-change tests confirming app flush/set operations run only in DCB-capable builds.
