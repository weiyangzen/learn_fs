# sources/distributed-fs/ceph-client/include/media/cec-notifier.h

Purpose: Defines the notifier contract that lets HDMI connector/DRM/display drivers report CEC physical-address changes to CEC adapters.

Important APIs/types/functions: Registration APIs are `cec_notifier_conn_register`, `cec_notifier_conn_unregister`, `cec_notifier_cec_adap_register`, and `cec_notifier_cec_adap_unregister`. Update helpers are `cec_notifier_set_phys_addr`, `cec_notifier_set_phys_addr_from_edid`, `cec_notifier_parse_hdmi_phandle`, and inline `cec_notifier_phys_addr_invalidate`.

Control flow: HDMI-side code registers a notifier for a device/port tuple and pushes physical-address updates, often parsed from EDID. CEC adapter code registers with the same tuple and receives those updates through the CEC core. Refcounts keep the shared notifier alive until both sides unregister.

State and persistence: The opaque `struct cec_notifier` owns shared connector state and refcounting in the core. When CEC/notifier support is disabled, stubs return a sentinel non-NULL pointer for register calls and no-op updates.

Dependencies and integration: Depends on `<media/cec.h>`, `struct device`, EDID, device-tree `hdmi-phandle`, and optional `CONFIG_CEC_CORE`/`CONFIG_CEC_NOTIFIER`.

Risks and test signals: Risks include stale connector keys, missing unregister, disabled-config sentinel misuse, and EDID physical-address parse failures. Test multi-connector devices, refcount lifetime, invalidation on HPD loss, disabled-config builds, and phandle lookup error paths.
