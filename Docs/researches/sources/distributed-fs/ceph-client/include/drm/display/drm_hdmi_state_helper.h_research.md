# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_state_helper.h

Purpose: atomic connector helpers for HDMI state reset, validation, audio/infoframe update and clear, hotplug/force handling, and mode validation.

Important APIs/types/functions: `__drm_atomic_helper_connector_hdmi_reset`, `drm_atomic_helper_connector_hdmi_check`, `drm_atomic_helper_connector_hdmi_update_audio_infoframe`, `drm_atomic_helper_connector_hdmi_clear_audio_infoframe`, `drm_atomic_helper_connector_hdmi_update_infoframes`, `drm_atomic_helper_connector_hdmi_hotplug`, `drm_atomic_helper_connector_hdmi_force`, and `drm_hdmi_connector_mode_valid`.

Control flow: drivers reset HDMI connector state, run check during atomic validation, update or clear infoframes during commit, and call hotplug/force helpers when status changes.

State and persistence: no header storage. It operates on DRM atomic connector state and hardware infoframe state at runtime.

Dependencies and integration points: DRM atomic state, connectors/states, display modes, HDMI audio infoframes, connector status, and generic atomic modesetting.

Risks and test signals: reset defaults, stale infoframes, hotplug races, and invalid high-clock/color modes are risks. Test atomic check, infoframe-affecting property changes, audio enable/disable, hotplug/forced connectors, and mode validation.
