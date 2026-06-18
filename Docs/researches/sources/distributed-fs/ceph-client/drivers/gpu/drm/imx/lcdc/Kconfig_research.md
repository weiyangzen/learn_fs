# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Kconfig

## Purpose
Defines the Kconfig option for the simple DRM driver for older Freescale i.MX LCDC display controllers.

## Important APIs, types, and functions
- `DRM_IMX_LCDC` is a tristate option for i.MX1, i.MX21, i.MX25, and i.MX27 LCDC displays.
- It depends on DRM and `ARCH_MXC || COMPILE_TEST`.
- It selects DRM client selection, GEM DMA helper, KMS helper, display helper, and bridge connector support.

## Control flow
Kconfig selection controls whether `imx-lcdc.o` is built by the local Makefile. There is no runtime control flow in the file.

## State and persistence
No runtime state exists. The symbol persists in kernel configuration and controls built-in/module availability.

## Dependencies and integration points
Integrates the LCDC driver with the DRM helper stack and bridge connector infrastructure needed by `imx-lcdc.c`.

## Risks
The driver relies on bridge lookup and GEM DMA helpers, so missing selects would surface as build failures in modular or COMPILE_TEST configurations. The option is independent from `DRM_IMX` because LCDC is a distinct older controller path.

## Test signals
Build `DRM_IMX_LCDC=y/m` with `ARCH_MXC` and with `COMPILE_TEST`, and verify the symbol can be disabled independently of the IPUv3/DCSS i.MX DRM drivers.
