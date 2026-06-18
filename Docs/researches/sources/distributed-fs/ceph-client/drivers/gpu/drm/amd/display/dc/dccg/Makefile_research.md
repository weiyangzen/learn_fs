# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/Makefile

## Purpose
The DCCG Makefile adds Display Clock Generator objects for multiple DCN generations to `AMD_DISPLAY_FILES` when `CONFIG_DRM_AMD_DC_FP` is enabled.

## Important Build Entries
It defines object groups for DCN20, DCN201, DCN21, DCN30, DCN301, DCN31, DCN314, DCN32, DCN35, DCN401, and DCN42. Each group names one `dcn*_dccg.o`, prefixes it with `$(AMDDALPATH)/dc/dccg/<generation>/`, and appends the resulting path to `AMD_DISPLAY_FILES`.

## Control Flow And State
Build inclusion is controlled entirely by the `ifdef CONFIG_DRM_AMD_DC_FP` block. There is no runtime behavior. The Makefile contributes object paths to the larger AMD display build list.

## Dependencies And Integration Points
It depends on the parent AMD display build system defining `AMDDALPATH` and collecting `AMD_DISPLAY_FILES`. It integrates with Kconfig selection of DC floating-point support and generation-specific DCCG constructors used by resource creation.

## Risks
New DCCG source files must be added here or they will not build. Paths must match directory names. Conditional exclusion under `CONFIG_DRM_AMD_DC_FP` can hide missing compile coverage when FP DC is disabled.

## Test Signals
Kernel build tests with `CONFIG_DRM_AMD_DC_FP=y`, allmodconfig/allyesconfig coverage, and link checks for generation-specific DCCG create functions are the primary signals.
