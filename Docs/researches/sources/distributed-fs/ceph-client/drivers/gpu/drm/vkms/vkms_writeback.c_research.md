# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_writeback.c

## Purpose

`vkms_writeback.c` implements VKMS writeback connector support. It exposes writeback formats, validates writeback framebuffer size against the active CRTC mode, maps writeback framebuffers for the software composer, queues writeback jobs, and initializes the writeback encoder/connector pair for an output.

## Important APIs, Types, and Functions

- `vkms_wb_formats[]`: supported writeback framebuffer formats.
- `vkms_wb_atomic_check`: validates writeback job framebuffer dimensions and delegates generic writeback state checks.
- `vkms_wb_connector_get_modes`: creates no-EDID modes up to device max width/height.
- `vkms_wb_prepare_job` and `vkms_wb_cleanup_job`: allocate/free `vkms_writeback_job`, vmap/vunmap the writeback framebuffer, and manage framebuffer refs.
- `vkms_wb_atomic_commit`: enables the composer, installs the active writeback job under `composer_lock`, queues the DRM writeback job, and initializes writeback frame info/pixel writer.
- `vkms_enable_writeback_connector`: creates the writeback encoder and calls `drmm_writeback_connector_init`.

## Control Flow

Atomic check returns early when there is no writeback job, no job framebuffer, or no associated CRTC. Otherwise it compares framebuffer dimensions to `crtc_state->mode` and rejects mismatches with `-EINVAL`, then calls DRM's writeback connector checker. Job preparation allocates a VKMS-private job wrapper, maps the framebuffer into `wb_frame_info.map`, takes a framebuffer reference, and stores the wrapper in `job->priv`.

At commit time, the connector state identifies the output CRTC and writeback connector. The composer is enabled, `active_writeback` and `wb_pending` are set while holding `composer_lock`, the job is queued to DRM, and the pixel write callback plus source/destination rectangles are initialized to the full CRTC mode size. Cleanup reverses mapping/refcount state, disables composer writeback participation, and frees the wrapper.

## State and Persistence Behavior

Writeback encoder and connector objects are DRM-managed and persist with the device. Individual writeback jobs allocate transient `vkms_writeback_job` objects stored in DRM job private data. Active job state is shared with the composer through `vkms_crtc_state` fields protected by the output's spinlock.

## Dependencies and Integration Points

- Uses DRM writeback, atomic helper, probe helper, EDID/no-EDID mode helper, and GEM framebuffer mapping APIs.
- Integrates with VKMS compositor state through `vkms_set_composer`, `active_writeback`, `wb_pending`, `wb_frame_info`, and `pixel_write`.
- Uses `get_pixel_write_function` from `vkms_formats.h`, so format lists and write callbacks must remain synchronized.

## Risks and Edge Cases

- `vkms_wb_atomic_commit` dereferences `connector_state->writeback_job->fb`; callers rely on DRM writeback semantics to only call this path for a valid job.
- The active job is published before `pixel_write` and rectangles are filled. The composer synchronization model must guarantee it cannot consume the job before those fields are initialized, or this ordering should be revisited.
- Cleanup returns early for jobs without framebuffer, so `job->priv` must only be set for framebuffer-backed jobs.
- Framebuffer size must exactly match the mode; no scaling or crop behavior is supported for writeback.

## Test Signals

- Writeback tests should cover valid commits, no-job commits, no-framebuffer jobs, framebuffer size mismatch, and each advertised writeback format.
- Race-oriented tests should verify composer state visibility around `active_writeback`, `wb_pending`, queueing, and cleanup.
- Mapping/refcount tests should ensure vmaps and framebuffer references are balanced on success and prepare failure.
