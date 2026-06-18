# sources/distributed-fs/ceph-client/include/sound/omap-hdmi-audio.h

Source read summary: 39 lines, OMAP HDMI audio platform-data bridge.

Purpose: defines the pdata contract between OMAP display/HDMI code and its audio codec/DAI integration.

Important APIs, types, and functions: `struct omap_hdmi_audio_ops` exposes audio startup, shutdown, start, stop, and audio config callbacks. `struct omap_hdmi_audio_pdata` carries device pointer, opaque HDMI data, ops pointer, and DMA/audio configuration values for the platform driver.

Control flow: OMAP HDMI code provides pdata, the audio driver calls ops to configure and start HDMI audio streams, and shutdown/stop functions reverse the setup.

State and persistence behavior: pdata is static per-device glue; stream state lives in the OMAP HDMI/display and ASoC runtime drivers.

Dependencies and integration points: integrates TI OMAP DSS/HDMI blocks with ALSA/ASoC HDMI audio handling.

Risks and edge cases: callback lifetime and opaque data ownership must match device removal; config values must align with HDMI video/audio state.

Test signals: OMAP HDMI audio probe, stream start/stop, display hotplug/suspend interactions, invalid pdata handling, and callback ordering.
