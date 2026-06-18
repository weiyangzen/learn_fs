# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_audio_helper.c

Purpose: adapts a DRM HDMI connector to the ALSA `hdmi-codec` platform-device interface so display drivers can expose audio callbacks, ELD data, DAI routing, stream mute, and plugged-state notifications through a common connector-owned helper.

Important APIs/types/functions: exports `drm_connector_hdmi_audio_init` and `drm_connector_hdmi_audio_plugged_notify`. It builds a static `struct hdmi_codec_ops` bridge around `struct drm_connector_hdmi_audio_funcs`, stores state in `connector->hdmi_audio`, and uses `struct hdmi_codec_pdata` to instantiate `HDMI_CODEC_DRV_NAME`.

Control flow: `drm_connector_hdmi_audio_init` validates required `prepare` and `shutdown` callbacks, stores callback and DAI-port metadata on the connector, prepares `hdmi_codec_pdata`, and registers a platform device under the supplied parent. Codec callbacks unwrap the connector from opaque `data`: startup is optional, prepare/shutdown call driver hooks, mute is optional and returns `-ENOTSUPP` when absent, ELD copies the connector ELD under `eld_mutex`, DAI ID parses OF graph endpoint and matches the configured port, and plugged callback registration stores a callback/device pair then immediately reports the last known state. `drm_connector_hdmi_audio_plugged_notify` updates `last_state` and invokes the registered callback under the HDMI audio lock.

State and persistence: persistent connector fields include callback pointers, platform device pointer, DAI port, plugged callback, callback device, last plugged state, and the ELD buffer owned by the connector. Locks protect ELD copying and plugged callback state. The helper does not unregister the codec device itself in this file, so lifecycle integration is expected from connector/device teardown paths.

Dependencies and integration: depends on `sound/hdmi-codec.h`, platform device registration, OF graph parsing, DRM connector/device structures, and connector hotplug code. `drm_bridge_connector.c` and VC4 HDMI paths use this helper to bind HDMI audio to DRM connector state.

Risks: required callback validation is minimal; driver hooks must tolerate codec timing and connector lifetime. Plugged callbacks are invoked while holding `hdmi_audio.lock`, so callback implementations must avoid lock inversions. `get_eld` silently truncates to the caller buffer length. DAI routing fails with `-ENOTSUPP` when disabled and `-EINVAL` when endpoint ports do not match.

Test signals: cover platform-device registration failures, missing required callbacks, ELD copy/truncation, OF endpoint DAI selection, plugged callback immediate replay, hotplug notify ordering, and optional mute/startup fallback behavior.
