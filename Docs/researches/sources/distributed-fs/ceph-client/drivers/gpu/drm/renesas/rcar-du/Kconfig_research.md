# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Kconfig

## Purpose

`rcar-du/Kconfig` defines build-time options for the Renesas R-Car Display Unit DRM driver and its companion CMM, HDMI, LVDS, MIPI DSI, VSP compositor, and writeback support.

## Important APIs, Types, and Functions

- `DRM_RCAR_DU` is the main tristate driver option and selects KMS, display helper, bridge connector, GEM DMA helper, and videomode helpers.
- `DRM_RCAR_USE_CMM` and `DRM_RCAR_CMM` control Color Management Module support.
- `DRM_RCAR_DW_HDMI` enables the internal DesignWare HDMI encoder glue.
- `DRM_RCAR_USE_LVDS` and `DRM_RCAR_LVDS` control embedded LVDS encoder support.
- `DRM_RCAR_USE_MIPI_DSI` and `DRM_RCAR_MIPI_DSI` control embedded MIPI DSI encoder support.
- `DRM_RCAR_VSP` enables VSP1 compositor-backed KMS planes and has dependency logic to keep VSP1 and DU linkage buildable.
- `DRM_RCAR_WRITEBACK` defaults to yes on ARM64 and depends on the main DU driver.

## Control Flow

Kconfig dependencies restrict visibility and selection by architecture, OF, DRM core, bridge, PM, reset, VSP1, and module/built-in compatibility. The main driver can be built as module or built-in; dependent companions follow tristate or bool defaults.

## State and Persistence Behavior

No runtime state. Selected symbols determine compiled object files and conditional code paths, including stub versus real CMM functions and VSP/writeback objects.

## Dependencies and Integration Points

Connects R-Car DU to DRM core helpers, bridge/panel/MIPI/DesignWare HDMI libraries, reset controller, PM, and media VSP1 driver configuration.

## Risks and Edge Cases

- VSP dependency must prevent an illegal built-in DU from depending on modular VSP1.
- Default-enabling companion support can expose probe deferrals when firmware/DT nodes reference bridges or CMM devices not yet available.
- Disabling `DRM_RCAR_USE_CMM` compiles CMM stubs, so color-management paths must behave correctly without hardware support.

## Test Signals

- Matrix builds should cover DU disabled, DU module, DU built-in, CMM disabled, LVDS/DSI/HDMI enabled, VSP module compatibility, ARM, ARM64, and COMPILE_TEST.
