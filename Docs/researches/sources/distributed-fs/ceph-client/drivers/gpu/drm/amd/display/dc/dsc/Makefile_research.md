# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/Makefile

## Purpose
This Makefile contributes Display Stream Compression sources to `AMD_DISPLAY_FILES` for the AMD Display Core build. It conditionally includes DCN generation-specific DSC implementations when floating-point DC support is enabled and always includes common DSC rate-control/calculation files.

## Important APIs, types, and functions
- Under `CONFIG_DRM_AMD_DC_FP`, `DSC_DCN20`, `DSC_DCN35`, and `DSC_DCN401` list generation-specific objects: `dcn20_dsc.o`, `dcn35_dsc.o`, and `dcn401_dsc.o`.
- `DSC` lists common objects: `dc_dsc.o`, `rc_calc.o`, and `rc_calc_dpi.o`.
- `AMD_DISPLAY_FILES += $(addprefix $(AMDDALPATH)/dc/dsc/..., ...)` appends all selected objects to the driver build.

## Control flow
Kbuild evaluates the conditional. If `CONFIG_DRM_AMD_DC_FP` is set, it appends DCN20/DCN35/DCN401 DSC implementation objects from their subdirectories. Regardless of that option, it appends common DSC objects under `dc/dsc/`.

## State and persistence behavior
The file has build-time state only through make variables. It does not create runtime state or persistence.

## Dependencies and integration points
It depends on the AMD Display Core Kbuild variable convention (`AMD_DISPLAY_FILES`, `AMDDALPATH`) and the `CONFIG_DRM_AMD_DC_FP` configuration symbol. It integrates DSC object files into the larger amdgpu display driver link.

## Risks and edge cases
Renaming or moving DSC source files without updating this Makefile will cause missing-object build failures. Generation-specific DSC is omitted when floating-point DC support is disabled, so references to those symbols must be similarly conditional. The `DSC_DCN401 +=` assignment is append-style even though it is first use; harmless, but different from the `=` style used for DCN20/DCN35.

## Test signals
Build tests with `CONFIG_DRM_AMD_DC_FP=y` and disabled should verify that the correct object sets are included and that common DSC objects always link. Generation-specific DSC feature tests should cover DCN20, DCN35, and DCN401 configurations.
