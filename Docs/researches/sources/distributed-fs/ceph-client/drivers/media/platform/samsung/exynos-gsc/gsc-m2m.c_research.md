# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-m2m.c

## Purpose
`gsc-m2m.c` implements the V4L2 memory-to-memory video node for the Exynos5 G-Scaler. It accepts source and destination multi-planar buffers, validates formats/selections, prepares DMA addresses, schedules one hardware conversion job through the V4L2 mem2mem framework, and completes both queues on the frame-done interrupt path.

## Important APIs, Types, and Functions
The public entry points are `gsc_register_m2m_device()`, `gsc_unregister_m2m_device()`, and `gsc_m2m_job_finish()`. Core scheduling is handled by `gsc_m2m_device_run()`, `gsc_m2m_job_abort()`, `gsc_m2m_ctx_stop_req()`, and `gsc_get_bufs()`. The vb2 queue operations are `gsc_m2m_queue_setup()`, `gsc_m2m_buf_prepare()`, `gsc_m2m_buf_queue()`, `gsc_m2m_start_streaming()`, and `gsc_m2m_stop_streaming()`. The ioctl table covers format enumeration/get/try/set, REQBUFS/EXPBUF/QBUF/DQBUF, stream on/off, and crop/compose selection through `gsc_m2m_g_selection()` and `gsc_m2m_s_selection()`.

## Control Flow
Open allocates a per-file `struct gsc_ctx`, creates controls, initializes source/destination defaults, and creates a V4L2 m2m context with output and capture vb2 queues. Streaming resumes runtime PM, buffers are queued into the m2m context, and `gsc_m2m_device_run()` becomes the hardware launch point. It marks `ST_M2M_PEND`, detects context changes, handles stop requests, prepares DMA addresses for the next source and destination buffers, writes input/output base addresses, programs all G-Scaler registers when `GSC_PARAMS` is set, triggers shadow-register update, and enables the hardware. The IRQ-side caller invokes `gsc_m2m_job_finish()`, which removes one source and one destination buffer, copies timestamp metadata, marks both vb2 buffers done, and notifies `v4l2_m2m_job_finish()`.

## State and Persistence
State is volatile per device and per context. `gsc->m2m.ctx`, `gsc->m2m.refcnt`, `gsc->state`, and `ctx->state` coordinate open users, pending jobs, parameter reprogramming, stop requests, and aborts. Runtime PM references are held while each queue streams. No persistent storage exists; all hardware state is rederived from current `gsc_ctx`, `gsc_frame`, controls, and queued buffers.

## Dependencies and Integration Points
The file depends on V4L2 mem2mem, vb2 DMA-contig memory, V4L2 ioctl helpers, runtime PM, and GSC core/register helpers such as `gsc_prepare_addr()`, `gsc_set_scaler_info()`, `gsc_try_fmt_mplane()`, `gsc_try_selection()`, and `gsc_hw_*()`. It integrates with the platform probe path through `gsc_register_m2m_device()` and with the interrupt handler through `gsc_m2m_job_finish()`.

## Risks and Edge Cases
Stop handling depends on a frame interrupt clearing `GSC_CTX_STOP_REQ`; a missing interrupt falls back to timeout and error-completion. `gsc_m2m_device_run()` logs address/scaler errors but does not complete buffers on those paths directly, so callers rely on scheduler/abort cleanup. Selection handling maps compose targets to the source frame and crop targets to the destination frame, which is easy to misread. REQBUFS rejects counts larger than hardware input/output buffer limits. Context switching forces full reprogramming by setting `GSC_PARAMS`.

## Test Signals
Useful validation includes open/close reference counts, runtime PM get/put balance, m2m format set rejection while queues stream, min/max buffer count limits, crop/compose `LE` and `GE` selection constraints, scaler ratio rejection, timestamp propagation from source to destination, abort during active job, and frame-done completion for RGB, YUV planar, tiled, rotated, and alpha formats.
