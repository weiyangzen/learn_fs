# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_display.h

Purpose: This header defines the public DP display object shared with MSM KMS, bridge code, audio, and panel/encoder initialization. It is the stable contract around the private orchestration implemented in `dp_display.c`.

Important APIs and types: `struct msm_dp` carries the platform device, DRM device, connector, next bridge, audio handle, connector type, link/power/audio booleans, internal HPD state, eDP flag, and PSR flag. `DP_MAX_PIXEL_CLK_KHZ` caps mode validation at 675 MHz before wide-bus or YUV420 halving. Function declarations expose mode enumeration, test-pattern state, test bpp, audio start/complete signaling, PSR control, and debugfs initialization.

Control flow and state: This header does not implement flow, but its fields are read and written across probe/bind, HPD notification, atomic bridge enable/disable, audio callbacks, debugfs, and mode validation. `link_ready` drives connector detection; `power_on` gates duplicate enable/disable and snapshots; `audio_enabled` coordinates audio shutdown wait; `internal_hpd` suppresses external HPD notifications when the DP block owns HPD; `is_edp` switches bridge behavior and AUX-bus handling.

Dependencies and integration: It includes DRM connector types and `dp_audio.h`, tying the display object to DRM bridge connector setup and HDMI/DP audio helpers. It is included by `dp_drm.h` and other MSM display code that stores `kms->dp[id]`.

Risks and test signals: Because this structure is shared rather than opaque, field semantics must remain synchronized with `dp_display.c` and `dp_drm.c`. Tests should cover public state transitions: `link_ready` after HPD, `power_on` after atomic enable/disable, audio completion paths, eDP PSR state, and mode validation against `DP_MAX_PIXEL_CLK_KHZ`.
