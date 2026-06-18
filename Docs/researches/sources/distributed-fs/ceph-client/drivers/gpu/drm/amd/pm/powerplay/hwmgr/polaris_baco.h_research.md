# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.h

## Purpose
`polaris_baco.h` declares the Polaris/VegaM BACO transition entry point for the SMU7 PowerPlay backend.

## Important API
`polaris_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)` is the only exported declaration. It allows generic BACO state callbacks to invoke Polaris-specific register sequencing while keeping the public PowerPlay interface ASIC-neutral.

## Dependencies And Integration
The header includes `smu7_baco.h` for `enum BACO_STATE` and shared SMU7 BACO support. It is included by `polaris_baco.c` and used indirectly by SMU7 hwmgr setup code that installs `get_asic_baco_state` and `set_asic_baco_state` callbacks.

## Risks And Test Signals
Risks are prototype drift, incorrect ASIC callback wiring, and accidental use on unsupported chips. Test signals are compile/link success, symbol availability, and correct dispatch for Polaris10/11/12 and VegaM BACO sysfs or reset flows.
