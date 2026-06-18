# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.c

## Purpose
Implements the OMAP3 ISP resizer V4L2 subdevice and its memory input/output video-node glue. The module scales interleaved YUV422 frames from either memory or the live video port, applies crop constraints, programs hardware filter coefficients, manages SBL bandwidth throttling, and integrates with media-controller links.

## Important APIs, Types, and Functions
Core public entry points are `omap3isp_resizer_init()`, `omap3isp_resizer_cleanup()`, entity register/unregister helpers, `omap3isp_resizer_isr()`, `omap3isp_resizer_isr_frame_sync()`, `omap3isp_resizer_busy()`, and `omap3isp_resizer_max_rate()`. Important internals include `resizer_calc_ratios()`, `resizer_try_crop()`, `resizer_set_format()`, `resizer_set_selection()`, `resizer_configure()`, `resizer_set_stream()`, and `resizer_video_queue()`.

## Control Flow
Initialization creates a two-pad scaler subdevice plus input and output video nodes. Media link setup selects memory input or video-port input, refusing conflicting links. Format and selection operations clamp sink/source sizes and compute TRM-valid ratios/crops. Stream start enables the resizer clock, programs source, input/output offsets, output size, crop, filters, phase, and luma settings, then starts one-shot processing when buffers are present. IRQ flow applies pending crop updates under `res->lock`, completes queued buffers through `omap3isp_video_buffer_next()`, loads the next DMA addresses, and restarts continuous or single-shot processing as appropriate.

## State and Persistence
Persistent runtime state lives in `struct isp_res_device`: active/requested crop, ratios, input selection, memory base address, crop offset, stream state, wait/stopping synchronization, and a spinlock-protected `applycrop` flag. Hardware state is volatile register programming under the resizer and SBL register blocks; nothing survives module unload or reboot.

## Dependencies and Integration Points
The code depends on `isp.h`, `ispreg.h`, media-controller pads/links, V4L2 subdev pad operations, OMAP3 ISP SBL/subclock helpers, revision-specific hardware limits, and generic `ispvideo` buffer handling. It feeds pipeline maximum-rate decisions through `omap3isp_resizer_max_rate()` during link validation.

## Risks and Edge Cases
The ratio equations are hardware-sensitive and depend on 4-tap versus 7-tap mode, default phase, output width alignment, vertical ratio, and OMAP ISP revision. Memory input crop programming splits byte offset between SDR address alignment and low horizontal start bits. Continuous mode underruns are deferred to frame-sync restart because immediate mid-frame enable causes shifted images. SBL throttling relies on valid `pipe->max_rate` and `max_timeperframe`; divide-by-zero or stale pipeline timing would be dangerous.

## Test Signals
Exercise media link combinations, memory-to-memory single-shot scaling, live sensor-to-memory scaling, crop changes while streaming, YUYV/UYVY ordering, ES1/ES2/3630 output-width limits, underrun recovery, SBL overflow absence under high scaling ratios, and v4l2-compliance for subdev format/selection enumeration.
