# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_helper.c

Purpose: registers a real CEC adapter for an HDMI DRM connector and bridges CEC framework operations to driver-provided HDMI CEC callbacks.

Important APIs/types/functions: exports `drmm_connector_hdmi_cec_register`, `drm_connector_hdmi_cec_received_msg`, `drm_connector_hdmi_cec_transmit_attempt_done`, and `drm_connector_hdmi_cec_transmit_done`. It defines `struct drm_connector_hdmi_cec_data` holding a `cec_adapter` and driver `drm_connector_hdmi_cec_funcs`, plus `cec_adap_ops` and `drm_connector_cec_funcs` adapters.

Control flow: registration validates mandatory driver callbacks (`init`, `enable`, `log_addr`, `transmit`), allocates connector CEC data, allocates a CEC adapter with connector-info capability, fills connector info from DRM metadata, stores data/functions under `connector->cec.mutex`, calls the driver `init`, registers the adapter with the CEC framework, and attaches a DRM-managed cleanup action. Adapter operations fetch the connector with `cec_get_drvdata` and forward enable/log-address/transmit calls to driver hooks. HDMI connector physical-address updates call `cec_s_phys_addr` or `cec_phys_addr_invalidate`. Receive/transmit completion exports forward low-level hardware notifications back into the CEC framework.

State and persistence: `connector->cec.data` points to allocated helper data until DRM-managed cleanup unregisters the adapter, calls optional driver `uninit`, frees memory, and clears the connector pointer. The CEC adapter can outlive DRM cleanup until userspace closes descriptors, but the CEC framework short-circuits operations after unregister.

Dependencies and integration: uses Linux CEC core, DRM managed actions, connector CEC hooks, connector info helpers, and HDMI hotplug paths that update CEC physical addresses. It is for drivers with native CEC hardware rather than only a notifier.

Risks: callback lifetime and locking are central. The code holds `connector->cec.mutex` across driver `init` and adapter registration; driver callbacks must avoid reentrant CEC connector locking. Exported receive/transmit notification helpers assume registration has succeeded and `connector->cec.data` is valid. Cleanup must pair `cec_unregister_adapter` with the CEC framework lifetime rules.

Test signals: cover mandatory callback validation, allocation/register failures, cleanup action rollback, physical address set/invalidate propagation, transmit completion forwarding, userspace-open adapter lifetime after DRM unbind, and hotplug integration.
