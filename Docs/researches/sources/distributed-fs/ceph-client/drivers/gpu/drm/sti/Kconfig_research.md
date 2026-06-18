# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/Kconfig

Purpose: declares `DRM_STI`, the STMicroelectronics stiH4xx DRM driver option.

Important entry: depends on OF, DRM, and `ARCH_STI || COMPILE_TEST`; selects reset controller, DRM client setup, KMS helpers, DMA GEM, DRM panel, firmware loader, and optionally HDMI codec support when sound SoC support exists.

Control flow: enabling the symbol builds the composite `sti-drm` object with mixer, planes, HDMI, VTG, HDA, TV out, HQVDP, AWG utilities, and driver glue.

State and persistence: no runtime state.

Dependencies and integration: ties the DRM driver to firmware loading, panel/HDMI, reset, and optional audio codec infrastructure.

Risks: broad composite selection means build failures in any STI subcomponent affect the whole driver. Optional HDMI audio depends on sound configuration.

Test signals: COMPILE_TEST builds and boot on stiH4xx hardware with HDMI/panel paths.
