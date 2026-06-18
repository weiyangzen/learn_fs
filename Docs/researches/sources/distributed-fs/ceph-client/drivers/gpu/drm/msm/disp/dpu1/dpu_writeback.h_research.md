# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.h

Purpose: declares the DPU-specific DRM writeback connector wrapper and init entry point.

Important APIs and types: `struct dpu_wb_connector` embeds `struct drm_writeback_connector`, tracks the associated writeback encoder in `wb_enc`, and stores `maxlinewidth`. `to_dpu_wb_conn()` converts from the embedded DRM writeback connector to the wrapper. `dpu_writeback_init()` constructs the connector for an encoder and format list.

Control flow and integration: DPU KMS or encoder initialization uses `dpu_writeback_init()` after creating a writeback encoder. DRM writeback callbacks installed in the C file then route job preparation and cleanup back to the DPU encoder.

State and persistence: all state is in-memory DRM object lifetime state. The wrapper has no persistent storage.

Dependencies: includes DRM CRTC/file/probe/writeback headers and DPU/MSM driver headers. It relies on `dpu_encoder_phys.h` for encoder-side writeback job hooks.

Risks: the container conversion assumes callers pass a `drm_writeback_connector` embedded in `dpu_wb_connector`. The encoder pointer must remain valid for the connector lifetime.

Test signals: compile coverage for DRM API signature changes, writeback connector creation tests, and writeback job execution/cleanup under normal and aborted atomic commits.
