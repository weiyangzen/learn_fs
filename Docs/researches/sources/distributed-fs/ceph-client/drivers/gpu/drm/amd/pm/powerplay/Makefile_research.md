# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/Makefile

## Purpose
This Makefile integrates the legacy PowerPlay implementation into the AMD PM build. It defines the local path, includes subcomponent makefiles for `smumgr` and `hwmgr`, and adds `amd_powerplay.o` to the aggregate `AMD_POWERPLAY_FILES` object list.

## Important Build Flow
`AMD_PP_PATH = ../pm/powerplay` establishes object paths relative to the AMD driver build. `PP_LIBS = smumgr hwmgr` is expanded into per-subdirectory Makefile paths under `$(FULL_AMD_PATH)/pm/powerplay/`, then included. `POWER_MGR-y = amd_powerplay.o` identifies the top-level PowerPlay adapter object, and `AMD_PP_POWER` prefixes it with `$(AMD_PP_PATH)` before appending to `AMD_POWERPLAY_FILES`.

## State, Dependencies, And Integration
The file has no runtime state; its persistence is build-system state in make variables. It depends on parent makefiles defining `FULL_AMD_PATH` and collecting `AMD_POWERPLAY_FILES`. It is the bridge that ensures PowerPlay core, SMU manager, and hardware manager objects are linked into the amdgpu PM component.

## Risks And Test Signals
Risks are path or aggregate-variable drift, missing subdirectory inclusion, and accidental omission of `amd_powerplay.o`. Test signals are successful kernel object builds with PowerPlay enabled, visible compilation of `amd_powerplay.c`, and link resolution for hwmgr/smumgr symbols referenced by the PowerPlay adapter.
