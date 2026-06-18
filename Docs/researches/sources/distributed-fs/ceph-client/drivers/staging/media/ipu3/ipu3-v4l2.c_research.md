# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-v4l2.c

## Purpose

This file exposes the IPU3 ImgU processing block as V4L2 media-controller entities: per-pipe subdevices, video nodes for input/output/viewfinder, metadata nodes for parameters and 3A statistics, controls, pad links, vb2 queues, and ioctl operations.

## Important APIs, Types, and Functions

Important entry points are `imgu_v4l2_register()`, `imgu_v4l2_unregister()`, and `imgu_v4l2_buffer_done()`. Subdevice operations include `imgu_subdev_open()`, `imgu_subdev_s_stream()`, format get/set, and selection get/set. Media links are handled by `imgu_link_setup()`. vb2 operations are `imgu_vb2_buf_init()`, `imgu_vb2_buf_cleanup()`, `imgu_vb2_buf_queue()`, `imgu_vb2_queue_setup()`, `imgu_vb2_start_streaming()`, and `imgu_vb2_stop_streaming()`. Format helpers include `find_format()`, `imgu_try_fmt()`, `imgu_fmt()`, and metadata format handlers. Registration helpers create subdevices and nodes for every pipe.

## Control Flow

Registration builds a media device, V4L2 device, one ImgU subdevice per CSS pipe, five video/meta nodes per pipe, pad links, subdev nodes, and then registers the media device. During setup, link enable toggles `node.enabled` and the input link toggles the corresponding CSS pipe bit. `STREAMON` starts an individual vb2 queue; only once all enabled nodes across enabled pipes are streaming does the file call each subdevice `s_stream(1)` and then `imgu_s_stream(true)`. `STREAMOFF` reverses that order once for the whole pipeline, then stops the individual node and returns queued buffers. `QBUF` maps or validates the buffer, links it to the node list, sets payload, and asks `imgu_queue_buffers()` to feed CSS if the device is already streaming.

## State and Persistence Behavior

Persistent state lives in `struct imgu_video_device`, `struct imgu_v4l2_subdev`, and `struct imgu_media_pipe`: enabled links, active subdevice state, running mode, formats, rectangles, vb2 queues, buffer lists, sequence counters, and media pipeline objects. Global streaming state is protected by `imgu->streaming_lock`; queue/list state is protected by `imgu->lock` and per-node queue locks.

## Dependencies and Integration Points

The file integrates V4L2 core, media controller, videobuf2 DMA-SG, IPU3 CSS format/metadata helpers, and IPU3 DMA mapping. It calls into `ipu3.c` through `imgu_s_stream()` and `imgu_queue_buffers()`, and into CSS helpers through `imgu_css_fmt_try()`, `imgu_css_fmt_set()`, and `imgu_css_meta_fmt_set()`.

## Risks and Edge Cases

Pipeline start depends on every enabled node streaming; a missing queue can leave stream setup staged but not started. Parameters are metadata output and are not DMA-mapped like image buffers. `imgu_fmt()` allocates temporary format copies during TRY format and must free all non-target queues. Stop streaming intentionally avoids multiple `s_stream(0)` calls because newer V4L2 call helpers warn on repeated calls. Enabled-link state and CSS enabled pipe bits must stay synchronized.

## Test Signals

Exercise media graph enumeration, link enable/disable, `VIDIOC_TRY_FMT`/`S_FMT` on raw input and NV12 outputs, metadata params/stat nodes, multi-pipe stream-on ordering, stream-off from different nodes, buffer queueing before and during streaming, and suspend/stop error paths that return queued buffers.
