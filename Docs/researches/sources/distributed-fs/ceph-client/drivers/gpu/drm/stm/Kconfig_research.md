# sources/distributed-fs/ceph-client/drivers/gpu/drm/stm/Kconfig

## Purpose
This Kconfig file defines build-time selection for the STMicroelectronics STM DRM display stack: the core STM LTDC DRM driver, the STM wrapper around Synopsys DesignWare MIPI DSI, and the STM LVDS bridge driver.

## Important Options
- `DRM_STM`: tristate core driver for STM32 LTDC display controller. It depends on DRM, `COMMON_CLK`, and STM32 architecture or compile testing. It selects KMS helper, DMA GEM helper, DRM client selection, panel bridge support, videomode helpers, and fb mmap support when framebuffer support is enabled.
- `DRM_STM_DSI`: optional STM-specific DesignWare MIPI DSI extension. It depends on `DRM_STM` and selects `DRM_DW_MIPI_DSI`.
- `DRM_STM_LVDS`: optional STM LVDS display interface transmitter bridge. It depends on `DRM_STM`.

## Control Flow, State, and Persistence
Kconfig has no runtime state, but it controls which objects in the STM DRM directory are compiled and whether symbols may be built-in or modular. Selecting `DRM_STM` makes the core `stm-drm` module possible; DSI and LVDS options add their separate bridge/host modules.

## Dependencies and Integration Points
The dependency set binds the driver to DRM/KMS, common clock, panel/bridge infrastructure, and platform display helpers. `DRM_STM_DSI` integrates with the generic DW MIPI DSI host library, while `DRM_STM_LVDS` integrates as a bridge exposed to the LTDC encoder chain.

## Risks and Test Signals
Risk centers on missing selected helper symbols when dependencies drift, especially for module builds and `COMPILE_TEST`. Build tests should cover `DRM_STM=y/m`, DSI and LVDS enabled independently, `ARCH_STM32` and `COMPILE_TEST`, and fb-enabled configurations for `FB_PROVIDE_GET_FB_UNMAPPED_AREA`.
