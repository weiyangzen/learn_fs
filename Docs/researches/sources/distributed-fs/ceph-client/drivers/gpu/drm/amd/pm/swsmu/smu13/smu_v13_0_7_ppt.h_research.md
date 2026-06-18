# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.h

## Purpose
Declares the SMU13.0.7 PPT backend entry point used by the AMDGPU SWSMU dispatcher.

## Important APIs, Types, And Functions
- The only public symbol is `smu_v13_0_7_set_ppt_funcs(struct smu_context *smu)`.
- The include guard `__SMU_V13_0_7_PPT_H__` prevents duplicate declarations.

## Control Flow
SMU device-selection code includes this header and calls `smu_v13_0_7_set_ppt_funcs` when the probed MP1/SMU IP version corresponds to SMU13.0.7. The implementation then installs the PPT function table, firmware mapping arrays, driver interface version, and mailbox setup.

## State And Persistence
The header owns no state. Its declared function mutates the caller-provided `struct smu_context` when invoked by platform setup.

## Dependencies And Integration Points
The declaration requires `struct smu_context` to be visible from surrounding SWSMU headers. It connects SMU13.0.7-specific code to common AMDGPU SMU initialization.

## Risks And Edge Cases
Prototype drift between this header and `smu_v13_0_7_ppt.c` would break platform setup at build time. Selecting this entry point for the wrong IP revision would install message and table mappings that do not match firmware.

## Test Signals
Build coverage should confirm the declaration matches the implementation. Runtime probe should show `smu->ppt_funcs`, mapping tables, and `smc_driver_if_version` populated after this entry point is called.
