<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Kconfig

Purpose: Defines the `DRM_TVE200` build option for the Faraday TV Encoder TVE200 DRM driver.

Important APIs/types/functions: The option is a tristate named "DRM Support for Faraday TV Encoder TVE200". It depends on `DRM`, `CMA`, `ARM || COMPILE_TEST`, and `OF`; it selects `DRM_BRIDGE`, `DRM_CLIENT_SELECTION`, `DRM_PANEL_BRIDGE`, `DRM_KMS_HELPER`, and `DRM_GEM_DMA_HELPER`.

Control flow: Kconfig selection controls whether the Makefile emits `tve200_drm.o` built-in, as a module, or not at all. The help text states that module builds are named `tve200_drm`.

State and persistence: No runtime state; it is build-time configuration metadata.

Dependencies and integration points: Captures the driver's need for device-tree platform probing, CMA-backed DMA GEM buffers, bridge/panel integration, and KMS helpers.

Risks and test signals: Build coverage should include ARM and `COMPILE_TEST`, built-in and module builds, and configs with panel/bridge helpers enabled through selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Kconfig -->
