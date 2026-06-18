# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.c

Purpose: Implements DisplayPort audio register programming and HDMI-codec bridge callbacks for the MSM DP driver.

Important APIs/functions: `msm_dp_audio_get()` allocates `struct msm_dp_audio_private` and returns the public `struct msm_dp_audio`. `msm_dp_audio_prepare()` validates that DP display power is on, stores channel count, programs audio SDPs, ACR, safe-to-exit level, enables audio, signals audio start, and marks audio enabled. `msm_dp_audio_shutdown()` disables audio only if it was enabled and signals completion so display clocks can be shut down. Helper functions program stream, timestamp, infoframe, copy-management, and ISRC SDP headers, ACR link-rate selection, mainlink safe-to-exit level, and `MMSS_DP_AUDIO_CFG`.

Control flow: HDMI-codec calls prepare after bridge/display setup. The code relies on `msm_dp_display->power_on` to avoid unclocked register access and on `audio_enabled` to guard shutdown after disconnect. SDP headers are packed through `msm_dp_utils_pack_sdp_header()` and written to link registers before enabling audio.

State and persistence: Public state stores lane count and bandwidth code for the current link. Private state stores pdev, DRM dev pointer, link base, channel count, and embedded public object. State is device-managed and not persistent.

Dependencies/integration: Depends on DP display bridge conversion, DP panel/reg/utils headers, DRM DP helper definitions, HDMI codec params, and link register MMIO. Display code supplies lane count/bw code and handles audio start/complete signals.

Risks and test signals: `drm_dev` is present but not set in `msm_dp_audio_get()`, so debug logging using it must tolerate null. ACR selection defaults on unknown link rate. Shutdown depends on `audio_enabled`, not connector status. Test audio prepare before connect, normal playback, disconnect while audio active, all link rates/lane counts, and repeated prepare/shutdown cycles.
