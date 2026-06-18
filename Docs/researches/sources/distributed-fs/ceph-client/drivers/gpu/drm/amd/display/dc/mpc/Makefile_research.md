# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/Makefile

Purpose: contributes generation-specific MPC object files to the AMD display build.

Important build variables: defines `MPC_DCN10`, `MPC_DCN20`, `MPC_DCN30`, `MPC_DCN32`, `MPC_DCN401`, and `MPC_DCN42`, expands each through `$(AMDDALPATH)/dc/mpc/<generation>/`, and appends them to `AMD_DISPLAY_FILES`.

Control flow: all MPC generation object additions are under `ifdef CONFIG_DRM_AMD_DC_FP`.

State/persistence: no runtime state; build state is the appended `AMD_DISPLAY_FILES` list.

Dependencies/integration: depends on the top-level AMD display Makefile providing `AMDDALPATH` and consuming `AMD_DISPLAY_FILES`.

Risks: missing generation object files or an incorrect config guard will break builds for affected ASIC families. Because all objects are behind FP, non-FP configurations must not reference these MPC implementations.

Test signals: kernel build matrix with `CONFIG_DRM_AMD_DC_FP` enabled/disabled and generation-specific resource link coverage.
