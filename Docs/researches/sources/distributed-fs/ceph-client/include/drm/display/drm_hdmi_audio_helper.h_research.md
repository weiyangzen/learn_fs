# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_audio_helper.h

Purpose: connector-level HDMI audio codec registration and plug notification helper interface.

Important APIs/types/functions: `drm_connector_hdmi_audio_init` and `drm_connector_hdmi_audio_plugged_notify`, with initialization parameters for codec device, audio callbacks, max I2S channels, I2S formats, SPDIF support, and sound DAI port.

Control flow: HDMI drivers initialize connector audio support after connector setup and notify plugged/unplugged state from hotplug/detect paths.

State and persistence: no header state. Audio state belongs to connector private data and HDMI codec integration; plug state is runtime only.

Dependencies and integration points: Linux types, DRM connectors, HDMI audio callback definitions, devices, ALSA HDMI codec, I2S/SPDIF capabilities, and hotplug.

Risks and test signals: wrong channel/format capabilities, missed plug notifications, codec lifetime mismatch, and DAI port errors are risks. Test codec registration, hotplug/unplug, ELD/audio routing, I2S/SPDIF exposure, and cleanup.
