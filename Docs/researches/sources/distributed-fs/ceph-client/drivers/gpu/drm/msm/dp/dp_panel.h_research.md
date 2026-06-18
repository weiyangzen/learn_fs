# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_panel.h

Purpose: This header defines the public DP panel/sink capability model and timing API used by display and controller code.

Important APIs and types: `struct msm_dp_display_mode` wraps a DRM mode with selected bpp, sync polarities, and YUV420 output flag. `struct msm_dp_panel_psr` stores PSR version/capabilities. `struct msm_dp_panel` stores DPCD, downstream ports, negotiated link info, cached EDID, connector, selected mode, PSR capabilities, video-test state, VSC support, hardware revision, and max bandwidth code. Inline helpers validate DP link rate and lane count. Public functions read sink capabilities, initialize mode info, configure timing, expose EDID modes, respond to sink requests, drive TPG, manage DSC DTO and VSC SDP, and allocate/free the panel object.

Control flow and state: `dp_display.c` populates and consumes this structure during HPD, mode validation, mode set, and stream enable. `dp_ctrl.c` relies on `link_info` and timing data for link training and stream setup. `dp_panel.c` owns EDID lifetime and mode-derived panel state.

Dependencies and integration: It includes DRM modes/MSM DRM, `dp_aux.h`, and `dp_link.h`, making it the sink-facing bridge between AUX/link negotiation and register programming.

Risks and test signals: Risks are shared mutable fields such as `drm_edid`, `video_test`, and `vsc_sdp_supported`. Compile and runtime testing should cover lane/rate validation, bpp selection, EDID mode enumeration, YUV420 SDP enablement, and PSR capability propagation.
