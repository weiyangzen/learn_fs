# sources/distributed-fs/ceph-client/include/video/imx-ipu-image-convert.h

## Purpose
`imx-ipu-image-convert.h` exposes the asynchronous image-conversion API for the i.MX IPU v3 image converter. It supports format adjustment/verification, prepared streaming contexts, queued conversion runs, abort, and one-shot conversion.

## Important APIs, Types, and Functions
`struct ipu_image_convert_ctx` is opaque. `struct ipu_image_convert_run` contains the context, input/output DMA addresses, completion status, and a private list node. `ipu_image_convert_cb_t` is the completion callback. APIs are `ipu_image_convert_adjust()`, `ipu_image_convert_verify()`, `ipu_image_convert_prepare()`, `ipu_image_convert_unprepare()`, `ipu_image_convert_queue()`, `ipu_image_convert_abort()`, and `ipu_image_convert()`.

## Control Flow
V4L2 drivers typically call `ipu_image_convert_adjust()` during try-format, `ipu_image_convert_verify()` before committing a format, `ipu_image_convert_prepare()` at stream-on, allocate and queue dynamic run objects while streaming, receive completed run objects through the callback, and call unprepare or abort at stream-off. The one-shot helper prepares and queues an initial run automatically while returning the context through `run->ctx`.

## State and Persistence Behavior
Conversion state is held in the opaque context and per-run objects. Active and pending runs are transient DMA operations; `unprepare()` and `abort()` complete outstanding runs with error status. No state persists beyond the conversion context or across reboot.

## Dependencies and Integration Points
The header depends on `video/imx-ipu-v3.h`, DMA address types, and Linux list infrastructure. It integrates V4L2 mem2mem/capture pipelines with IPU IC tasks, rotation modes, tiled conversion constraints, and DMA-backed image buffers.

## Risks and Test Signals
Risks include stack-allocated run objects despite the API requiring dynamic allocation, unverified formats reaching `prepare()`, callback lifetime races during abort/unprepare, DMA address mismatches, and leaked contexts after one-shot conversion. Test signals include try-format clamping, invalid-format rejection, repeated queue/complete cycles, abort while active and pending, stream-off cleanup, rotation/tile cases, and callback error-status handling.
