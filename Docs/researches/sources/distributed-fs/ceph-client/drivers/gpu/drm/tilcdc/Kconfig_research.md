# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Kconfig

## Purpose

`tilcdc/Kconfig` exposes configuration options for the TI LCDC DRM driver and its legacy panel-binding compatibility layer.

## Important APIs, Types, and Functions

- `DRM_TILCDC` is a tristate option for TI LCDC display controllers. It depends on `DRM`, `OF`, and `ARM`, and selects DRM client, KMS, DMA GEM, bridge, display helper, bridge connector, panel bridge, videomode, and backlight support.
- `DRM_TILCDC_PANEL_LEGACY` is a bool compatibility option for legacy `ti,tilcdc,panel` DT blobs. It depends on `DRM_TILCDC`, OF, backlight, and PM, and selects OF overlay and `DRM_PANEL_SIMPLE`.

## Control Flow

Kernel configuration enables compilation of `tilcdc.o` through the Makefile. If the legacy option is enabled, an early initcall module applies a DT overlay and property migration before normal device probing.

## State and Persistence Behavior

Kconfig choices persist in the kernel build configuration. The legacy option defaults to enabled when dependencies are met, which affects boot-time DT mutation behavior.

## Dependencies and Integration Points

These options integrate with the DRM subsystem, OF graph/device-tree probing, panel/bridge helpers, DMA GEM memory management, and backlight/videomode helpers. `DRM_TILCDC_PANEL_LEGACY` also integrates with OF overlay infrastructure and the simple panel driver.

## Risks and Edge Cases

- `DRM_TILCDC` is restricted to ARM despite possible compile-test interest; portability requires config changes.
- The legacy option defaults on and mutates the live DT; systems with unexpected legacy-compatible nodes can be affected.
- Selecting helper subsystems pulls in broad DRM infrastructure, so dependency regressions surface at build time.

## Test Signals

Kconfig tests should cover built-in, module, and disabled combinations; legacy enabled/disabled builds; missing OF overlay dependencies; and boot tests with legacy and modern panel bindings.
