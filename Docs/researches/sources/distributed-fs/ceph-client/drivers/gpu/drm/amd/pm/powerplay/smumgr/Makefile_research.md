# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/Makefile

## Purpose

This Makefile collects all PowerPlay SMU manager object files and appends them to `AMD_POWERPLAY_FILES`. It is the build glue that ensures the common manager plus ASIC-specific implementations are compiled into the AMDGPU PowerPlay component.

## Important APIs, types, and variables

`SMU_MGR` lists object files: `smumgr.o`, SMU8, Tonga, Fiji, Polaris10, Iceland, SMU7, Vega10, SMU10, CI, Vega12, VegaM, SMU9, and Vega20 managers. `AMD_PP_SMUMGR` prefixes each object with `$(AMD_PP_PATH)/smumgr/`. `AMD_POWERPLAY_FILES += $(AMD_PP_SMUMGR)` exports the objects to the parent build.

## Control flow

Kbuild evaluates the variable assignments during AMDGPU build setup. There is no runtime control flow. The order in `SMU_MGR` controls link input ordering but the actual runtime implementation is selected by ASIC-specific function tables and initialization code.

## State and persistence behavior

The file stores build configuration only. Its effect persists in generated object lists for the current build. It does not create runtime state.

## Dependencies and integration points

It depends on `AMD_PP_PATH` and `AMD_POWERPLAY_FILES` being defined by the surrounding PowerPlay build system. Every object named here must have a corresponding source file in `smumgr/` and must compile under the selected kernel/AMDGPU configuration.

## Risks

Missing an object silently removes a generation-specific SMU backend from the build, causing runtime ASIC initialization failures or unresolved function selection. Adding an object without the source or with unmet dependencies breaks the build. Because all managers are collected here, merge conflicts or stale entries can affect multiple ASIC families.

## Test signals

The primary test is an AMDGPU build that compiles and links PowerPlay successfully. Additional signals include module symbol availability for each manager function table and runtime probe success on ASICs represented by the listed object files.
