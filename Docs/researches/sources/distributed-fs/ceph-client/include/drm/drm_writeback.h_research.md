# sources/distributed-fs/ceph-client/include/drm/drm_writeback.h

## Purpose
`drm_writeback.h` declares the DRM writeback connector abstraction, which lets a display pipeline write composed output into a framebuffer and signal completion with a fence.

## Important APIs, types, and functions
`struct drm_writeback_connector` embeds a connector, an internal encoder for the standard init path, pixel-format blob pointer, job queue lock/list, fence context/lock/seqno, and timeline name. `struct drm_writeback_job` stores connector backpointer, prepared flag, cleanup work, queue link, destination framebuffer, output fence, and driver-private data. APIs include `drm_connector_to_writeback`, `drm_writeback_connector_init`, `drm_writeback_connector_init_with_encoder`, `drmm_writeback_connector_init`, `drm_writeback_set_fb`, `drm_writeback_prepare_job`, `drm_writeback_queue_job`, `drm_writeback_cleanup_job`, `drm_writeback_signal_completion`, and `drm_writeback_get_out_fence`.

## Control flow
Drivers initialize a writeback connector with supported pixel formats and CRTC mask. Atomic connector state sets the target framebuffer, prepares a job to hold references and create an out fence, queues it for hardware, and later signals completion status. Cleanup may defer dropping framebuffer references to a workqueue.

## State and persistence
Runtime state is connector/encoder registration, pixel-format blob, queued jobs, fence timeline counters, locks, framebuffer references, and output fences. Jobs are transient per writeback commit.

## Dependencies and integration points
It depends on DRM connectors, encoders, connector state, framebuffers, dma-fence, and workqueues. It integrates with atomic KMS writeback properties and userspace that captures display output.

## Risks and test signals
Risks include job queue ordering mistakes, failing to signal out fences on error, framebuffer reference leaks, encoder ownership confusion between init variants, pixel-format blob mismatch, and completion after connector teardown. Test signals include writeback connector init variants, atomic writeback commits, unsupported format rejection, out-fence signaling success/error, cleanup work execution, queued job ordering, and driver unload with pending jobs.
