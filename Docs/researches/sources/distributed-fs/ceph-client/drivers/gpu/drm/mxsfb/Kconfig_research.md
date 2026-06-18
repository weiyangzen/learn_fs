# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Kconfig

## Purpose
This Kconfig file declares build-time configuration for the MXS/LCDIF DRM drivers. It separates a common internal selector, the classic i.MX `(e)LCDIF` controller driver, and the newer i.MX LCDIFv3 driver.

## Important APIs, Types, And Data
`config DRM_MXS` is a hidden boolean selected by the concrete drivers. `config DRM_MXSFB` is a tristate for i.MX23, i.MX28, i.MX6SX, i.MX7, and i.MX8M LCDIF/eLCDIF hardware and builds module `mxsfb`. `config DRM_IMX_LCDIF` is a tristate for LCDIFv3 hardware on i.MX8MP and i.MXRT-class SoCs and builds module `imx-lcdif`. Both depend on DRM, OF, COMMON_CLK, and relevant architecture/compile-test support, and both select DRM client setup, KMS helper, DMA GEM helper, panel, and panel bridge support.

## Control Flow, State, And Integration
The file controls Kbuild inclusion and dependency closure rather than runtime behavior. Enabling either driver brings in the required DRM helpers and panel bridge support needed by probe paths in `mxsfb_drv.c` and `lcdif_drv.c`.

## Risks And Test Signals
Dependency mistakes can cause link failures or missing runtime helpers. The broad `COMPILE_TEST` path should catch portability issues, while architecture dependencies prevent irrelevant prompts on most systems. Test signals are `oldconfig/menuconfig` visibility, allmodconfig/allyesconfig builds, module names matching help text, and successful probe on device trees using compatible strings handled by the C drivers.
