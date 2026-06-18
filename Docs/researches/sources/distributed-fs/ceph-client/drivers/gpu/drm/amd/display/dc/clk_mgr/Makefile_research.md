# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/Makefile

## Purpose
This makefile wires the Display Core clock-manager subcomponent into the AMD display build.

## Important APIs, Types, And Functions
- `CLK_MGR` contributes the common `clk_mgr.o`.
- DCE object groups add DCE100, DCE110, DCE112, and DCE120 managers unconditionally.
- Under `CONFIG_DRM_AMD_DC_FP`, DCN clock manager and SMU support objects from DCN10 through DCN42 are added.
- `AMD_DISPLAY_FILES += ...` is the integration output for the parent build.

## Control Flow
Build flow is declarative: object lists are prefixed with `$(AMDDALPATH)/dc/clk_mgr/` and appended to the global AMD display object list. Floating-point DCN managers are gated by `CONFIG_DRM_AMD_DC_FP`.

## State And Persistence
No runtime state. Build state is the object list produced for the kernel build.

## Dependencies And Integration Points
The file integrates with the AMDGPU display build system via `AMDDALPATH`, `AMD_DISPLAY_FILES`, and kernel config symbols. It must stay aligned with constructors referenced by `clk_mgr.c`.

## Risks
Missing an object here yields unresolved symbols for constructors or destroy functions. Adding constructor cases in `clk_mgr.c` without matching object inclusion breaks builds, especially under config-specific paths.

## Test Signals
Kernel build coverage across configs with and without `CONFIG_DRM_AMD_DC_FP` is the key signal. Linker failures catch stale object lists.
