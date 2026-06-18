# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Kconfig

Purpose: defines `DRM_SPRD`, the Unisoc/Spreadtrum DRM display driver option.

Important entry: `DRM_SPRD` depends on `ARCH_SPRD || COMPILE_TEST`, DRM, and OF. It selects DMA GEM, KMS helpers, DRM MIPI DSI, and videomode helpers. The module name is `sprd_drm`.

Control flow: enables the master DRM driver plus DPU, DSI, and PLL objects through the Makefile.

State and persistence: no runtime state.

Dependencies and integration: integrates with OF component probing, MIPI DSI panel/bridge ecosystems, DMA GEM buffers, and videomode conversion.

Risks: only OF systems are supported. Runtime PM is implied by the master atomic commit tail helper, so subdrivers must cooperate with power management even though Kconfig does not expose extra clock/reset dependencies.

Test signals: build on ARCH_SPRD and COMPILE_TEST, plus boot-time OF component binding.
