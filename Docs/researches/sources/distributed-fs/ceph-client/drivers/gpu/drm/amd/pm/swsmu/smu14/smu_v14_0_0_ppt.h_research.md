# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_0_ppt.h

## Purpose
Declares the setup entry point for the SMU14.0.0-family PPT backend.

## Important APIs, Types, And Functions
- The sole exported declaration is `smu_v14_0_0_set_ppt_funcs(struct smu_context *smu)`.
- The include guard is `__SMU_V14_0_0_PPT_H__`.

## Control Flow
AMDGPU SMU IP-version selection includes this header and invokes `smu_v14_0_0_set_ppt_funcs` for supported SMU14.0.0-family APUs. The implementation installs the backend function table, firmware mappings, table mappings, APU flag, driver interface version, and mailbox registers.

## State And Persistence
The header has no state. The declared function mutates `struct smu_context` and indirectly controls later firmware-visible state through the installed callbacks.

## Dependencies And Integration Points
It depends on the SWSMU context definition and integrates the SMU14.0.0 PPT implementation with common AMDGPU SMU initialization.

## Risks And Edge Cases
A wrong platform selector would install SMU14.0.0 message mappings against incompatible PMFW. Prototype drift would break build-time integration.

## Test Signals
Build should validate the prototype against callers and implementation. Runtime probe should confirm `ppt_funcs`, `feature_map`, `table_map`, `is_apu`, and the selected SMU14 driver interface version are set after this function runs.
