# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-notifier.c

Purpose: This file implements the CEC notifier bridge between HDMI/DRM devices that know connector physical addresses and CEC adapters that need those addresses and connector metadata.

Important APIs, types, and functions: `struct cec_notifier` stores lock, list node, kref, HDMI device key, connector info, port name, attached CEC adapter, and physical address. Exported APIs are `cec_notifier_conn_register()`, `cec_notifier_conn_unregister()`, `cec_notifier_cec_adap_register()`, `cec_notifier_cec_adap_unregister()`, `cec_notifier_set_phys_addr()`, `cec_notifier_set_phys_addr_from_edid()`, and `cec_notifier_parse_hdmi_phandle()`. Internal helpers are `cec_notifier_get_conn()`, `cec_notifier_release()`, and `cec_notifier_put()`.

Control flow and state: Connector providers and CEC adapters independently obtain a notifier keyed by `(hdmi_dev, port_name)`. Registration bumps a kref or creates a new object under the global notifier list lock. Connector registration stores connector info and invalidates/updates attached adapters. Adapter registration stores the adapter pointer, copies connector info into it, and pushes the current physical address unless the adapter controls its own physical address. Unregister clears the corresponding side and drops references. EDID helpers parse the source physical address before updating.

State and persistence behavior: Notifier state is volatile, reference-counted, and global within the kernel. It persists only while either connector or CEC adapter holds a reference. Physical address starts invalid and changes as HDMI/EDID state changes.

Dependencies and integration points: Depends on the Linux device model, kref/list/mutex primitives, platform and I2C OF lookup, DRM EDID helpers, public CEC notifier APIs, and adapter functions `cec_s_phys_addr()`/`cec_s_conn_info()`. Platform drivers use `cec_notifier_parse_hdmi_phandle()` for device-tree `hdmi-phandle` integration.

Risks and edge cases: Keying by raw `struct device *` plus optional port name requires providers and consumers to use exactly matching objects/names. The phandle helper drops the device reference because the device is used only as a key; misuse elsewhere would be unsafe. Probe deferral is expected when the HDMI device is not registered. Race protection uses both global and per-notifier locks; all adapter update paths must avoid lifetime cycles.

Test signals: Test adapter-before-connector and connector-before-adapter ordering, EDID physical-address changes, connector unregister invalidation, multi-port matching by port name, DT phandle probe deferral, I2C HDMI device lookup, and adapter-controlled physical-address drivers such as CH7322.
