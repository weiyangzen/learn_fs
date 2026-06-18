# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_bridge.c

Purpose: DRM bridge implementation for the MSM HDMI transmitter. It controls bridge power sequencing, mode timing registers, HDMI infoframes, EDID/DDC access, HPD notification work, TMDS clock validation, PHY powerup/down, HDCP hooks, and HDMI audio bridge callbacks.

Important APIs and functions:
- `msm_hdmi_power_on()` and `power_off()` manage runtime PM and optional external pixel clock.
- `msm_hdmi_bridge_atomic_pre_enable()` programs timings, powers resources, updates audio/infoframes, powers the PHY, enables HDMI core, and starts HDCP.
- `msm_hdmi_bridge_atomic_post_disable()` stops HDCP, disables HDMI core while preserving HPD mode if needed, powers down PHY, updates audio, disables resources, and drops runtime PM.
- `msm_hdmi_set_timings()` writes total, active hsync/vsync, interlace F2, and frame polarity registers.
- clear/write infoframe helpers implement AVI, audio, SPD, and vendor HDMI packets.
- `msm_hdmi_bridge_edid_read()`, `msm_hdmi_bridge_tmds_char_rate_valid()`, `msm_hdmi_hotplug_work()`, and `msm_hdmi_bridge_init()` integrate EDID, mode validation, HPD work, and DRM bridge registration.

Control flow: atomic pre-enable obtains the new connector and CRTC state, stores TMDS char rate in `hdmi->pixclock`, programs timings, powers resources under `state_mutex` if not already on, updates audio if sink is HDMI, asks DRM helpers to update infoframes, powers the PHY with current pixclock, enables the HDMI core, and turns on HDCP. Post-disable reverses this, but `msm_hdmi_set_mode()` is called with `hpd_enabled` to keep the core active enough for HPD if requested. EDID read temporarily sets `HDMI_CTRL_ENABLE` around DDC access and restores the previous control value.

State and persistence: `hdmi->pixclock` persists the current TMDS rate and feeds audio ACR plus PHY/external clock setup. `power_on` and `hpd_enabled` are protected by `state_mutex`. Infoframe register state persists until DRM helper callbacks clear or rewrite it. HPD work queues bridge notifications asynchronously on the HDMI workqueue.

Dependencies and integration points: uses DRM bridge atomic helpers, bridge connector, EDID/DDC helpers, HDMI infoframe state helpers, MSM KMS `round_pixclk`, optional `extp_clk`, HDMI PHY power helpers, HDCP helpers, and audio callbacks in `hdmi_audio.c`.

Risks: power-on ignores the return value of `pm_runtime_resume_and_get()`, so later register/clock operations may proceed after runtime PM failure. Infoframe packing is hardware-specific and length-sensitive. EDID temporarily modifies `REG_HDMI_CTRL` without `reg_lock`, while other paths also touch that register. `power_off()` waits a fixed 20 ms rather than synchronizing to an actual final vblank. TMDS validation demands exact rounded rate equality, which can reject modes if clock providers round slightly.

Test signals: atomic enable/disable on HDMI and DVI sinks, interlaced and polarity flag modes, all infoframe helper paths and invalid lengths, EDID read with HPD on/off, TMDS validation through KMS `round_pixclk` and `extp_clk`, HDCP on/off sequencing, runtime PM failure injection, and hotplug work notification.
