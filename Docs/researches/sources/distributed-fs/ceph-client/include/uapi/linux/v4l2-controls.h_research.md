# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-controls.h

## Purpose
Defines the Video4Linux2 control ID namespace, enum values, and compound control payloads. It is the core userspace ABI for configuring video, camera, radio, codec, detection, colorimetry, and stateless codec devices through V4L2 controls.

## Important APIs, Types, And Constants
The file partitions control IDs by class: user, stateful codec, camera, FM TX/RX, flash, JPEG, image source, image processing, digital video, RF tuner, detection, stateless codec, and colorimetry. The user class covers classic image/audio controls such as brightness, contrast, saturation, hue, white balance, gain, flip, power-line frequency, color effects, rotation, alpha, and minimum buffer requirements. Private user bases reserve ranges for specific drivers including bttv, UVC, Rockchip ISP1, and Mali-C55.

Codec controls include MPEG stream/audio/video settings, H.263/H.264/MPEG4/VP8/VP9/HEVC/AV1 profile and level enums, bitrate/rate-control settings, GOP and slice settings, QP controls, and legacy hardware-specific CX2341X/MFC51 ranges. Camera controls include exposure mode, pan/tilt/zoom/focus/iris, 3A lock flags, autofocus status/range, orientation, sensor rotation, and HDR sensor mode. Other classes define RDS modulation/reception, flash modes/faults/intensity, JPEG markers, sensor blanking/gains/unit cell size, image processing link frequency/pixel rate/digital gain, DV TX/RX state, RF gain controls, motion detection grids, and HDR10 CLL/mastering display structs with explicit mastering range constants.

The dense stateless codec section exports compound structs for parser-provided decode metadata. H.264 structs include SPS, PPS, scaling matrices, prediction weights, references, slice params, DPB entries, and decode params. FWHT, VP8, MPEG-2, HEVC, VP9, and AV1 each provide parameter structs for sequence/frame headers, loop filters, segmentation, quantization, reference timestamps, tile info, global motion, restoration, film grain, and codec-specific flags. Many comments specify that reserved fields must be zeroed and that some controls are dynamic arrays.

## Control Flow, State, And Persistence
This header does not implement control handling; V4L2 core and drivers use the IDs and payload structs when userspace calls control ioctls. Stateful controls persist in driver/device control state until changed or reset. Stateless codec controls are per-request decode metadata attached to queued buffers; reference state is linked through V4L2 capture buffer timestamps. Dynamic-array controls, DPB arrays, and reference timestamps create the effective control flow for stateless decode: userspace parses bitstreams, fills controls, queues bitstream buffers, and hardware consumes metadata plus reference buffers.

## Dependencies And Integration Points
Depends on `<linux/const.h>` and `<linux/types.h>`, and is included by `videodev2.h`. It integrates with V4L2 control handler internals, media codecs, camera sensors, USB cameras, HDMI/DV receivers, radio devices, and userspace frameworks such as libcamera, GStreamer, FFmpeg, and V4L2 compliance tools.

## Risks And Test Signals
ABI risk is broad: numeric control IDs are stable, compound struct layout must not change, reserved fields must be zero, and userspace/kernel must agree on enum semantics. Stateless codecs are especially sensitive to malformed bitstream-derived values, stale reference timestamps, dynamic array length mismatches, and 32/64-bit layout assumptions. Test signals include `v4l2-compliance`, compile-time struct size checks, control enumeration/query tests, invalid enum/range rejection, per-codec conformance bitstreams, DPB/reference timestamp stress tests, and media framework interop.
