# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.h

Purpose: this header defines DPU's private CRTC structures, enums, inline helpers, and public CRTC APIs used by encoder, plane, KMS, and performance code.

Important types: `enum dpu_crtc_client_type` separates real-time scanout from non-real-time writeback. SMMU enums and `struct dpu_crtc_smmu_state_data` track attach/detach transitions. `enum dpu_crtc_crc_source` selects none, layer mixer, or encoder CRC/MISR. `struct dpu_crtc_mixer` binds LM, CTL, optional DSPP, and mixer operation mode for each virtual pipeline. `struct dpu_crtc_frame_event` packages encoder frame events for kthread work. `struct dpu_crtc` embeds `drm_crtc` and stores event, vblank, frame, lock, performance, and SMMU state. `struct dpu_crtc_state` extends `drm_crtc_state` with performance, resource assignments, LM bounds, and CRC state.

Important APIs: `dpu_crtc_frame_pending()`, `dpu_crtc_check_mode_changed()`, `dpu_crtc_vblank()`, `dpu_crtc_vblank_callback()`, `dpu_crtc_commit_kickoff()`, `dpu_crtc_complete_commit()`, `dpu_crtc_init()`, `dpu_crtc_get_intf_mode()`, `dpu_crtc_get_client_type()`, `dpu_crtc_frame_event_cb()`, and `dpu_crtc_get_num_lm()`.

Dependencies and integration: includes DRM CRTC, `dpu_kms.h`, and `dpu_core_perf.h`. Encoders call vblank/frame-event/commit helpers; performance code consumes CRTC state; planes are assigned through atomic resource logic.

State and persistence: live `dpu_crtc` objects persist with DRM device lifetime, while `dpu_crtc_state` is duplicated/destroyed through atomic helpers. Frame-event structures are statically cached to avoid IRQ-context allocation.

Risks: `dpu_crtc_get_client_type()` returns RT whenever `crtc->state` exists, otherwise NRT, which is simple but can be surprising for writeback-only paths. Fixed-size mixer/event arrays depend on constants such as `CRTC_DUAL_MIXERS` and `DPU_CRTC_FRAME_EVENT_SIZE`. SMMU transition fields are shared state that can poison plane flushes on errors.

Test signals: compile coverage across encoder/CRTC/perf users, atomic state duplication/reset/destroy, frame-event callback paths, RT/NRT classification, SMMU transition error handling, and CRC source changes.
