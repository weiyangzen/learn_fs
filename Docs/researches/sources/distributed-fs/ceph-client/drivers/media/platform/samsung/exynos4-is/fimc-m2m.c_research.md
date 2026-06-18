# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-m2m.c

## Purpose
Implements the V4L2 memory-to-memory interface for the Samsung FIMC video postprocessor, covering format conversion, scaling, crop/compose, rotation, and DMA-to-DMA jobs.

## Important APIs, Types, and Functions
Exports `fimc_register_m2m_device()`, `fimc_unregister_m2m_device()`, and `fimc_m2m_job_finish()`. Important internals are `fimc_device_run()`, `fimc_m2m_shutdown()`, vb2 queue callbacks, format/selection ioctls, `queue_init()`, `fimc_m2m_open()`, and `fimc_m2m_release()`.

## Control Flow
Open allocates a per-file `fimc_ctx`, creates controls, initializes a v4l2-m2m context with source and destination vb2 queues, marks M2M running, and installs default RGB32 formats. Streaming resumes runtime PM. The scheduler calls `fimc_device_run()`, which prepares DMA offsets and addresses, copies timestamps, reprograms FIMC hardware when parameters changed or context switched, and activates input DMA/capture. Stop streaming waits for pending hardware shutdown, completes queued buffers with error, and drops runtime PM.

## State and Persistence
Per-file state lives in `struct fimc_ctx`: source/destination frames, controls, paths, scaler, rotation/effects, and parameter-dirty bits. Device-level `fimc->m2m` tracks the current hardware context, v4l2-m2m device, video node, and reference count. All state is volatile.

## Dependencies and Integration Points
Depends on FIMC core helpers, register helpers in `fimc-reg.c`, vb2 DMA-contig, V4L2 mem2mem framework, runtime PM, and common format/scaler validation code.

## Risks and Edge Cases
`fimc_buf_prepare()` sets payloads without checking actual plane sizes, relying on vb2/core allocation correctness. `fimc_device_run()` exits after DMA address or scaler errors without explicitly finishing the job, so error handling depends on later abort/stop paths. Selection type checks use single-planar buffer types while the queues are multi-planar, reflecting the driver's inverted-crop compatibility quirk and needing regression coverage.

## Test Signals
Exercise source/destination format negotiation, crop/compose scaler-ratio limits, rotation and flips, tiled formats, DMABUF/MMAP/USERPTR queues, runtime PM reference balance, job abort, and hardware IRQ completion through `fimc_m2m_job_finish()`.
