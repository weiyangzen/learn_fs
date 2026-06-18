# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_port.c

Purpose: `usbip_port.c` implements `usbip port`, which displays devices currently imported into local VHCI ports.

Important functions: `list_imported_devices()` initializes usb.ids names, opens the VHCI driver, prints a heading, iterates all `vhci_driver->idev` entries, and delegates formatting to `usbip_vhci_imported_device_dump()`. `usbip_port_show()` is the command entry point.

Control flow and integration: the command is read-only except for tracefs/sysfs reads done by VHCI open/refresh. It uses `/var/run/vhci_hcd/portN` records indirectly through the dump helper to show remote host and busid information.

State and dependencies: transient state includes names database globals and VHCI parsed status. Dependencies are `vhci_hcd`, usb.ids, and readable state files for full remote mapping. Risks include failing the entire command on VHCI open failure, incomplete host details if state files are missing, and reliance on the global `vhci_driver`. Test signals are `usbip port` output after attach and graceful "available" handling for empty ports.
