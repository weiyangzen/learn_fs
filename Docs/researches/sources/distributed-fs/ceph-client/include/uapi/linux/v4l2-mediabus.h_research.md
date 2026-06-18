# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-mediabus.h

## Purpose
Defines the media-bus frame format structure used between V4L2 sub-devices and preserves deprecated media-bus pixel-code aliases for userspace compatibility.

## Important APIs, Types, And Constants
`V4L2_MBUS_FRAMEFMT_SET_CSC` marks colorspace conversion intent. `struct v4l2_mbus_framefmt` carries width, height, media-bus format code, field order, colorspace, either YCbCr or HSV encoding, quantization, transfer function, flags, and reserved words. For non-kernel users, frozen `enum v4l2_mbus_pixelcode` values are generated from `MEDIA_BUS_FMT_*` constants through `V4L2_MBUS_FROM_MEDIA_BUS_FMT`, covering fixed, RGB, YUV, Bayer, JPEG, and AHSV formats.

## Control Flow, State, And Persistence
No code runs here. Media pipeline negotiation passes this struct through subdev format ioctls; active format state is held per subdev pad/stream by drivers, while try formats are temporary negotiation state.

## Dependencies And Integration Points
Depends on `linux/media-bus-format.h`, `linux/types.h`, and `linux/videodev2.h`. It is consumed by `v4l2-subdev.h`, camera sensor/bridge drivers, ISP pipelines, and userspace graph managers.

## Risks And Test Signals
Risks include mixing deprecated `V4L2_MBUS_FMT_*` aliases with canonical `MEDIA_BUS_FMT_*`, failing to zero reserved fields, and inconsistent colorspace metadata across pipeline entities. Tests should enumerate supported bus codes, set/get pad formats, validate colorspace conversion flags, and compile old userspace using the deprecated enum names.
