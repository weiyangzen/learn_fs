<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Kconfig

## Purpose

`analogix/Kconfig` defines Analogix DRM bridge options for ANX6345, ANX78XX, the shared Analogix DP core, and ANX7625.

## Important APIs, Types, And Symbols

- `DRM_ANALOGIX_ANX6345`: OF-based ANX6345 bridge, selecting Analogix DP helpers, DRM DP/display helpers, KMS helpers, and regmap I2C.
- `DRM_ANALOGIX_ANX78XX`: SlimPort/MyDP bridge with the shared Analogix DP and helper selections.
- `DRM_ANALOGIX_DP`: tristate shared DP core depending on DRM.
- `DRM_ANALOGIX_ANX7625`: MIPI/DPI-to-DP bridge depending on DRM, OF, Type-C, USB role switch, and selecting DP/HDCP/display helpers, DP AUX bus, and MIPI DSI.

## Control Flow

There is no runtime control flow. Kconfig symbols control which objects in `analogix/Makefile` are built and which helpers are selected.

## State And Persistence Behavior

The only state is kernel configuration.

## Dependencies And Integration Points

The symbols integrate Analogix bridge drivers with DRM DP helpers, regmap I2C, KMS, Type-C/USB-role infrastructure, HDCP helpers, and MIPI DSI depending on the chip.

## Risks And Edge Cases

The hidden shared `DRM_ANALOGIX_DP` core is selected by front-end drivers. Missing OF or Type-C dependencies should prevent invalid runtime configurations. Helper selection must stay aligned with source includes and Makefile targets.

## Test Signals

Kconfig build matrix, allmodconfig, and targeted module builds for each Analogix symbol validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Kconfig -->
