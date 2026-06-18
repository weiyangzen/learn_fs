# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_audio.c

Purpose: HDMI audio programming for MSM HDMI bridge integration. It validates audio parameters, updates DRM HDMI audio infoframes, computes ACR N/CTS values, and enables or disables HDMI audio packets/registers based on video power state.

Important APIs and functions:
- `msm_hdmi_audio_update()` is the low-level register update path for ACR, VBI, audio packet control, audio config, interrupt enable, and general control packets.
- `msm_hdmi_bridge_audio_prepare()` is the DRM bridge HDMI audio callback; it validates sample rates, updates the connector audio infoframe, stores rate/channels/enabled state, and calls the update path.
- `msm_hdmi_bridge_audio_shutdown()` clears the DRM audio infoframe, resets audio state to disabled stereo defaults, and updates hardware.

Control flow: audio prepare accepts only 32, 44.1, 48, 88.2, 96, 176.4, and 192 kHz. If the connector is not HDMI, `msm_hdmi_audio_update()` rejects with `-EINVAL`. Enabled audio is forced off if video is not powered or `pixclock` is zero. For high sample rates, N is divided and an ACR multiplier is used. The selected ACR bank follows the 32/44.1/48 kHz families, then packets, GC, FIFO watermark, engine enable, and interrupts are programmed.

State and persistence: software state is `hdmi->audio.enabled`, `rate`, and `channels`; hardware state persists in HDMI packet/audio registers until changed. The code reads current packet/config registers before modifying bit fields, preserving unrelated state.

Dependencies and integration points: uses DRM HDMI helpers for ACR calculation and atomic connector infoframe updates, ALSA `hdmi-codec` params, `hdmi.xml.h` register fields, and bridge callbacks wired in `hdmi_bridge.c`.

Risks: audio register writes are not protected by `reg_lock`, so interactions with other register users depend on register separation and atomic callback serialization. Non-HDMI/DVI sinks reject audio update. Audio enable depends on current video state and must be refreshed on video power transitions; bridge pre-enable/post-disable does call update. Unsupported rates return `-EINVAL` before touching state.

Test signals: prepare/shutdown for all supported sample rates, rejection of unsupported rates and DVI sinks, 2-channel versus multichannel layout bit, video-off audio suppression, ACR N/CTS verification for each rate family, and audio update during HDMI bridge power transitions.
