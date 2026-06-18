# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Kconfig

## Purpose
Defines Kconfig options for the Ingenic DRM display controller driver, optional Ingenic IPU plane support, and JZ4780 DesignWare HDMI wrapper.

## Important APIs, types, and functions
- `DRM_INGENIC` is the main tristate driver, depending on MIPS or COMPILE_TEST, DRM, CMA, OF, and COMMON_CLK.
- The main option selects DRM bridge, client, panel bridge, KMS/display helpers, bridge connector, GEM DMA helper, and regmap support.
- `DRM_INGENIC_IPU` is a bool suboption that exposes the Ingenic IPU as a second primary plane.
- `DRM_INGENIC_DW_HDMI` is a tristate JZ4780 DW-HDMI wrapper depending on `MACH_JZ4780` and selecting `DRM_DW_HDMI`.

## Control flow
Kconfig controls which objects the Makefile builds and whether `ingenic-drm-drv.c` compiles IPU component-master support. `DRM_INGENIC_IPU` is a bool nested under the main driver, so it modifies the main module rather than creating a separate module choice.

## State and persistence
No runtime state exists. Selected symbols persist in kernel configuration and drive module composition.

## Dependencies and integration points
Integrates the Ingenic display driver with DRM helpers, CMA-backed GEM DMA, OF graph bridge/panel discovery, regmap MMIO, common clocks, and optional DW-HDMI.

## Risks
The HDMI wrapper depends on `MACH_JZ4780`, so COMPILE_TEST coverage for HDMI may be narrower than for the main DRM driver. Optional IPU support affects build composition and runtime component binding, so configuration combinations must be tested.

## Test signals
Build `DRM_INGENIC` with and without `DRM_INGENIC_IPU`, and build `DRM_INGENIC_DW_HDMI` on JZ4780 configs. Confirm selected helper dependencies avoid unresolved symbols in modular builds.
