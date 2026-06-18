# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/Makefile

## Purpose
Adds SMU14 manager objects to the AMDGPU powerplay build.

## Important APIs, Types, And Functions
- `SMU14_MGR` lists the SMU14 object files: `smu_v14_0.o`, `smu_v14_0_0_ppt.o`, and `smu_v14_0_2_ppt.o`.
- `AMD_SWSMU_SMU14MGR` prefixes those objects with `$(AMD_SWSMU_PATH)/smu14/`.
- `AMD_POWERPLAY_FILES += $(AMD_SWSMU_SMU14MGR)` contributes them to the parent AMDGPU powerplay object list.

## Control Flow
When the parent powerplay makefiles include this file, the SMU14 object list is expanded into source-tree-relative object paths and appended to the global AMD powerplay build variable. Kbuild then compiles and links the SMU14 common layer and PPT backends into the AMDGPU driver when the surrounding configuration enables AMDGPU powerplay support.

## State And Persistence
The file has no runtime state. Its persistent effect is build graph membership for SMU14 sources.

## Dependencies And Integration Points
It depends on the parent make environment defining `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`. It integrates SMU14 sources with the larger AMDGPU SWSMU build and must stay aligned with files present in the `smu14` directory.

## Risks And Edge Cases
Removing an object here drops the corresponding platform backend from the driver even if the source remains. Adding a missing object causes build failure. The listed SMU14.0.2 backend is outside this work item but is part of the same build group, so dependency changes in common SMU14 code can affect it.

## Test Signals
Kbuild should compile all listed objects without missing-file errors. Link output should include SMU14 common and PPT setup symbols used by AMDGPU IP-version selection.
