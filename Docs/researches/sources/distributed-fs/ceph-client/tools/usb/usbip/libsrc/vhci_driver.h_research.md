# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.h

Purpose: `vhci_driver.h` declares the client-side VHCI control API and data structures.

Important types and APIs: `enum hub_speed` distinguishes high-speed and super-speed hubs. `struct usbip_imported_device` stores hub type, port, status, remote devid/bus/dev numbers, and local USB metadata. `struct usbip_vhci_driver` owns the udev handle, controller count, port count, and flexible imported-device array. APIs open/close/refresh the driver, find a free port, attach by devid or bus/dev, detach, and dump imported devices.

Control flow and integration: `usbip_attach.c`, `usbip_detach.c`, and `usbip_port.c` include this header to manipulate the local virtual host controller.

State, dependencies, risks, and tests: the header exposes the global `vhci_driver`, coupling callers to open-before-use ordering. It depends on libudev and common USB metadata. Risks include callers dereferencing the global after failed open and deprecated `usbip_vhci_attach_device()` still present. Test signals are successful compile/link of attach/detach/port and runtime behavior across high-speed and super-speed devices.
