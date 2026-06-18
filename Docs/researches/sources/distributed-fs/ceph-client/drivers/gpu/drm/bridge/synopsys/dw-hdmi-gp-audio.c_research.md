# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-gp-audio.c

Purpose: provides a lightweight HDMI-codec based audio interface for the DesignWare HDMI General Purpose Audio path, mainly used by NXP platforms.

Important APIs/types/functions: `struct snd_dw_hdmi` stores copied `dw_hdmi_audio_data` and the registered HDMI codec platform device. `audio_hw_params()` programs sample rate, channel count, channel allocation, non-PCM flag, sample width, and IEC958 subframe mode through DW-HDMI core APIs. `audio_mute_stream()` toggles DW-HDMI audio enable/disable. `audio_get_eld()` copies ELD from the parent connector. `audio_hook_plugged_cb()` registers HDMI hotplug callback. Probe registers an `HDMI_CODEC_DRV_NAME` child with I2S enabled, SPDIF disabled, max 8 channels, and the ops table.

Control flow: the platform driver receives parent-provided `dw_hdmi_audio_data`, copies it, and creates an hdmi-codec device. During playback setup the ASoC HDMI codec calls `hw_params`, then mute/unmute controls audio start/stop. Remove unregisters the codec device.

State and persistence: driver-owned state is only copied platform data and codec pdev pointer. Audio parameters are pushed to parent DW-HDMI state on each hw_params call; no local stream state is tracked.

Dependencies and integration: depends on `sound/hdmi-codec.h`, ALSA IEC958 constants, DRM ELD/connector headers, and DW-HDMI exported audio control functions. It shares channel allocation defaults with the AHB driver.

Risks: `params->channels - 2` indexes a seven-entry table without local bounds checks, relying on hdmi-codec constraints. `audio_shutdown()` is empty, so mute callbacks must perform actual stop. Probe assumes non-NULL platform data. GP-specific hardware enablement is delegated entirely to the parent core.

Test signals: hdmi-codec registration, 2-8 channel LPCM and IEC958 formats, ELD reads with and without connector, plug callback propagation, mute/unmute behavior, and remove/unregister ordering.
