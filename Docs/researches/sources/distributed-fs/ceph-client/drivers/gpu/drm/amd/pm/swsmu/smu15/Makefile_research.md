<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/Makefile

## Purpose

This Makefile adds the SMU15 manager objects to the AMDGPU powerplay build. It defines the local object list for the SMU v15 subdirectory and appends the source-tree-qualified object paths to `AMD_POWERPLAY_FILES`, which the parent AMDGPU build includes.

## Important Variables And Control Flow

`SMU15_MGR` contains `smu_v15_0.o`, `smu_v15_0_0_ppt.o`, and `smu_v15_0_8_ppt.o`. `AMD_SWSMU_SMU15MGR` prefixes those objects with `$(AMD_SWSMU_PATH)/smu15/`. The final line appends that list to `AMD_POWERPLAY_FILES`. There are no conditional branches in this file, so all three objects are part of the configured SMU15 manager build whenever this Makefile is included by the parent AMDGPU make logic.

## State, Dependencies, And Integration

The file has no runtime state. It depends on parent make variables `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`. It integrates the common v15 support file and both IP-specific PPT implementations into the same driver object set, allowing runtime ASIC selection code to call the appropriate `smu_v15_0_0_set_ppt_funcs()` or `smu_v15_0_8_set_ppt_funcs()` symbol.

## Risks And Test Signals

Object-list omissions would produce unresolved symbols or unsupported ASIC paths at runtime. Adding a new SMU15 PPT implementation requires updating this list. Test signals are kernel build success, link success for AMDGPU, and runtime availability of SMU15 initialization on IP 15.0.0 and 15.0.8 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/Makefile -->
