
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d.c

## Purpose

`ge2d.c` implements a V4L2 mem2mem driver for the Amlogic Meson GE2D 2D graphics accelerator. The implemented path copies/transforms RGB buffers with crop/compose rectangles, rotation, horizontal/vertical flip, and alpha handling. The file explicitly notes missing features such as scaling, simple half vertical scaling, YUV input, source global alpha, and colorspace conversion.

## Important APIs, Types, And Functions

`struct ge2d_fmt` maps V4L2 fourcc formats to alpha presence, depth, hardware format, and hardware color map. `struct ge2d_frame` stores the current VB2 buffer, pixel format, crop rectangle, and format descriptor. `struct ge2d_ctx` is per-filehandle state including V4L2 FH, mem2mem context, input/output frames, controls, sequence counters, and transform flags. `struct meson_ge2d` is the device object with V4L2 device, mem2mem device, video node, regmap, clock, mutex, and current running context.

Core execution functions are `ge2d_hw_start()`, `device_run()`, and `ge2d_isr()`. VB2/mem2mem operations include `queue_init()`, `ge2d_queue_setup()`, `ge2d_buf_prepare()`, `ge2d_buf_queue()`, stream start/stop, and `ge2d_m2m_ops`. V4L2 ioctl handlers cover querycap, format enumeration/get/try/set for output and capture, crop/compose selection, buffer ioctls, stream ioctls, and control events. Controls are handled by `ge2d_s_ctrl()` for HFLIP, VFLIP, and ROTATE.

## Control Flow

Probe maps MMIO, initializes regmap, requests IRQ, gets reset and clock, resets hardware, enables the clock, registers the V4L2 device, allocates a video node, initializes the V4L2 mem2mem device, and registers `/dev/video*`.

Open allocates a context, initializes default 128x128 XRGB-like frames, creates mem2mem queues, initializes V4L2 FH, adds controls, and attaches the control handler. Userspace configures output/capture formats and crop/compose rectangles, queues one source and one destination buffer, and starts streaming. `device_run()` selects the next source/destination buffers and calls `ge2d_hw_start()`.

`ge2d_hw_start()` resets GE2D, writes DMA base/stride for source1, source2, and destination, programs control registers, format maps, clipping and full-image extents, constructs an ALU copy operation with alpha behavior based on input/output alpha support, and writes `GE2D_CMD_CTRL` with flip/rotation bits plus command start. The IRQ handler polls `GE2D_STATUS0`; when the busy bit is clear, it removes source/destination buffers, updates sequence numbers, copies timestamp/timecode/flags, marks both done, and finishes the mem2mem job.

## State And Persistence

Per-open state persists in `struct ge2d_ctx` until release. Device state persists in `struct meson_ge2d`; `curr` tracks the in-flight context. Queue state is held by V4L2 mem2mem/VB2. Hardware register state is transient per job. There is no file-backed persistence.

## Dependencies And Integration Points

The driver depends on platform compatible `amlogic,axg-ge2d`, a single MMIO resource, IRQ, reset control, clock, regmap MMIO, V4L2 mem2mem, VB2 DMA-contig, and the local register header. It exposes a V4L2 M2M video node with `V4L2_CAP_VIDEO_M2M | V4L2_CAP_STREAMING`.

## Risks

`ge2d_isr()` treats `!(GE2D_GE2D_BUSY)` as completion, which depends on interrupt behavior and status semantics; spurious IRQs while `ge2d->curr` is NULL would dereference NULL. Format handling supports RGB layouts only despite GE2D color-map definitions for YUV. Rotation changes capture dimensions and refuses changes only when the capture queue is busy; output queue interactions should also be considered. The log message `"queue (%d) bust"` appears to be a typo. There is no explicit runtime PM; the clock is enabled for the driver's lifetime. Hardware scaling registers are defined but not used, so crop/compose must not be interpreted as arbitrary scaling support.

## Test Signals

Run V4L2 mem2mem compliance for format enumeration, try/set behavior, busy-queue rejection, crop/compose validation, and controls. Queue RGB buffers for copy, HFLIP, VFLIP, and rotations 90/180/270 and compare output pixels. IRQ tests should cover normal completion, streamoff with queued buffers, and spurious/early interrupts. Probe/remove tests should validate reset, clock enable/disable, IRQ registration, and clean release of video and mem2mem devices.
