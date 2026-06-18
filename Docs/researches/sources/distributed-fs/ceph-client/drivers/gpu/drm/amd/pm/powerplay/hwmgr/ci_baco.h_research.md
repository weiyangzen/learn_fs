# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.h

## Purpose
`ci_baco.h` declares the CI-specific BACO state transition function used by the SMU7/PowerPlay hardware-manager backend.

## Important API
The single API is `ci_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`. It takes the generic PowerPlay hardware-manager context and a BACO state enum from `smu7_baco.h`, allowing the SMU7 backend to wire CI ASICs into the generic `get_asic_baco_state` and `set_asic_baco_state` callbacks exposed by `amd_powerplay.c`.

## Dependencies And Integration
The header includes `smu7_baco.h`, which provides `enum BACO_STATE`, `struct pp_hwmgr` visibility through included headers, and common SMU7 BACO support declarations. It is included by `ci_baco.c` and referenced by ASIC function-pointer setup code outside this file.

## Risks And Test Signals
The risk surface is small but ABI-sensitive: mismatching the prototype or enum source would break function-table wiring. Test signals are successful compilation, correct symbol resolution for `ci_baco_set_state`, and BACO capability/state callbacks dispatching to CI-specific behavior only for supported ASICs.
