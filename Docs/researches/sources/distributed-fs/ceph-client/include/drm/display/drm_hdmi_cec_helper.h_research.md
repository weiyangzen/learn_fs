# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_cec_helper.h

Purpose: HDMI CEC connector helper interface for managed adapter registration, received-message delivery, transmit completion, and optional CEC notifier registration.

Important APIs/types/functions: `struct drm_connector_hdmi_cec_funcs` with init/uninit/enable/log_addr/transmit callbacks, `drmm_connector_hdmi_cec_register`, `drm_connector_hdmi_cec_received_msg`, `drm_connector_hdmi_cec_transmit_done`, `drm_connector_hdmi_cec_transmit_attempt_done`, and Kconfig-gated `drmm_connector_hdmi_cec_notifier_register`.

Control flow: drivers register CEC callbacks for a connector; CEC core invokes hardware callbacks, while IRQ/polling code reports received messages and transmit status. Notifier registration is a stub when disabled.

State and persistence: no header state. Managed adapter lifetime follows connector/device cleanup; logical addresses and enable state are runtime hardware state.

Dependencies and integration points: Linux types, DRM connectors, CEC messages/adapters, devices, managed DRM cleanup, optional notifier support, and HDMI bridge drivers.

Risks and test signals: callback ordering, transmit races, logical address failures, disabled notifier assumptions, and hotplug teardown are risks. Test registration, enable/disable, multi-LA, receive delivery, transmit done/attempt done, notifier Kconfig modes, and connector removal.
