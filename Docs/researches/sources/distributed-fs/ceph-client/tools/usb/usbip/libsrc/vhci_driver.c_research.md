# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.c

Purpose: `vhci_driver.c` is the client-side library for controlling the local `vhci_hcd` virtual host controller. It discovers ports, parses imported-device status, attaches sockets to ports, detaches ports, and prints imported-device records.

Important functions: `usbip_vhci_driver_open()` creates a udev context, finds platform device `vhci_hcd.0`, reads `nports`, counts controllers, allocates `vhci_driver`, and refreshes imported devices. `parse_status()` parses `status` and `status.N` sysfs text into `struct usbip_imported_device` entries. `usbip_vhci_get_free_port()` selects a high/super-speed-compatible free port. `usbip_vhci_attach_device2()` writes `port sockfd devid speed` to `attach`; `usbip_vhci_detach_device()` writes a port to `detach`. `read_record()` reads `/var/run/vhci_hcd/portN`, and `usbip_vhci_imported_device_dump()` formats port ownership.

Control flow and integration: `usbip attach` opens this driver after receiving a remote import reply, attaches the connected TCP socket to a free VHCI port, then records host/port/busid in `/var/run/vhci_hcd`. `usbip detach` and `usbip port` use the same parsed status.

State and dependencies: state includes global `vhci_driver`, global `udev_context`, kernel sysfs attributes, and persistent `/var/run/vhci_hcd/portN` files. Risks include global context conflicts, strict parsing of kernel status format, status arrays indexed by parsed port, no locking around state files, and attach/detach requiring root and loaded modules. Test signals are `usbip attach`, `usbip port`, valid `/var/run/vhci_hcd/portN`, and correct detach cleanup.
