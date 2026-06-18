# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_detach.c

Purpose: `usbip_detach.c` implements `usbip detach`, removing an imported USB device from a local VHCI port.

Important functions: `detach_port()` validates that the `-p` argument contains only digits, opens the VHCI driver, confirms the port exists and is not already empty, removes `/var/run/vhci_hcd/portN`, attempts to remove the state directory, and writes the port to the VHCI `detach` sysfs attribute. `usbip_detach()` parses `-p`.

Control flow and integration: state-file removal happens before the kernel detach request. The driver list parsed during open is used to reject invalid ports and no-op empty ports.

State and dependencies: it mutates local VHCI kernel state and `/var/run/vhci_hcd`. It depends on root privileges and loaded `vhci_hcd`. Risks include removing the state file before a detach failure, `uint8_t` truncation of large port numbers after string validation, directory removal failing silently if other ports remain, and no synchronization with concurrent attach/detach. Test signals are `usbip detach -p N`, `usbip port` no longer showing the device, and `/var/run/vhci_hcd/portN` being removed.
