# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/dbgp.c

## Purpose

`dbgp.c` implements the standalone EHCI Debug Port gadget `g_dbgp`. It is not a libcomposite gadget; it registers a raw `usb_gadget_driver` that responds to debug descriptors and enters debug mode through a standard SET_FEATURE request.

## Important APIs, Types, and Functions

Global `struct dbgp` stores the gadget, EP0 request, IN/OUT endpoints, and optional `gserial` state. Important functions are `dbgp_bind()`, `dbgp_unbind()`, `dbgp_setup()`, `dbgp_disconnect()`, `dbgp_configure_endpoints()`, and module init/exit. In `CONFIG_USB_G_DBGP_PRINTK` mode, `dbgp_enable_ep()`, `dbgp_enable_ep_req()`, `dbgp_complete()`, and `dbgp_consume()` receive OUT data and print it. In serial mode, `gserial_connect()` and `gserial_disconnect()` bridge endpoints to TTY.

## Control Flow

Init registers the gadget driver. Bind allocates an EP0 request buffer, optional serial object and tty line, autoconfigures two 8-byte bulk debug endpoints, and fills the USB debug descriptor. EP0 setup handles `GET_DESCRIPTOR` for device and debug descriptors and `SET_FEATURE USB_DEVICE_DEBUG_MODE`, which either enables printk receive requests or connects the serial function. Disconnect disables endpoints or disconnects serial; unbind frees EP0 and optional serial state.

## State and Persistence Behavior

The singleton `dbgp` object holds all runtime state. Endpoint descriptors are static but have endpoint addresses and max-packet values filled during autoconfiguration. Printk mode owns one queued OUT request at a time. Serial mode owns a tty line until module exit. Nothing is persisted.

## Dependencies and Integration Points

The file depends on low-level gadget APIs, Chapter 9 descriptors, optional `u_serial`, and EHCI debug-device semantics. It bypasses libcomposite because the debug device has specialized enumeration behavior.

## Risks and Test Signals

Risks include singleton assumptions, modifying the const control request length for oversized IN descriptors, endpoint enable/disable ordering, request lifetime in printk completion, and serial-line allocation/free balance. Tests should request device/debug descriptors, issue debug-mode SET_FEATURE, stream data in printk and serial modes, disconnect/reset repeatedly, verify endpoint max packet is 8, and unload after active debug traffic.
