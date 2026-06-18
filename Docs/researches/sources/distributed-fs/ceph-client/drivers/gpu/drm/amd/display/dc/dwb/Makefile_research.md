# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/Makefile

## Purpose

`dc/dwb/Makefile` selects Display Writeback block objects for AMD Display Core builds. It adds DCN30 and DCN35 DWB source files to `AMD_DISPLAY_FILES` when floating-point display core support is enabled.

## Important APIs, Types, And Functions

The file defines `DWB_DCN30`, `AMD_DAL_DWB_DCN30`, `DWB_DCN35`, and `AMD_DAL_DWB_DCN35`, appending each expanded path under `$(AMDDALPATH)/dc/dwb/...` to `AMD_DISPLAY_FILES`.

## Control Flow

Build inclusion is gated by `ifdef CONFIG_DRM_AMD_DC_FP`. DCN30 builds `dcn30_dwb.o` and `dcn30_dwb_cm.o`; DCN35 builds `dcn35_dwb.o`.

## State, Dependencies, Risks, And Test Signals

This is build metadata only. It mutates make variables during compilation and has no runtime state. It depends on top-level AMD display Makefile variables and Kconfig. Risks include missing objects when new DWB generations are added, stale path prefixes, and accidental exclusion in non-FP configurations. Build tests with `CONFIG_DRM_AMD_DC_FP=y` should confirm DWB symbols link.
