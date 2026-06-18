# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.c

Purpose: creates and validates a DRM writeback connector for DPU writeback encoders.

Important APIs and functions: `dpu_writeback_init()` allocates `struct dpu_wb_connector`, installs connector helper funcs, and calls `drmm_writeback_connector_init()`. `dpu_wb_conn_get_modes()` creates no-EDID modes bounded by catalog `max_mixer_width` and DRM `max_height`. `dpu_wb_conn_atomic_check()` validates writeback job framebuffer dimensions against the CRTC mode, enforces `maxlinewidth`, and only accepts linear modifiers. `dpu_wb_conn_prepare_job()` and `dpu_wb_conn_cleanup_job()` delegate framebuffer job setup/teardown to DPU encoder helpers.

Control flow: atomic check is a no-op for disconnected or job-less states, otherwise it obtains CRTC state, compares job framebuffer to mode, and then invokes DRM writeback helper validation. Job callbacks skip null framebuffers.

State and persistence: connector state is managed by DRM atomic helpers. The DPU wrapper stores the encoder pointer and max line width for the connector lifetime.

Dependencies and integration: depends on DRM writeback helpers, DPU KMS catalog, and `dpu_encoder_prepare_wb_job()`/`dpu_encoder_cleanup_wb_job()`. Writeback resource reservation is handled elsewhere by DPU RM and encoder code.

Risks: modes are limited to mixer width until dual-SSPP/source split support exists, so some valid hardware writeback combinations may be hidden. Non-linear modifiers are rejected. Incorrect max height or catalog max line width can expose modes that later fail bandwidth checks.

Test signals: atomic writeback jobs should pass only when framebuffer size equals mode, width is within max line width, and modifier is linear. IGT writeback and invalid-fb tests are useful.
