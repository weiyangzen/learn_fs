# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/Makefile

## Purpose
Adds AMD Display Core power-gating controller objects to the kernel build. It currently includes DCN35 and DCN42 power-gating controllers when floating-point Display Core support is enabled.

## Important APIs, Types, and Variables
The Makefile is guarded by `ifdef CONFIG_DRM_AMD_DC_FP`. It defines `PG_DCN35 = dcn35_pg_cntl.o`, expands it through `AMD_DAL_PG_DCN35 = $(addprefix $(AMDDALPATH)/dc/pg/dcn35/,$(PG_DCN35))`, and appends to `AMD_DISPLAY_FILES`. The same pattern is used for `PG_DCN42 = dcn42_pg_cntl.o`.

## Control Flow and State
Build inclusion is conditional and declarative. When the config symbol is absent, no PG controller objects from this directory are appended. When present, both generation-specific object files are compiled into the AMD display file list.

## Dependencies and Integration Points
Depends on outer AMDGPU/DC Makefiles defining `AMDDALPATH`, `AMD_DISPLAY_FILES`, and the kernel config symbol. It integrates the PG controller implementations used by DCN35/DCN42 resource paths and power-management sequences.

## Risks and Test Signals
Risks are missing object inclusion for a new generation, stale config guards, or wrong path prefixes. Test signals include kernel build coverage with `CONFIG_DRM_AMD_DC_FP=y`, link presence of `pg_cntl35_create()` and `pg_cntl42_create()`, and resource code resolving PG controller symbols.
