# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.c

## Purpose
Provides shared V4L2 subdevice helpers for IPU7 ISYS bridge entities: media-bus-code to MIPI data-type conversion, bayer format detection and order conversion, format propagation, route setup, active-state format lookup, and generic subdevice initialization/cleanup.

## Important APIs, Types, and Functions
Exports `ipu7_isys_mbus_code_to_mipi()`, `ipu7_isys_is_bayer_format()`, `ipu7_isys_convert_bayer_order()`, `ipu7_isys_subdev_set_fmt()`, `ipu7_isys_subdev_enum_mbus_code()`, `ipu7_isys_get_stream_pad_fmt()`, `ipu7_isys_subdev_set_routing()`, `ipu7_isys_subdev_init()`, and `ipu7_isys_subdev_cleanup()`. Internal `subdev_set_routing()` validates routing with one-to-one and no-source-multiplexing flags, normalizes source streams to zero, and installs a default 4096x3072 SGRBG10 format.

## Control Flow
Format setting clamps dimensions to ISYS bounds, selects the requested supported media-bus code or falls back to the first supported code, writes sink format state, propagates to the opposite source stream, and resets crop to the propagated frame. Source-pad `set_fmt` returns current format because the bridge does not transcode. Initialization allocates pads, marks sink pads as mandatory connections and source pads as outputs, initializes media entity pads, optionally initializes controls, and installs default subdev flags for devnode/events/streams.

## State and Persistence Behavior
Subdevice state is managed through V4L2 active state and media entity pad arrays allocated with devm. `asd->source` is initialized to -1 and later set by concrete subdevices such as CSI2. Crop reset happens whenever sink format changes; routing state persists in V4L2 subdev state.

## Dependencies and Integration Points
Depends on media-controller and V4L2 subdev streams APIs, MIPI CSI2 media-bus definitions, and ISYS min/max geometry constants. CSI2 subdevices reuse the pad ops for format, enum, and routing; video setup uses `ipu7_isys_get_stream_pad_fmt()` for link validation and firmware pin configuration.

## Risks and Test Signals
Risks include WARNs for unsupported bus codes, bayer order conversion only covering 8/10/12-bit bayer codes, crop pointers not checked before reset, and forced `source_stream = 0` simplifying routing in ways that may reject future multiplexed use cases. Test with invalid routes, multiple sink streams, format propagation across active routes, bayer crop parity, and all supported/non-supported media-bus codes.
