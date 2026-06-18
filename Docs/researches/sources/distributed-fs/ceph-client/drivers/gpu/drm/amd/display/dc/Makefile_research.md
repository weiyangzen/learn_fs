# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/Makefile

### Purpose
`dc/Makefile` assembles the AMD Display Core component by selecting DC subdirectory Makefiles and core DC object files into `AMD_DISPLAY_FILES`.

### Important APIs, Types, And Functions
The main variables are `DC_LIBS`, `AMD_DC`, `FILES`, and `AMD_DISPLAY_FILES`. `DC_LIBS` lists DC subcomponents such as basics, bios, dml, clk_mgr, dce, gpio, hwss, irq, link, dsc, resource, optc, dpp, hubbub, hubp, dio, dwb, mpc, and others. `FILES` adds core objects including `dc_dmub_srv.o`, EDID/fused I/O/helper files, and `core/dc*.o` modules.

### Control Flow
The Makefile starts with a base subcomponent list, conditionally adds DCN and floating-point-heavy libraries under `CONFIG_DRM_AMD_DC_FP`, always adds DCE generations and HDCP, conditionally adds DCE6 for SI, builds the list of child Makefiles, includes them, then appends root DC objects with the `$(AMDDALPATH)/dc/` prefix.

### State, Persistence, And Dependencies
Build state is make variables only. It depends on parent definitions of `AMDDALPATH`, `FULL_AMD_DISPLAY_PATH`, `CONFIG_DRM_AMD_DC_FP`, `CONFIG_DRM_AMD_DC_SI`, and the child Makefiles for each subcomponent.

### Integration Points
Included by the AMDGPU display build system to compile DC into the driver. It coordinates source inclusion across DC generations and optional FP-enabled DCN support.

### Risks
Missing or misordered subcomponent entries can omit required objects or duplicate DML inclusion. FP gating affects KCOV instrumentation and DCN libraries; wrong config guards can break non-FP or SI builds. Child Makefile include paths depend on parent variables being set correctly.

### Test Signals
Build AMDGPU with `CONFIG_DRM_AMD_DC_FP` on/off and `CONFIG_DRM_AMD_DC_SI` on/off, check that expected DCN/DCE objects are present, and run incremental builds after touching child Makefiles.
