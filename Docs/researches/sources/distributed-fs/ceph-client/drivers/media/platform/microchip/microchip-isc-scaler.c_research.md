# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-scaler.c

## Purpose
`microchip-isc-scaler.c` exposes the ISC/XISC crop/scaler path as a V4L2 subdevice in the media graph. It models the PFE/scaler constraints between the upstream sensor and the capture video node.

## Important APIs, Types, and Functions
Pad operations are `isc_scaler_enum_mbus_code()`, `isc_scaler_set_fmt()`, `isc_scaler_get_fmt()`, and `isc_scaler_g_sel()`. State initialization is `isc_scaler_init_state()`. Exported lifecycle and graph helpers are `isc_scaler_init()` and `isc_scaler_link()`.

## Control Flow
`isc_mc_init()` calls `isc_scaler_init()` to create the scaler subdevice with sink and source pads. The scaler sink accepts any supported ISC input media-bus code and any frame size, while the source is clamped to the controller's maximum width/height. `isc_scaler_link()` creates immutable enabled links from sensor source to scaler sink and scaler source to ISC video sink after async subdevice binding completes.

## State and Persistence
Scaler state is stored in `isc->scaler_format[]` for sink/source pads and in media entity pad objects. Try formats and crop rectangles live in V4L2 subdevice state. No hardware state is programmed directly here; the actual crop/PFE limits are applied by the base streaming path.

## Dependencies and Integration Points
The file depends on V4L2 subdevice state, media entity APIs, `isc_find_format_by_code()`, and `struct isc_device`. It integrates the logical media graph with the base driver's link-validation and crop programming.

## Risks and Edge Cases
The source pad format is fixed from the sink but clamped to hardware limits, so applications that set a larger sink size must observe the source format before configuring capture. Selection support only reports crop bounds/current crop on the sink pad. Failed registration cleanup is owned by surrounding media-device teardown.

## Test Signals
Use `media-ctl` to verify immutable links, enumerate scaler bus codes, set sink formats above and below hardware maximums, inspect clamped source formats and crop bounds, and confirm capture dimensions match link validation.
