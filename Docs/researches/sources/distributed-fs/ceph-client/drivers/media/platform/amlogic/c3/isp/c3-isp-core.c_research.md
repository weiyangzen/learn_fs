
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-core.c

## Purpose

`c3-isp-core.c` implements the central V4L2 subdevice for the Amlogic C3 ISP pipeline. It models the ISP core as a media entity with video sink, parameter sink, statistics source, and three video source pads. Its responsibilities are format negotiation, frame-size programming, raw Bayer phase offset programming, stream propagation to the upstream source, and frame-sync event delivery.

## Important APIs, Types, And Functions

The local `struct c3_isp_core_format_info` table maps supported media-bus codes to valid pads, raw/YUV behavior, and Bayer phase offsets. `core_find_format_by_code()` and `core_find_format_by_index()` are the table lookup helpers behind pad enumeration and validation.

Hardware-facing helpers include `c3_isp_core_enable()`, `c3_isp_core_disable()`, `c3_isp_core_lswb_ofst()`, `c3_isp_core_3a_ofst()`, `c3_isp_core_dms_ofst()`, and `c3_isp_core_cfg_format()`. They program top-level path selection, frame-end/frame-reset IRQ masks, input/core frame sizes, hold size, AF/AE/AWB windows, and Bayer phase offsets for BLC/WB/lens/demosaic/3A blocks.

V4L2/media integration is exposed through `c3_isp_core_pad_ops`, `c3_isp_core_core_ops`, `c3_isp_core_internal_ops`, and `c3_isp_core_entity_ops`. Public entry points are `c3_isp_core_queue_sof()`, `c3_isp_core_register()`, and `c3_isp_core_unregister()`.

## Control Flow

Initialization creates a `V4L2_SUBDEV_FL_HAS_DEVNODE` and event-capable subdevice named `c3-isp-core`, assigns pad flags, initializes the media entity, finalizes subdev state, and registers it with the parent `v4l2_device`. Default state sets the sink to RAW10 RGGB at default size, the video sources to YUV10 at matching size, and metadata pads to `MEDIA_BUS_FMT_METADATA_FIXED`.

Format setting is pad-sensitive. The video sink accepts RAW10/RAW12 Bayer codes and clamps dimensions to ISP min/max. Source formats mirror sink dimensions and accept YUV10 or 16-bit raw Bayer output codes. Parameter and statistics pads retain fixed metadata format.

Streaming is coordinated with capture-path readiness. `c3_isp_core_enable_streams()` returns early until the number of enabled core source links matches `isp->pipe.start_count`. Once all consumers are ready, it resets `frm_sequence`, programs current format state, enables core input and interrupts, locates the unique upstream pad, and enables upstream stream 0. Disable only tears down the upstream stream and core hardware when `start_count` drops to one.

## State And Persistence

Persistent runtime state is in `struct c3_isp_core` and the parent `struct c3_isp_device`: `src_pad` stores the current upstream media pad, `frm_sequence` is incremented by the top-level IRQ handler, and subdev state stores per-pad formats. No file-backed persistence exists. Register state is volatile and rebuilt during stream enable.

## Dependencies And Integration Points

This file depends on V4L2 subdev active-state APIs, media-controller pad/link validation, V4L2 events, runtime PM through the broader device, and register helpers from `c3-isp-dev.c`. It integrates with parameter and statistics video nodes via metadata pads, with three resizers through video source pads, and with the upstream MIPI adapter/sensor through an immutable media link.

## Risks

`c3_isp_core_streams_ready()` compares `link->flags == MEDIA_LNK_FL_ENABLED`; links with additional flag bits would not be counted. Source-pad loops from `C3_ISP_CORE_PAD_SOURCE_VIDEO_0` to `C3_ISP_CORE_PAD_MAX` include the stats metadata pad, so the sink-format propagation writes width/height into all later pads before metadata pads are explicitly initialized only in `init_state`. The enable path calls `c3_isp_core_enable()` before resolving the upstream pad; an `-EPIPE` leaves the core enabled. Bayer phase offsets rely on the format table being complete and correct for every accepted sink code.

## Test Signals

Build with `CONFIG_VIDEO_C3_ISP` and run media-graph enumeration to verify six pads and expected default formats. Exercise `VIDIOC_SUBDEV_ENUM_MBUS_CODE`, `S_FMT`, `G_FMT`, and frame-sync event subscription. Streaming tests should start one, two, and three capture paths and verify the core only starts the upstream source after all enabled capture paths are ready, then stops when the last path stops. Hardware tests should confirm frame-end IRQs update stats/params/captures and frame-reset IRQs queue `V4L2_EVENT_FRAME_SYNC`.
