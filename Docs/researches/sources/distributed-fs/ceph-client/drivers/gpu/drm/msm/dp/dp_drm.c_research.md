# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.c

Purpose: This file adapts MSM DP/eDP display logic to DRM bridge and bridge-connector APIs. It separates DP-specific HPD/detect/audio operations from eDP self-refresh behavior while delegating actual hardware sequencing to `dp_display.c`.

Important APIs and functions: DP bridge ops include detect, atomic check, get modes, debugfs init, HPD enable/disable/notify, audio prepare/shutdown, and the generic atomic/mode callbacks exported by `dp_display.c`. eDP bridge ops wrap atomic enable/disable/post-disable to enter or exit PSR around CRTC self-refresh transitions and use a looser mode-valid path because panel drivers provide supported eDP modes. `msm_dp_bridge_init()` allocates `struct msm_dp_bridge`, sets bridge type and YUV420 capability, attaches DP audio metadata for external DP, registers and attaches the bridge, and optionally attaches `next_bridge`. `msm_dp_drm_connector_init()` creates a bridge connector and DP subconnector property for pluggable DP.

Control flow: During modeset init, `dp_display.c` calls `msm_dp_bridge_init()` then connector init. For DP, DRM detect reads `dp->link_ready`; get_modes returns cached EDID modes only after HPD. Atomic check rejects commits on HPD-capable bridges when unplugged to avoid disabling already-dead hardware. For eDP, atomic check marks connector self-refresh-aware if PSR is supported; atomic disable enters PSR when the new CRTC state requests self-refresh, exits PSR on disable from self-refresh, and skips full post-disable while self-refresh remains active.

State and dependencies: It uses `struct msm_dp` fields plus DRM atomic/bridge state. Dependencies are DRM bridge connector helpers, DRM atomic helpers, MSM KMS, DP audio, and DP display exports.

Risks and test signals: Risks include incorrect HPD rejection causing userspace modeset failures, eDP PSR entry/exit ordering, bridge attachment order with external panel bridges, and audio metadata only being set for external DP. Test with hotplug detect/get_modes, unplug while CRTC active, eDP self-refresh commits, external bridge attach, DP audio prepare/shutdown, and YUV420 mode allowance.
