# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Kconfig

## Purpose

`rz-du/Kconfig` defines build-time options for the RZ/G2L Display Unit DRM driver and its embedded MIPI DSI encoder.

## Important APIs, Types, and Functions

`DRM_RZG2L_DU` is the main tristate driver option. It depends on Renesas architecture or compile testing, DRM, OF, and `VIDEO_RENESAS_VSP1`, and selects DRM client, GEM DMA, KMS, display-helper, bridge-connector, and videomode helpers. `DRM_RZG2L_USE_MIPI_DSI` is a user-visible bool gated by DRM bridge/OF and the DU driver. `DRM_RZG2L_MIPI_DSI` is a derived tristate selecting `DRM_MIPI_DSI`.

## Control Flow

Kconfig controls whether `rzg2l-du-drm.o`, `rzg2l_du_vsp.o`, and `rzg2l_mipi_dsi.o` are built. The MIPI DSI implementation is enabled when the DU driver and DSI support option are enabled.

## State and Persistence Behavior

No runtime state exists. Build configuration determines available modules and stub behavior in headers.

## Dependencies and Integration Points

The options integrate with the DRM subsystem, VSP1 media driver, OF graph, MIPI DSI core, and the Makefile in the same directory.

## Risks and Edge Cases

The main DU depends on VSP1 because the driver is VSP-fed. Disabling MIPI DSI still permits DPAD-style output where supported by DT/SoC routing.

## Test Signals

Configuration tests should build DU as built-in and module, with MIPI DSI enabled and disabled, and under `COMPILE_TEST`.
