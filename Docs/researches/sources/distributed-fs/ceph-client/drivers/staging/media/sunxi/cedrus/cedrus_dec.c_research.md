# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.c

Purpose: mem2mem job dispatcher for Cedrus stateless decode jobs. It converts queued V4L2 buffers and request controls into a `struct cedrus_run`, delegates setup/trigger to the selected codec backend, and completes failed jobs.

Important APIs/functions: `cedrus_device_run(void *priv)` is registered as `v4l2_m2m_ops.device_run`. It fetches next source and destination buffers, applies request controls via `v4l2_ctrl_request_setup()`, fills codec-specific control pointers based on `ctx->src_fmt.pixelformat`, copies metadata from source to destination, configures output format registers through `cedrus_dst_format_set()`, calls `ctx->current_codec->setup()`, completes controls, schedules the watchdog on success, and calls `trigger()`.

Control flow: V4L2 mem2mem core invokes `cedrus_device_run()` when a source/destination pair is ready. On setup error, it logs and calls `v4l2_m2m_buf_done_and_job_finish(..., VB2_BUF_STATE_ERROR)`. On success, IRQ or watchdog later finishes the job.

State and persistence: transient `cedrus_run` only. It relies on controls stored in `ctx->hdl`, queued buffer state in mem2mem queues, and codec scratch state held in `ctx`/capture buffers.

Dependencies/integration: depends on `cedrus_find_control_data()`, `cedrus_get_num_of_controls()`, `cedrus_dst_format_set()`, V4L2 request controls, and codec backend ops selected by `cedrus_video.c`.

Risks: missing controls yield NULL pointers that codec setup code generally dereferences, so robust userspace/request validation matters. HEVC entry point count uses control element count rather than slice value alone and rejects mismatches in codec setup. Watchdog is scheduled only after setup succeeds.

Test signals: submit each supported pixelformat with complete and incomplete control sets, verify metadata propagation, ensure setup errors complete both buffers as error, and confirm watchdog/IRQ finish paths are reached after trigger.
