# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_writeback.c

## Purpose
Implements DRM writeback connector support: connector-specific properties, internal/custom encoder initialization, framebuffer-backed writeback jobs, out-fence creation/signaling, and deferred cleanup.

## Important APIs, Types, and Functions
Exports `drm_writeback_connector_init`, `drm_writeback_connector_init_with_encoder`, `drmm_writeback_connector_init`, `drm_writeback_prepare_job`, `drm_writeback_queue_job`, `drm_writeback_cleanup_job`, `drm_writeback_signal_completion`, and `drm_writeback_get_out_fence`. It creates properties `WRITEBACK_FB_ID`, `WRITEBACK_PIXEL_FORMATS`, and `WRITEBACK_OUT_FENCE_PTR`. `struct drm_writeback_connector` owns a job queue, job lock, fence lock/context/seqno, and pixel-format blob.

## Control Flow
Initialization creates shared writeback properties, initializes a writeback connector, attaches an encoder, creates the immutable formats blob, initializes job/fence state, and attaches properties. `drm_writeback_set_fb()` lazily allocates a connector-state job and references the framebuffer. Prepare invokes optional connector helper validation/setup and marks the job prepared. Queue transfers job ownership from connector state to FIFO queue. Completion pops the first job, signals and releases its out-fence, then schedules job cleanup on `system_long_wq` because framebuffer release can sleep.

## State and Persistence
State is in-memory DRM object state. Jobs persist in `job_queue` from commit queueing to hardware completion. Pixel format blobs are refcounted DRM blobs. Managed init registers cleanup that destroys properties/blob and drains queued jobs.

## Dependencies and Integration Points
Integrates with DRM connector/encoder/property frameworks, atomic connector state, connector helper callbacks (`prepare_writeback_job`, `cleanup_writeback_job`), `dma_fence`, `sync_file` userspace ABI, and driver hardware completion interrupts.

## Risks
Drivers must signal exactly one completion per queued job and preserve hardware FIFO order. Property deletion is device-global and must not break multiple connectors. Accessing a framebuffer after completion without a private reference is unsafe. Out-fence error propagation depends on drivers passing accurate status.

## Test Signals
Atomic writeback tests should check property presence, supported format blob contents, per-commit FB semantics, out-fence signaling/error, FIFO completion ordering, cleanup on connector teardown, and interrupt-context completion.
