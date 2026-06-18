# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-capture.c

## Purpose

`imx-media-capture.c` builds the V4L2 video capture node used by i.MX media subdevices. It adapts a source subdevice pad into a `/dev/video*` receiver, owns the videobuf2 DMA-contiguous queue, exposes both media-controller-centric and legacy pre-MC ioctls, and starts or stops the upstream media pipeline on stream-on/off.

## Important APIs, Types, and Functions

`struct capture_priv` is the private object behind `struct imx_media_video_dev`; it stores the owning media device, source subdevice/pad, vb2 queue, ready buffer list, queue spinlock, mutex, optional inherited control handler, and legacy API flag. Public entry points are `imx_media_capture_device_init()`, `imx_media_capture_device_register()`, `imx_media_capture_device_unregister()`, `imx_media_capture_device_remove()`, `imx_media_capture_device_next_buf()`, and `imx_media_capture_device_error()`.

Format helpers include `capture_find_format()`, `__capture_try_fmt()`, and `__capture_legacy_try_fmt()`. Queue callbacks are `capture_queue_setup()`, `capture_buf_init()`, `capture_buf_prepare()`, `capture_buf_queue()`, `capture_start_streaming()`, and `capture_stop_streaming()`. The file exposes two ioctl tables: `capture_ioctl_ops` for MC users and `capture_legacy_ioctl_ops` for legacy direct sensor-style queries.

## Control Flow

Initialization allocates `capture_priv`, a video device, a single sink media pad, and a DMA-contiguous vb2 queue with MMAP and DMABUF support. Registration initializes the default format, registers the video device, creates the source-subdev-to-video-node pad link, and adds the video device to the media device master list.

For streaming, users queue buffers into `ready_q`. `capture_start_streaming()` validates the selected video format against the active source pad format and calls `imx_media_pipeline_set_stream()` on the source entity. Hardware-owning subdevices later fetch buffers through `imx_media_capture_device_next_buf()`. On stop, the pipeline is stopped and all remaining queued buffers are returned with `VB2_BUF_STATE_ERROR`.

## State and Persistence Behavior

There is no disk persistence. Runtime state is in the video-device format, compose rectangle, selected pixel-format descriptor, queued buffers, and inherited controls. `ready_q` is protected by `q_lock`; device operations use `mutex`. The vb2 owner is cleared at release. Format changes are blocked while the queue is busy.

## Dependencies and Integration Points

The file integrates with V4L2 video-device ioctls, media controller links, V4L2 events, vb2 DMA-contiguous memory, and upstream i.MX subdevices. CSI uses this capture node at its IDMAC source pad. The legacy API delegates frame size, interval, standard, and time-per-frame operations upstream to the source subdevice.

## Risks and Edge Cases

`capture_validate_fmt()` checks size and color-space class but not every bus-code detail, so bad upstream negotiations can still fail later in hardware. The memory cap divides by `pix->sizeimage`; callers depend on format initialization to avoid zero size. On pipeline start failure, buffers are returned as queued rather than error, which is consistent with vb2 start failure but important for user-space retry behavior. Legacy format enumeration depends on the active upstream format and may return only one format for raw/bayer passthrough.

## Test Signals

Exercise MC and legacy ioctls, busy-queue format rejection, format validation mismatch returning `-EPIPE`, buffer memory cap behavior, stream start failure cleanup, stream stop buffer return, event subscription for frame-interval errors, inherited controls in legacy mode, and DMABUF/MMAP queueing through a CSI IDMAC capture pipeline.
