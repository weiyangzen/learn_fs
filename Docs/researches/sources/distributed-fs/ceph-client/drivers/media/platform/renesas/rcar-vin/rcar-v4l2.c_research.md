# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-v4l2.c

## Purpose
`rcar-v4l2.c` implements the VIN userspace-facing V4L2 video node: pixel format enumeration/alignment, selection/crop/compose ioctls, event subscription, file open/release PM handling, video registration, and forwarding notifications from subdevices to the active VIN node.

## Important APIs, Types, And Functions
The static `rvin_formats[]` table maps V4L2 fourcc formats to bytes per pixel. `rvin_format_from_pixel()` is shared with DMA setup and applies SoC/channel restrictions for XBGR32, NV12, and RAW10. Format helpers are `rvin_format_bytesperline()`, `rvin_format_sizeimage()`, and `rvin_format_align()`. IOCTL handlers include querycap, get/try/set format, enum format, get/set selection, and event subscription. File operations are `rvin_open()` and `rvin_release()`. Registration entry points are `rvin_v4l2_register()` and `rvin_v4l2_unregister()`.

## Control Flow
Video registration initializes a `video_device`, sets queue/fops/ioctls/caps, installs a default 800x600 YUYV format, aligns it, registers the node, and stores drvdata. Open resumes runtime PM, opens the V4L2 file handle, powers the media pipeline, and sets up controls. Release delegates streaming cleanup to vb2, drops pipeline PM, unlocks, and runtime-suspends.

Format ioctls force capture colorspace metadata, validate fourcc against VIN capabilities, align width and bytesperline to hardware needs, and reject set-format while vb2 is busy. Selection ioctls expose crop bounds from the remote subdev active format, compose bounds from the active output format, clamp crop/compose rectangles, align compose offsets to hardware buffer-address requirements, update `vin->crop`/`vin->compose`, and call `rvin_crop_scale_comp()` so running hardware can be updated.

## State And Persistence
The active `v4l2_pix_format`, crop rectangle, compose rectangle, and control state are stored in `struct rvin_dev`. These settings persist only while the device is bound. vb2 busy state prevents format changes while buffers are allocated/streaming. Events are queued in the V4L2 framework.

## Dependencies And Integration Points
The file depends on V4L2 ioctl helpers, V4L2 events, media-controller remote pad lookup, runtime PM, pipeline PM, and sibling DMA functions. It integrates with upstream subdevices for crop bounds and notifications and with userspace through `V4L2_CAP_VIDEO_CAPTURE`, streaming, read/write, and media-controller IO capabilities.

## Risks
Selection changes call hardware programming without explicitly checking `running`; this relies on the DMA helper and register accessibility under current PM/open assumptions. Format enumeration has special raw bus-code handling and a TODO for future RAW12. Compose alignment loops decrement top/left until address alignment works, so boundary conditions around zero and format bpp matter. `rvin_remote_rectangle()` depends on an enabled media link and remote `get_fmt`; missing graph setup returns errors to selection ioctls.

## Test Signals
Use `v4l2-ctl --list-formats-ext`, try/set/get format for each SoC capability set, verify bytesperline and sizeimage alignment, test busy `S_FMT`, crop/compose clamping and alignment, frame-sync/source-change event subscription, open/release PM balancing, subdevice event forwarding, and video node removal while graph unbinds.
