# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.h

Purpose: `usbip_host_common.h` defines the generic exported-device backend abstraction for usbip daemon-side device providers.

Important types and APIs: `struct usbip_host_driver_ops` contains open/close/refresh/get and backend-specific read/filter callbacks. `struct usbip_host_driver` stores device count, exported list, subsystem name, and ops. `struct usbip_exported_device` combines a udev handle, status, USB metadata, list node, and flexible interface array. Inline wrappers call optional ops and return `-EOPNOTSUPP` or NULL when missing. Generic helper prototypes expose open/close/refresh/export/get behavior.

Control flow and integration: both `host_driver` and `device_driver` instantiate this abstraction. `usbipd` treats the selected backend uniformly for devlist and import handling.

State, dependencies, risks, and tests: it depends on libudev, list primitives, common USB structs, and sysfs helper declarations. Risks include flexible-array allocation mistakes, backend callbacks being optional in ways command code must tolerate, and the host-oriented naming obscuring device-mode behavior. Test signals are successful compilation of both backend implementations and daemon operation in default and `--device` modes.
