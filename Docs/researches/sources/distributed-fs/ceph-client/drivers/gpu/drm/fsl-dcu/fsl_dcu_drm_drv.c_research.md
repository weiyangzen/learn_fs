<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.c

## Purpose

This is the platform and DRM core entry point for the Freescale/NXP DCU DRM driver. It binds `fsl,ls1021a-dcu` and `fsl,vf610-dcu` platform devices, maps the DCU register block through regmap, enables clocks, registers a derived pixel-clock divider, initializes optional TCON bypass support, allocates/registers the DRM device, installs IRQ/vblank handling, and wires system suspend/resume.

## Important APIs, Types, And Functions

Key functions are `fsl_dcu_drm_probe()`, `fsl_dcu_drm_remove()`, `fsl_dcu_drm_shutdown()`, `fsl_dcu_load()`, `fsl_dcu_unload()`, `fsl_dcu_drm_irq()`, `fsl_dcu_irq_install()`, `fsl_dcu_drm_pm_suspend()`, and `fsl_dcu_drm_pm_resume()`. The file defines the `fsl_dcu_drm_driver`, `fsl_dcu_drm_platform_driver`, SoC data for LS1021A and VF610, an OF match table, `legacyfb_depth`, and a regmap configuration with `DCU_INT_STATUS` and `DCU_UPDATE_MODE` marked volatile.

## Control Flow

Probe allocates `struct fsl_dcu_drm_device`, selects SoC data from OF, maps MMIO, fetches IRQ and clocks, enables the DCU clock, chooses the pixel-clock parent (`pix` clock or legacy `dcu` fallback), registers a divider on `DCU_DIV_RATIO`, initializes optional TCON, allocates the DRM device, stores private pointers, registers the DRM device, and starts fbdev/client setup. Driver load initializes KMS objects, enables LS1021A SCFG PIXCLK if available, initializes vblank, installs IRQ, and validates legacy fb depth. IRQ reads `DCU_INT_STATUS`, forwards vblank bit 3 to DRM, then writes the status back to acknowledge. Suspend disables IRQ, suspends mode config, and disables the DCU clock; resume re-enables clock, restores TCON bypass and layer registers, re-enables IRQ, and resumes mode config.

## State And Persistence

Persistent driver state lives in `fsl_dcu_drm_device`: regmap, IRQ number, core and pixel clocks, TCON pointer, DRM object, CRTC/encoder/connector storage, and SoC capabilities. Hardware state includes interrupt masks/status, mode-setting registers, DCU layer descriptors, the divider register, and the LS1021A SCFG pixel-clock gate. Suspend drops the clock and relies on resume reinitialization and DRM mode restoration. `legacyfb_depth` is a module parameter and is normalized to 16/24/32 bpp during load.

## Dependencies And Integration Points

The file integrates Linux platform/OF, clk, regmap, syscon, PM sleep, DRM GEM DMA helpers, DRM fbdev DMA helpers, KMS helpers, vblank, `fsl_dcu_drm_modeset_init()`, plane reinitialization, and `fsl_tcon`. It also depends on SoC-specific register layout differences from `fsl_dcu_drm_drv.h`.

## Risks And Test Signals

Risks include IRQ-not-connected handling, regmap volatility mistakes for W1C/status registers, unbalanced clock or pixel-divider cleanup on probe failure, permanently enabled LS1021A PIXCLK power cost, and suspend/resume ordering around IRQ and mode restoration. Test signals are platform probe/remove, invalid `legacyfb_depth`, vblank interrupts, fbdev creation, suspend/resume with active modes, TCON-present and TCON-absent device trees, big-endian divider shift handling, and both LS1021A/VF610 layer-count variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.c -->
