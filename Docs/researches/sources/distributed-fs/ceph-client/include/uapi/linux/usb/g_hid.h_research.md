# sources/distributed-fs/ceph-client/include/uapi/linux/usb/g_hid.h

Purpose: Defines platform/configuration data for the USB HID gadget function.

Important APIs/types/functions: `struct hidg_func_descriptor` carries subclass, protocol, report length, report descriptor length, and pointer to report descriptor data.

Control flow: Gadget setup code supplies this descriptor to instantiate a HID function. The gadget exposes HID descriptors and endpoints according to the report descriptor and report length.

State and persistence behavior: Descriptor data defines static gadget capabilities for the lifetime of the configured function. HID runtime state depends on host traffic and gadget implementation.

Dependencies and integration points: Integrates with USB gadget HID function, configfs/platform gadget setup, HID class drivers, and host input stacks.

Risks: Pointer field is unsuitable as a stable cross-process wire ABI and is mainly for in-kernel/platform setup. Report length must match descriptor semantics to avoid truncated or stalled reports.

Test signals: Instantiate HID gadget with keyboard/mouse/custom descriptors, enumerate on a host, validate report descriptor and report I/O lengths, and test invalid descriptor sizes.
