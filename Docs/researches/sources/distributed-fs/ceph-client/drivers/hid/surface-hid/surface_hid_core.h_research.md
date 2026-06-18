# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_hid_core.h

Purpose: shared declarations for Surface SSAM HID transports.

Important APIs/types: descriptor entry enum identifies HID descriptor, report descriptor, and attributes. Packed descriptor structs model the SSAM-provided HID metadata. `struct surface_hid_device_ops` abstracts transport operations. `struct surface_hid_device` carries device/controller UID, descriptor data, notifier, HID device pointer, and ops.

Control flow: frontend drivers populate the structure and call `surface_hid_device_add()`; the core calls ops during parse/raw request/start/stop.

State and persistence: all per-device transport and HID registration state is centralized here.

Dependencies and integration: includes Linux HID/PM types and Surface Aggregator controller/device APIs.

Risks: packed descriptor layouts are enforced with `static_assert`; any firmware protocol change requires header updates and validation.

Test signals: compile-time size assertions and successful generic plus legacy transport probing.
