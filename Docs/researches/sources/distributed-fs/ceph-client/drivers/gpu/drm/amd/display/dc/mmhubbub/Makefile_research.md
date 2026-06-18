# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/Makefile

Purpose: contributes MMHUBBUB/MCIF writeback object files to the AMD display build.

Important build variables: `MMHUBBUB_DCN20`, `MMHUBBUB_DCN32`, `MMHUBBUB_DCN35`, and `MMHUBBUB_DCN42` name generation-specific objects. Each is expanded through `$(AMDDALPATH)/dc/mmhubbub/<generation>/` and appended to `AMD_DISPLAY_FILES`.

Control flow: DCN20, DCN32, and DCN35 are included only under `ifdef CONFIG_DRM_AMD_DC_FP`; DCN42 is appended outside that guard.

State/persistence: no runtime state; build state is the accumulated `AMD_DISPLAY_FILES` variable.

Dependencies/integration: depends on top-level AMD display Makefile variables and the object files produced by the generation folders.

Risks: the guard difference means DCN42 can be built in configurations where earlier MMHUBBUB generations are not. Missing object paths or inconsistent `CONFIG_DRM_AMD_DC_FP` assumptions will surface as build failures.

Test signals: kernel build matrix with and without `CONFIG_DRM_AMD_DC_FP`, and link coverage for DCN42 references.
