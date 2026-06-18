# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_notifier_helper.c

Purpose: registers a CEC notifier for an HDMI DRM connector when a separate CEC adapter driver consumes connector identity and physical-address changes.

Important APIs/types/functions: exports `drmm_connector_hdmi_cec_notifier_register`. Internal `drm_connector_cec_funcs` implementations forward physical address set/invalidate operations to `cec_notifier_set_phys_addr` and `cec_notifier_phys_addr_invalidate`.

Control flow: registration fills a `cec_connector_info` from the DRM connector, calls `cec_notifier_conn_register` for the supplied parent device and port name, stores the notifier pointer and connector CEC ops under `connector->cec.mutex`, and registers a DRM-managed cleanup action. Cleanup unregisters the notifier and clears `connector->cec.data`.

State and persistence: `connector->cec.data` persists as a `struct cec_notifier *` while the DRM device is alive. Physical address state is held by the media CEC notifier framework and updated by HDMI hotplug/EDID parsing through the connector CEC callbacks.

Dependencies and integration: depends on DRM connector metadata, DRM managed cleanup, Linux CEC notifier APIs, and HDMI hotplug helpers that call `drm_connector_cec_phys_addr_set` or invalidate. It complements `drm_hdmi_cec_helper.c`; drivers should use one model depending on whether they own a full CEC adapter or only publish notifier data.

Risks: registration failure returns `-ENOMEM` for a null notifier. The helper assumes no competing CEC data is already installed on the connector. Consumers must keep port names and connector info stable enough for CEC routing. Physical address callbacks assume `connector->cec.data` remains valid until managed cleanup.

Test signals: cover successful notifier registration, managed-action rollback, unregister cleanup, physical address update propagation, invalidation on disconnect, and behavior when notifier allocation fails.
