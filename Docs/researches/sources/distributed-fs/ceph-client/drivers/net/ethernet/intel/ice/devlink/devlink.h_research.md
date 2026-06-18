# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/devlink/devlink.h

## Purpose
`devlink.h` declares the public devlink-facing entry points used by the rest of the ICE driver. It is a narrow interface between probe/remove, PF/SF lifecycle code, devlink port management, devlink regions, and devlink-rate scheduler export.

## Important APIs, Types, And Functions
The allocation APIs are `ice_allocate_pf()` and `ice_allocate_sf()`. Registration APIs are `ice_devlink_register()`, `ice_devlink_unregister()`, `ice_devlink_register_params()`, and `ice_devlink_unregister_params()`. Port APIs expose PF and VF devlink port creation/destruction. Region APIs expose `ice_devlink_init_regions()` and `ice_devlink_destroy_regions()`. Rate APIs expose `ice_devlink_rate_init_tx_topology()`, `ice_tear_down_devlink_rate_tree()`, and `ice_devlink_rate_clear_tx_topology()`.

## Control Flow
Probe code allocates a PF through devlink rather than embedding devlink allocation directly in the bus probe path. After hardware and PF capability discovery, callers register parameters, ports, and regions. Remove or error unwind paths call matching destroy/unregister functions. Scheduler topology is exported after VSI and scheduler nodes exist and cleared before scheduler teardown or reload.

## State And Persistence
This header owns no state, but every function it declares manipulates PF devlink state: the devlink private PF object, registered devlink params, devlink ports, devlink regions, and cached devlink-rate pointers on scheduler nodes. Persistent behavior is mediated by the implementation, especially NVM-backed scheduler-layer settings and firmware activation.

## Dependencies And Integration Points
The header assumes `struct device`, `struct devlink`, `struct ice_pf`, `struct ice_sf_priv`, `struct ice_vf`, and `struct ice_vsi` are visible to including translation units. It is included by driver initialization, SR-IOV/VF paths, and scheduler or reset code that needs to expose or tear down devlink resources.

## Risks And Test Signals
The main risk is lifecycle mismatch: callers must pair each create/register/init with the matching destroy/unregister operation and must respect locking expectations from the implementation, especially devlink lock use around port operations. Build coverage is a strong signal because missing prototypes or type ordering errors surface immediately. Runtime signals are clean probe/remove, reload, VF creation/removal, and absence of stale devlink ports or regions after teardown.
