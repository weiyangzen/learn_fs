# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/Makefile

## Purpose
This Kbuild fragment adds AMD DC output pixel processor implementations to `AMD_DISPLAY_FILES` when `CONFIG_DRM_AMD_DC_FP` is enabled. It covers DCN10, DCN20, and DCN35 OPP generations.

## Important APIs, types, and functions
The file has no C APIs. Its important build variables are `OPP_DCN10`, `AMD_DAL_OPP_DCN10`, `OPP_DCN20`, `AMD_DAL_OPP_DCN20`, `OPP_DCN35`, and `AMD_DAL_OPP_DCN35`, each mapping generation-local object names to paths under `$(AMDDALPATH)/dc/opp/...`.

## Control flow
Kbuild evaluates the block only under `ifdef CONFIG_DRM_AMD_DC_FP`. Each object list is prefixed with its source directory and appended to `AMD_DISPLAY_FILES`, which is later consumed by the parent AMD display build.

## State and persistence behavior
There is no runtime state. The file only controls compile-time object selection.

## Dependencies and integration points
It depends on the kernel build system, `CONFIG_DRM_AMD_DC_FP`, `AMDDALPATH`, and the presence of `dcn10_opp.o`, `dcn20_opp.o`, and `dcn35_opp.o`. It integrates the OPP implementation layer into the larger DC object set.

## Risks and edge cases
If a generation object is renamed, moved, or added without updating this file, that OPP implementation will not link. The file intentionally gates floating-point DC code; build configurations without `CONFIG_DRM_AMD_DC_FP` omit these objects.

## Test signals
Build tests with AMD DC FP enabled should compile and link the three OPP object files. Missing-object, disabled-config, and incremental-build coverage are the relevant validation signals.
