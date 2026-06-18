# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/Makefile

## Purpose
This Makefile enumerates the PowerPlay hardware-manager object set. It collects generic hwmgr/PSM/table-processing helpers, ASIC-specific managers, thermal and powertune implementations, OverDrive support, and BACO implementations for several generations.

## Important Build Flow
`HARDWARE_MGR` lists objects such as `hwmgr.o`, `hardwaremanager.o`, `processpptables.o`, `smu7_hwmgr.o`, `vega10_hwmgr.o`, `vega20_hwmgr.o`, `common_baco.o`, `polaris_baco.o`, `fiji_baco.o`, `ci_baco.o`, and related thermal/powertune files. `AMD_PP_HWMGR` prefixes those entries with `$(AMD_PP_PATH)/hwmgr/`, then appends them to `AMD_POWERPLAY_FILES` for the parent build.

## State, Dependencies, And Integration
The file has build-state effects only. It depends on the parent PowerPlay Makefile defining `AMD_PP_PATH` and on the listed source files matching actual ASIC support compiled into the driver. It is the link-time integration point for hwmgr function tables that `hwmgr.c`, `hardwaremanager.c`, and `amd_powerplay.c` call.

## Risks And Test Signals
Risks are missing an object when a function table or ASIC implementation is referenced, retaining obsolete object names, or build-order assumptions hidden in aggregate variables. Test signals are successful compile/link of the amdgpu PM component and resolved symbols for all selected ASIC families and BACO state handlers.
