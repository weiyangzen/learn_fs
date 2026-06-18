<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/g_hid.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/g_hid.h

Purpose: defines the platform/config descriptor passed to the legacy USB HID gadget driver.

Important APIs and types: `struct hidg_func_descriptor` carries HID subclass, protocol, report length, report descriptor length, and flexible report descriptor bytes.

Control flow: board or gadget setup code supplies this descriptor; the HID gadget function uses it to expose the HID interface and report descriptor to the USB host and to size report I/O.

State and persistence: descriptor data is static gadget configuration. Runtime HID reports and endpoint state are owned by the HID gadget driver.

Dependencies and integration points: no explicit includes. It integrates legacy platform-data HID gadgets with USB composite/gadget HID implementation.

Risks and test signals: risks include report descriptor length mismatch, invalid HID report descriptors, and subclass/protocol values binding the wrong host driver behavior. Test HID gadget enumeration, descriptor reads, report send/receive lengths, and host compatibility for boot keyboard/mouse protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/g_hid.h -->
