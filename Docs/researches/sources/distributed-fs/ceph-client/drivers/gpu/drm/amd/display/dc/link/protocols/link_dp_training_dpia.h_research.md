# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.h

Purpose: public interface for USB4 DPIA DP link training.

Important APIs/types: `DPIA_CLK_SYNC_DELAY` defines the approximate 16 ms wait for nine USB4 DP clock-sync packets. Exports `dpia_perform_link_training`, `dpia_training_abort`, `dpia_get_eq_aux_rd_interval`, and `dpia_set_tps_notification`.

Control flow/integration: callers use `dpia_perform_link_training` as the DPIA equivalent of normal DP training. Lower-level helpers are exposed so shared PHY/DPCD training code can request cleanup, timing, or TPS notification behavior when DPIA is involved.

State/persistence: no persistent state in the header; all state flows through `dc_link`, `link_resource`, `dc_link_settings`, and `link_training_settings`.

Dependencies: includes `link_dp_training.h` for training settings/result enums and common DP structures.

Risks: the API exposes hop-indexed operations; callers must pass DPRX/repeater offsets consistently with the implementation's hop model.

Test signals: compile coverage for DPIA callers, link-training abort cleanup, and correct propagation of `skip_video_pattern` even though the current implementation ignores it.
