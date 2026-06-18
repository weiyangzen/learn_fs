# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_list.c

Purpose: `usbip_list.c` implements `usbip list`, covering remote exportable devices, local physical USB devices, and local vUDC gadget devices.

Important functions: `get_exported_devices()` sends `OP_REQ_DEVLIST`, receives device/interface records, unpacks them, and prints names/classes. `list_exported_devices()` handles TCP connect. `list_devices()` enumerates non-hub USB devices through libudev, skips devices under `vhci_hcd`, and prints busid/vendor/product. `list_gadget_devices()` scans platform devices bound to `usbip-vudc`, reads the binary descriptor sysattr, and prints gadget identity. `usbip_list()` parses `-p`, `-r`, `-l`, and `-d` and initializes usb.ids names.

Control flow and integration: only one listing mode is executed per invocation. Remote mode uses the usbip daemon protocol; local modes read sysfs directly.

State and dependencies: state is transient libudev enumeration, TCP sockets, and names database globals. Dependencies include usb.ids, libudev, network protocol helpers, and Linux descriptor layout. Risks include a likely typo assigning `idProduct_buf` from `idVendor`, not unrefing skipped udev devices in all paths, strict remote PDU sequencing, and parsable mode printing only partial metadata. Test signals are useful output for `usbip list -l`, `usbip list -d`, `usbip list -r HOST`, and named products/classes when usb.ids is present.
