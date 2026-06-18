# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/Makefile

## Purpose

`dc/hubp/Makefile` contributes HUBP generation-specific object files to the AMD Display Core build when `CONFIG_DRM_AMD_DC_FP` is enabled. It lists the HUBP implementation object for each supported DCN generation and appends their source-tree paths to `AMD_DISPLAY_FILES`.

## Important APIs, Types, And Functions

- `ifdef CONFIG_DRM_AMD_DC_FP`: gates all HUBP object inclusion behind the floating-point AMD DC build option.
- Generation variables: `HUBP_DCN10`, `HUBP_DCN20`, `HUBP_DCN201`, `HUBP_DCN21`, `HUBP_DCN30`, `HUBP_DCN31`, `HUBP_DCN32`, `HUBP_DCN35`, `HUBP_DCN401`, and `HUBP_DCN42`.
- Path variables: `AMD_DAL_HUBP_DCN* = $(addprefix $(AMDDALPATH)/dc/hubp/<generation>/,$(HUBP_DCN*))`.
- Build integration: repeated `AMD_DISPLAY_FILES += $(AMD_DAL_HUBP_DCN*)`.

## Control Flow

Make evaluation is straightforward. If `CONFIG_DRM_AMD_DC_FP` is set, each generation declares a one-object list, prefixes it with the corresponding HUBP subdirectory under `$(AMDDALPATH)`, and appends that full object path to the global `AMD_DISPLAY_FILES` aggregate. If the config is unset, the file contributes no objects.

## State And Persistence Behavior

The Makefile mutates only build-system variables during make evaluation. It does not persist runtime state and has no direct hardware side effects. Its effects are reflected in which HUBP object files are compiled and linked into the AMD display driver.

## Dependencies And Integration Points

It depends on the parent AMD display make infrastructure defining `AMDDALPATH`, `AMD_DISPLAY_FILES`, and `CONFIG_DRM_AMD_DC_FP`. It integrates with generation-specific HUBP C files under `dc/hubp/dcn10`, `dcn20`, `dcn201`, `dcn21`, `dcn30`, `dcn31`, `dcn32`, `dcn35`, `dcn401`, and `dcn42`.

## Risks And Edge Cases

- Adding a new HUBP generation requires adding both the object variable and `AMD_DISPLAY_FILES` append; missing either silently omits the implementation from the build.
- The file assumes one object per generation. Multi-file generation implementations would need variable expansion changes.
- Paths depend on `AMDDALPATH` being correct in the parent Makefile.
- All entries are gated by `CONFIG_DRM_AMD_DC_FP`; configurations without it will not compile these HUBP implementations.

## Test Signals

Build logs and `make V=1` output should show the expected HUBP object paths in `AMD_DISPLAY_FILES`. Kernel builds for DCN10 through DCN42 ASIC support catch missing objects, stale paths, and linker errors for missing HUBP constructors or function tables.
