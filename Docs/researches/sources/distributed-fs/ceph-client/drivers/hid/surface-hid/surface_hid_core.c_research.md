# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.c

Purpose: shared HID low-level driver for Surface SSAM HID transports.

Important APIs: `surface_hid_device_add()` loads descriptors/attributes, allocates `hid_device`, fills bus/vendor/product/version/name/phys and registers it. `surface_hid_device_destroy()` destroys it. `surface_hid_pm_ops` forwards PM events to HID driver callbacks.

Control flow: load HID descriptor, validate type/count/report descriptor metadata, load attributes, allocate HID device, attach `surface_hid_ll_driver`, and call `hid_add_device()`. HID `.start` registers SSAM notifier; `.stop` unregisters unless hot-removed; `.parse` fetches report descriptor and calls `hid_parse_report()`; `.raw_request` dispatches output/get feature/set feature through transport ops.

State and persistence: descriptor and attribute copies live in `struct surface_hid_device`; the HID core owns the registered `hid_device`. Hot-remove state is queried from SSAM devices before control requests.

Dependencies and integration: depends on HID core, USB HID descriptor constants, and Surface Aggregator controller/device helpers. Frontend transports provide descriptor/report operations and event notifiers.

Risks: core assumes exactly one report descriptor and validates fixed descriptor sizes. `surface_hid_device_destroy()` assumes `shid->hid` was either added or is destroyable. PM callbacks require driver data to be set by the frontend.

Test signals: descriptor protocol tests, `hid_add_device()` probe path, notifier registration/unregistration, raw report request results, hot-remove behavior, and PM callback forwarding.
