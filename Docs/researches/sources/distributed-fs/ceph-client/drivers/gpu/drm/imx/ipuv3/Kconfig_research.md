# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Kconfig

## Purpose
Defines Kconfig options for the legacy Freescale/NXP i.MX IPUv3 DRM stack and its output encoders: parallel display, TV/VGA encoder, LVDS display bridge, and i.MX6 HDMI.

## Important APIs, types, and functions
- `DRM_IMX` enables the core IPUv3 DRM driver, depends on DRM, `ARCH_MXC || COMPILE_TEST`, and `IMX_IPUV3_CORE`, and selects DRM client/KMS/GEM DMA/videomode helpers.
- `DRM_IMX_PARALLEL_DISPLAY` enables the parallel DPI output driver and selects bridge, bridge connector, display helper, panel bridge, legacy bridge, and videomode helpers.
- `DRM_IMX_TVE` enables the i.MX53 TV/VGA encoder and selects `REGMAP_MMIO`.
- `DRM_IMX_LDB` enables the i.MX53/i.MX6 LVDS bridge and selects syscon, DRM bridge helpers, panel bridge, and legacy bridge.
- `DRM_IMX_HDMI` enables the i.MX6 DesignWare HDMI wrapper and selects `DRM_DW_HDMI`.

## Control flow
Kconfig dependency resolution determines which objects in the adjacent Makefile are built. Output drivers depend on `DRM_IMX`, so they are available only when the component-based IPUv3 DRM core is enabled.

## State and persistence
No runtime state exists. The selected symbols persist in the kernel configuration and control module/built-in composition.

## Dependencies and integration points
Integrates the IPUv3 DRM code with the kernel's DRM, bridge, panel, regmap, syscon, common-clock, and IPUv3 core subsystems. It controls whether downstream component drivers can bind into the `imx-display-subsystem` master.

## Risks
Missing selects can produce build failures only for certain configurations, especially COMPILE_TEST. `DRM_IMX_HDMI` depends on `OF` and `DRM_IMX`, while the other output drivers bring in bridge helpers explicitly. Any dependency change must preserve module ordering and component-probe expectations.

## Test signals
Signals are configuration coverage: `allyesconfig`/`allmodconfig` build, `COMPILE_TEST` build on non-MXC architectures, modular load of `imxdrm` and optional encoders, and correct absence when `DRM_IMX` or `IMX_IPUV3_CORE` is disabled.
