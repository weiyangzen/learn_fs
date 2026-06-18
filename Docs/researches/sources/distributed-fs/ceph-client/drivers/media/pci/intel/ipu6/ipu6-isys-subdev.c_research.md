# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.c

## Purpose
`ipu6-isys-subdev.c` provides common V4L2 subdevice helpers for IPU6 ISYS bridge entities, especially CSI-2 receiver subdevices. It centralizes media-bus code handling, Bayer-order conversion, format propagation, stream routing setup, and common subdevice initialization/cleanup.

## Important APIs, Types, And Functions
Public helpers include `ipu6_isys_mbus_code_to_bpp()`, `ipu6_isys_mbus_code_to_mipi()`, `ipu6_isys_is_bayer_format()`, `ipu6_isys_convert_bayer_order()`, `ipu6_isys_subdev_set_fmt()`, `ipu6_isys_subdev_enum_mbus_code()`, `ipu6_isys_get_src_stream_by_src_pad()`, `ipu6_isys_subdev_set_routing()`, `ipu6_isys_subdev_init()`, and `ipu6_isys_subdev_cleanup()`. The implementation uses `struct ipu6_isys_subdev` from the companion header and V4L2 active-state routing APIs.

## Control Flow
Media-bus conversion helpers map V4L2 media-bus codes to bit depth and MIPI CSI-2 data types. Unsupported codes warn and return conservative defaults. `ipu6_isys_subdev_set_fmt()` clamps width/height to ISYS limits, picks a supported bus code, stores the format, and for sink pads propagates the same format to the opposite routed source stream while resetting crop to the full frame. Source-pad set-format requests are effectively read-only for bridge subdevices with more than one pad.

Routing is initialized to a default active 1:1 route from sink pad 0 stream 0 to source pad 1 stream 0 with a 4096x3072 SGRBG10 format. `ipu6_isys_subdev_set_routing()` validates `V4L2_SUBDEV_ROUTING_ONLY_1_TO_1` and applies routing with the same default format.

## State And Persistence
State lives in V4L2 subdev active/try state and the in-memory `ipu6_isys_subdev`. Crops are reset when a sink format changes. `asd->source` is initialized to `-1` and later used by CSI-2 code as the firmware stream source.

## Dependencies And Integration Points
This file integrates with media entity pads, V4L2 subdev streams/routing, V4L2 controls, and MIPI CSI-2 data type definitions. CSI-2 subdevice code reuses it to expose bridge entities consistently to `ipu6-isys-video.c`.

## Risks And Test Signals
Defaulting unsupported media-bus codes to 8-bit or invalid MIPI type can hide caller mistakes after only a warning. Routing currently supports only simple 1:1 routes, so multi-stream graph changes must be validated carefully. Test signals include V4L2 subdev routing tests, format propagation on sink pads, Bayer order conversion under odd crop offsets, unsupported code handling, and media graph validation before stream-on.
