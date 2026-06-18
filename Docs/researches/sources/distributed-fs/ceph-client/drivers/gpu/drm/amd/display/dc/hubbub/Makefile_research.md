# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/Makefile

Purpose: Adds hubbub memory-arbiter/display-hub objects for multiple DCN generations to the AMD display build.

Important APIs and build variables: The object additions are guarded by `CONFIG_DRM_AMD_DC_FP`. It defines generation object lists for DCN10, DCN20, DCN201, DCN21, DCN30, DCN301, DCN31, DCN32, DCN35, DCN401, and DCN42, then appends prefixed paths to `AMD_DISPLAY_FILES`.

Control flow: parent makefiles include this file when building AMD DC. Each block maps one object name to a source-tree path under `$(AMDDALPATH)/dc/hubbub/<generation>/`.

State and persistence: no runtime state; build variables determine object inclusion.

Dependencies and integration: integrates all hubbub generation implementations with the display driver. Relies on parent-provided `AMDDALPATH`, `AMD_DISPLAY_FILES`, and config symbols.

Risks and test signals: missing an object breaks only the affected generation's memory hub programming. Build tests should check expected hubbub objects are present for FP-enabled DC builds and omitted when the guard is disabled.
