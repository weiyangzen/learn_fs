# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/Kconfig

## Purpose
Defines Kconfig options for the Amlogic Meson DRM display controller and optional Synopsys HDMI/DSI encoder support.

## Important APIs, types, and functions
- `DRM_MESON` is the base tristate for the display controller.
- `DRM_MESON_DW_HDMI` enables Meson-specific DesignWare HDMI support.
- `DRM_MESON_DW_MIPI_DSI` enables Meson-specific DesignWare MIPI DSI support.

## Control flow
Kconfig dependency resolution selects DRM helper libraries, DMA GEM helpers, bridge connector support, display connector helpers, videomode helpers, MMIO regmap, Meson canvas, and optional CEC core. HDMI/DSI child options depend on the base driver and default to `y` when `DRM_MESON` is enabled.

## State and persistence
No runtime state is stored. Build configuration persists in kernel config and determines which objects are compiled.

## Dependencies and integration points
The base driver depends on DRM, OF, ARM/ARM64 or compile-test, and ARCH_MESON or compile-test. HDMI selects `DRM_DW_HDMI` and implies I2S audio. DSI selects `DRM_DW_MIPI_DSI` and `GENERIC_PHY_MIPI_DPHY`.

## Risks
Because child options default to enabled with the base driver, build and probe coverage includes HDMI/DSI unless explicitly disabled. Missing selects would show as link failures in the Makefile object set or runtime missing helpers.

## Test signals
Signals include allmodconfig/allyesconfig builds, Meson-only builds with and without HDMI/DSI options, CEC notifier combinations, and module load behavior for `meson-drm`, `meson_dw_hdmi`, and `meson_dw_mipi_dsi`.
