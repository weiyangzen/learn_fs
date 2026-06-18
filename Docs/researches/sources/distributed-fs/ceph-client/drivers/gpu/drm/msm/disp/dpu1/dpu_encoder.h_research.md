# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder.h

Purpose: this header declares the public DPU encoder interface shared with CRTC, KMS, writeback, physical encoder code, and DRM integration.

Important constants and types: frame-event bits define encoder-to-CRTC notifications for done, error, panel-dead, and idle. `IDLE_TIMEOUT` sets the delayed idle-power-collapse duration, and `MAX_H_TILES_PER_DISPLAY` bounds split displays. `struct msm_display_info` describes interface type, tile count, controller IDs per tile, command-mode flag, and TE/vsync source.

Important APIs: lifecycle and commit helpers include `dpu_encoder_init()`, `dpu_encoder_assign_crtc()`, `dpu_encoder_prepare_for_kickoff()`, `dpu_encoder_trigger_kickoff_pending()`, `dpu_encoder_kickoff()`, `dpu_encoder_start_frame_done_timer()`, and `dpu_encoder_virt_runtime_resume()`. Synchronization APIs include `dpu_encoder_wait_for_commit_done()` and `dpu_encoder_wait_for_tx_complete()`. Query helpers expose interface mode, line/vsync counts, clone masks, widebus, DSC, DSC merge, CRC count/values, and commit validity. Topology/writeback APIs include `dpu_encoder_update_topology()`, `dpu_encoder_needs_modeset()`, `dpu_encoder_prepare_wb_job()`, and `dpu_encoder_cleanup_wb_job()`.

Dependencies and integration: includes DRM CRTC and `dpu_hw_mdss.h`. CRTC code uses these declarations for vblank toggling, kickoff sequencing, frame timers, topology, CRC, and writeback clone mode. Physical encoder implementations provide the underlying mode-specific operations.

State and persistence: no state lives in the header. It defines contracts over state stored in `struct dpu_encoder_virt` and physical encoder structs in the C file.

Risks: the header exposes many functions that must be called in a specific order: assign CRTC, mode set/enable, prepare, kickoff, timer, wait, disable. Misordering can cause IRQ waits without resources, stale CRTC pointers, or missed frame done. Frame-event bits are shared ABI within the driver and must stay consistent with CRTC handling.

Test signals: compile coverage for all call sites, split DSI tile initialization, vblank enable/disable per CRTC, commit/tx waits, topology update during atomic check, widebus/DSC queries, CRC setup/collection, and writeback job prepare/cleanup.
