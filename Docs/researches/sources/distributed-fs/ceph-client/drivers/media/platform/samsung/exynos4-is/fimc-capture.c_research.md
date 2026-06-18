# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-capture.c

## Purpose
`fimc-capture.c` implements the FIMC camera capture video node and FIMC processing subdevice. It manages media graph links, pipeline format negotiation, capture vb2 queues, frame buffer scheduling, interrupt-time buffer completion, crop/compose selection, and suspend/resume cleanup for camera and ISP writeback capture.

## Important APIs, Types, and Functions
Hardware and stream lifecycle functions include `fimc_capture_hw_init()`, `fimc_capture_state_cleanup()`, `fimc_stop_capture()`, `fimc_capture_suspend()`, and `fimc_capture_resume()`. IRQ-time scheduling is in `fimc_capture_irq_handler()` and `fimc_capture_config_update()`. vb2 callbacks are `queue_setup()`, `buffer_prepare()`, `buffer_queue()`, `start_streaming()`, and `stop_streaming()`. User-facing ioctl helpers include format, input, stream, reqbufs, and selection handlers such as `__video_try_or_set_format()`, `fimc_cap_streamon()`, and `fimc_cap_s_selection()`. Media/subdev integration uses `fimc_link_setup()`, `fimc_pipeline_try_format()`, `fimc_pipeline_validate()`, `fimc_subdev_get_fmt()`, `fimc_subdev_set_fmt()`, `fimc_subdev_get_selection()`, `fimc_subdev_set_selection()`, `fimc_initialize_capture_subdev()`, and `fimc_unregister_capture_subdev()`.

## Control Flow
Probe initializes the capture subdev, and the subdev `registered()` callback creates both mem2mem and capture video nodes. Opening capture blocks concurrent m2m use, resumes runtime PM, opens the media pipeline for the first file handle, and applies default format. Format setting either drives the whole upstream pipeline or, in user-subdev API mode, trusts active subdev formats after validation. Stream-on starts the media pipeline, stores current source configuration, validates links when needed, and delegates to vb2. When enough buffers are queued, `buffer_queue()` or `start_streaming()` programs output addresses, activates capture, and starts upstream streaming. Each frame interrupt completes the oldest active buffer, moves a pending buffer into the hardware slot ring, optionally supplies embedded-data buffers to CSIS, applies deferred configuration changes, and stops capture when the last buffer drains.

## State and Persistence
Runtime state lives in `fimc->state`, `fimc->vid_cap`, and the capture `struct fimc_ctx`. `ST_CAPT_*` bits represent pending/running/streaming/suspended/shutdown/JPEG/config-apply states. `pending_buf_q`, `active_buf_q`, `active_buf_cnt`, `buf_index`, and `frame_count` track buffer ownership. Formats are stored in `ci_fmt`, `wb_fmt`, `s_frame`, and `d_frame`; source configuration is copied from sensor hostdata at stream-on. No persistent storage exists.

## Dependencies and Integration Points
The file depends on V4L2 video ioctl helpers, V4L2 subdev pad operations, media controller graph APIs, vb2 DMA-contig, runtime PM, FIMC register helpers, `media-dev.h` pipeline callbacks, common sensor discovery, and optional MIPI-CSIS `s_rx_buffer` support for embedded metadata. It integrates with the core IRQ handler via `fimc_capture_irq_handler()`.

## Risks and Edge Cases
Capture and mem2mem are mutually exclusive through state bits and the device mutex. JPEG/user-defined formats disable scaling/cropping and require sensor frame descriptors to size payloads. The buffer slot ring has `FIMC_MAX_OUT_BUFS` hardware slots while user-requested buffer count may differ. Suspend cleanup moves active buffers back to pending, whereas normal stop completes them with error. Several paths depend on graph locking discipline to avoid nested media locks. Pipeline validation must catch mismatched pad formats or undersized compressed buffers before streaming.

## Test Signals
Test direct camera, CSIS, FIMC-LITE, and FIMC-IS writeback pipelines; default format on first open; link setup and sensor control inheritance; TRY/S_FMT with and without user-subdev API; JPEG payload/frame descriptor handling; one-buffer and multi-buffer capture; metadata plane handoff to CSIS; crop/compose bounds and deferred config updates during streaming; streamoff cleanup; suspend/resume with queued buffers; and sensor end-of-frame notifications completing still capture.
