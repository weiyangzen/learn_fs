# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/Makefile

## Purpose
Builds AMD Display Core resource-pool implementations for DCE and DCN ASIC generations. Resource files describe hardware capabilities and factories for clocks, pipes, links, encoders, and validation functions.

## Important APIs, Types, and Variables
The Makefile appends generation-specific object paths to `AMD_DISPLAY_FILES` through variables such as `RESOURCE_DCE100`, `AMD_DAL_RESOURCE_DCE100`, `RESOURCE_DCN32`, `RESOURCE_DCN401`, and `RESOURCE_DCN42`. DCE60 is gated by `CONFIG_DRM_AMD_DC_SI`. DCN resources are gated by `CONFIG_DRM_AMD_DC_FP`. DCN42 includes both `dcn42_resource.o` and `dcn42_resource_fpu.o` with per-file FPU compile flags using `CFLAGS_...` and `CFLAGS_REMOVE_...`.

## Control Flow and State
Build flow is declarative. DCE80 through DCE120 and DCE100 are always added outside the DCN FP guard, while newer DCN generations are included only under FP-enabled Display Core builds. The FPU flag override isolates DCN42 floating-point code from non-FPU build flags.

## Dependencies and Integration Points
Depends on the outer AMDGPU build system for `AMDDALPATH`, `AMD_DISPLAY_FILES`, `CC_FLAGS_FPU`, and `CC_FLAGS_NO_FPU`. Resource objects created here bind ASIC discovery to the rest of Display Core.

## Risks and Test Signals
Risks include missing a generation object, stale config gating, incorrect FPU flag application, or object order assumptions. Test signals are full kernel builds for SI, non-FP, FP, and DCN42 configurations and link-time resolution of each generation's create-resource-pool symbol.
