# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/Makefile

## Purpose
This Kbuild fragment adds AMD DC output timing controller implementations to `AMD_DISPLAY_FILES` when `CONFIG_DRM_AMD_DC_FP` is enabled. It covers DCN10, DCN20, DCN201, DCN30, DCN301, DCN31, DCN314, DCN32, DCN35, DCN401, and DCN42.

## Important APIs, types, and functions
There are no runtime APIs. Important variables are the per-generation object lists, such as `OPTC_DCN10`, `OPTC_DCN20`, `OPTC_DCN201`, `OPTC_DCN30`, `OPTC_DCN301`, through `OPTC_DCN42`, and their `AMD_DAL_OPTC_*` path-prefixed forms.

## Control flow
When the config symbol is set, each object list is prefixed with `$(AMDDALPATH)/dc/optc/<generation>/` and appended to the global AMD display file list. Parent Kbuild logic later compiles and links the selected objects.

## State and persistence behavior
The file has build-time state only and no runtime persistence.

## Dependencies and integration points
It depends on Kbuild, `CONFIG_DRM_AMD_DC_FP`, `AMDDALPATH`, and the generation directories. It integrates timing-generator support into the AMD display core.

## Risks and edge cases
The file must be kept in sync with available generation directories and Kconfig expectations. Adding a new OPTC generation without appending it here prevents it from linking; retaining a removed object breaks builds.

## Test signals
Builds with AMD DC FP enabled should compile every listed generation object. Configuration coverage with the symbol disabled should omit them cleanly.
