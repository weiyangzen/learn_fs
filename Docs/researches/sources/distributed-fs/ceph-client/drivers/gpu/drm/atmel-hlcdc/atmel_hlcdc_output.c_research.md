<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_output.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_output.c

## Purpose

`atmel_hlcdc_output.c` discovers downstream bridges/panels from device-tree graph endpoints and creates simple DRM encoders for HLCDC RGB output paths. It also records the endpoint bus format advertised by the `bus-width` property.

## Important APIs, Types, And Functions

- `struct atmel_hlcdc_rgb_output`: wraps a DRM encoder and cached media bus format.
- `atmel_hlcdc_encoder_get_bus_fmt(struct drm_encoder *encoder)`: returns the cached bus format for CRTC output-mode selection.
- `atmel_hlcdc_of_bus_fmt()`: maps endpoint `bus-width` values 12/16/18/24 to RGB444/RGB565/RGB666/RGB888 media bus formats; missing property returns 0.
- `atmel_hlcdc_attach_endpoint()`: finds a bridge for one endpoint, allocates an encoder, reads bus width, assigns possible CRTCs, and attaches the bridge.
- `atmel_hlcdc_create_outputs()`: scans endpoints, always trying the first four and then continuing while attachments keep succeeding.

## Control Flow

Output creation iterates endpoint indices. Each endpoint lookup obtains a bridge from OF graph, allocates a simple encoder, obtains the endpoint node to parse `bus-width`, validates the result, links the encoder to the controller CRTC, and attaches the downstream bridge. A missing endpoint is skipped for the first few indices; after at least one success, a trailing `-ENODEV` is treated as success.

## State And Persistence Behavior

The persistent state is the allocated encoder plus its `bus_fmt`. No hardware registers are written directly; later CRTC checks use this state to select controller output mode.

## Dependencies And Integration Points

It depends on OF graph, DRM bridge helpers, simple encoder allocation, and local CRTC/device state. It integrates with downstream panel/bridge drivers and with `atmel_hlcdc_crtc_select_output_mode()`.

## Risks And Edge Cases

The function assumes `devm_drm_of_get_bridge()` returning `-ENODEV` means absent endpoint, not fatal topology damage. Invalid `bus-width` aborts output creation. `DRM_MODE_ENCODER_NONE` is used for the local simple encoder because the downstream bridge determines the physical interface.

## Test Signals

Device-tree graph tests with one or multiple endpoints, missing endpoint gaps, invalid bus widths, RGB444/565/666/888 bus-format negotiation, and downstream bridge attach failures validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_output.c -->
