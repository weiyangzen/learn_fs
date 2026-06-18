# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.c

Purpose: `usbip_host_common.c` implements generic exported-device enumeration and export operations shared by physical host and vUDC backends.

Important functions: `read_attr_usbip_status()` reads a device's `usbip_status` sysfs attribute. `usbip_exported_device_new()` builds a `struct usbip_exported_device`, invokes backend-specific device/interface readers, reallocates for interface records, and reads status. `refresh_exported_devices()` enumerates a backend subsystem through libudev and filters with `is_my_device()`. `usbip_generic_driver_open()`, `usbip_generic_driver_close()`, and `usbip_generic_refresh_device_list()` manage udev context and the exported list. `usbip_export_device()` writes a connected socket descriptor to `usbip_sockfd`. `usbip_generic_get_device()` indexes the list.

Control flow and integration: `host_driver` and `device_driver` use these functions through `struct usbip_host_driver_ops`. `usbipd` refreshes the list before each PDU and calls `usbip_export_device()` on import requests.

State and dependencies: state is a linked list of heap-allocated exported devices and a global libudev context. Persistent kernel state changes when `usbip_sockfd` receives the daemon's accepted connection fd. Risks include missing NULL checks after `calloc`, potential udev refs not being unreffed for enumeration temp devices, short status reads, and race windows between status enumeration and export. Test signals are accurate devlist contents, correct busy/error status handling, and kernel takeover of the socket after import.
