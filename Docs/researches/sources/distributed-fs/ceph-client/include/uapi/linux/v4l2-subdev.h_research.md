# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-subdev.h

## Purpose
Defines the userspace ioctl ABI for V4L2 sub-device nodes. Subdevs expose pad-level media-bus formats, crop/selection, frame intervals, capabilities, routing, stream-aware client capabilities, EDID/std/DV timing ioctls, and compatibility aliases.

## Important APIs, Types, And Constants
`enum v4l2_subdev_format_whence` selects try versus active configuration. Format, crop, media-bus-code enumeration, frame-size enumeration, frame interval, frame-interval enumeration, and selection structs all carry pad/index/code/dimensions plus stream fields and reserved arrays. Capability bits report read-only subdevs and stream/routing support. `struct v4l2_subdev_route` and `struct v4l2_subdev_routing` describe sink-to-source pad/stream routes; `V4L2_SUBDEV_ROUTE_FL_ACTIVE` marks active routes. Client capability bits opt userspace into stream fields and interval `which` semantics. The `VIDIOC_SUBDEV_*` ioctl macros define querycap, get/set format, intervals, crop, selection, routing, client caps, EDID, standards, and DV timing operations.

## Control Flow, State, And Persistence
Applications enumerate formats and frame sizes, negotiate try formats, commit active formats/selections, configure routing, and then video-node streaming uses those active routes. The kernel may force stream fields to zero unless the client advertises stream awareness. Persistent runtime state is per-subdev active configuration and route tables; try state is negotiation-scoped.

## Dependencies And Integration Points
Depends on `<linux/const.h>`, `<linux/ioctl.h>`, `<linux/types.h>`, `v4l2-common.h`, and `v4l2-mediabus.h`. It integrates with the media controller API, camera sensors, bridges, multiplexed streams, V4L2 video nodes, EDID/DV timing helpers, and userspace managers such as libcamera.

## Risks And Test Signals
Risks include unzeroed reserved fields, client capability mismatches that silently collapse streams to zero, route array length/`num_routes` truncation, obsolete crop API use, and inconsistent active configuration across linked pads. Tests should run `v4l2-compliance`, enumerate and set try/active formats, route multi-stream topologies, verify read-only capability behavior, and exercise EDID/DV timing passthrough.
