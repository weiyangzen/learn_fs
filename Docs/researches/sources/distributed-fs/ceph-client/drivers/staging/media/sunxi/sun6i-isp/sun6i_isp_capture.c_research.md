# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.c

Purpose: capture video node implementation for the sun6i ISP. It exposes NV12/NV21 capture formats, configures main-channel output registers in the ISP load table, manages capture buffer state across hardware parameter-load cycles, implements vb2 queue operations, and creates the immutable media link from proc output to capture.

Important APIs/functions: `sun6i_isp_capture_dimensions()` and `sun6i_isp_capture_format()` expose active capture format. `sun6i_isp_capture_format_find()` maps V4L2 pixfmt to hardware output format. `sun6i_isp_capture_buffer_configure()` writes Y/U/V DMA addresses for a queued buffer into load registers. `sun6i_isp_capture_configure()` writes size, output format, and stride registers. State helpers move queued buffers to `pending`, then `current`, then `complete`, timestamping and completing buffers when PARAM_LOAD indicates the pending state became active. `sun6i_isp_capture_finish()` increments sequence on frame finish. Queue ops validate size, set payload, enqueue buffers, start/stop pipeline streaming, and cleanup queued/current buffers. Ioctl ops implement capture format and single camera input handling.

Control flow: userspace opens the video node, sets capture format, queues buffers, and streamon starts the media pipeline through the proc subdev. Queued buffers trigger `sun6i_isp_state_update()` if streaming. On PARAM_LOAD, pending becomes current and prior current is completed; on FINISH sequence increments. Stop streaming turns off proc stream, stops pipeline, and completes all outstanding buffers as error.

State and persistence: `sun6i_isp_capture_state` holds queue, pending/current/complete buffer pointers, sequence, and streaming flag. Format persists in `capture.format`; load-table output address/format registers persist until next state update.

Dependencies/integration: uses V4L2 video device/ioctls/events/media controller, vb2 DMA-contig, proc subdev streaming, proc dimensions for link validation, and core state/update helpers.

Risks: buffer cleanup iterates queued list with `list_for_each_entry()` while completing buffers and then reinitializes the list; this relies on completion not modifying the same list entries unexpectedly. Width alignment comment says stride aligns to 4 but implementation aligns pixel width to 2 before multiplying by bytes-per-pixel. No scaling/cropping is supported; capture dimensions must equal proc dimensions. Capture start sets `state->streaming = true` before source stream succeeds and unwinds on error.

Test signals: NV12/NV21 format negotiation and sizeimage, link validation dimension mismatch, buffer state ordering over FINISH/PARA_LOAD interrupts, streamon source failure unwind, qbuf while streaming causing immediate state update, stop streaming with pending/current/queued buffers, and V4L2 compliance for capture ioctls.
