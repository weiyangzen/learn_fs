# sources/distributed-fs/ceph-client/include/uapi/linux/usb/raw_gadget.h

Purpose: Defines the USB Raw Gadget ioctl ABI for userspace to emulate a USB device directly on a UDC.

Important APIs/types/functions: `usb_raw_init` selects UDC driver/device name and speed. Event types report connect, control, suspend, resume, reset, and disconnect. `usb_raw_event` returns event data, with control events carrying `usb_ctrlrequest`. `usb_raw_ep_io` performs EP0 and endpoint reads/writes with flags such as zero packet. Endpoint info structs expose endpoint capabilities, limits, names, and addresses. Ioctls initialize, run, fetch events, EP0 read/write/stall, enable/disable endpoints, endpoint read/write, configure, set VBUS draw, query endpoint info, and set/clear halt or wedge.

Control flow: Userspace initializes a raw gadget, runs it, fetches events, responds to EP0 setup packets, enables endpoints using descriptors, configures the device, and services endpoint I/O synchronously through ioctls.

State and persistence behavior: Raw gadget state is tied to the open instance and selected UDC. Endpoint handles are valid while enabled and reset/disconnect events can invalidate assumptions.

Dependencies and integration points: Includes `asm/ioctl.h`, `linux/types.h`, and USB chapter 9. Integrates with UDC drivers, dummy_hcd/dummy_udc, fuzzing frameworks, and custom USB device emulators.

Risks: This ABI exposes low-level USB device behavior and is often used for fuzzing. EP0 direction must match the last setup packet. Endpoint descriptor/capability mismatches and reset/disconnect races are common failure points.

Test signals: Use dummy UDC to initialize/run, fetch connect/control/reset events, handle standard enumeration requests, enable bulk/interrupt endpoints, transfer data, query endpoint caps, and test halt/wedge/stall behavior.
