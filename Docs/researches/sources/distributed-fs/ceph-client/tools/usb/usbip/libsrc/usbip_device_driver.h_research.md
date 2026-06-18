# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.h

Purpose: this header exports the vUDC/device-mode usbip driver backend.

Important API: `extern struct usbip_host_driver device_driver;` exposes a backend compatible with the generic `usbip_host_driver` interface even though it enumerates UDC devices rather than host USB devices.

Control flow and integration: `usbipd.c` switches its global `driver` pointer to `&device_driver` when invoked with `--device`, reusing the same daemon protocol handlers for virtual device export.

State, dependencies, risks, and tests: the header pulls in common USB metadata, host common backend types, and list support. Risks are semantic confusion from using `usbip_host_driver` names for device-mode operation. Test signals are compile-time visibility to `usbipd.c` and successful runtime selection with `usbipd --device`.
