# sources/distributed-fs/ceph-client/drivers/usb/serial/usb-serial.c

## Purpose
`usb-serial.c` is the USB serial core. It registers the ttyUSB major, manages dynamic minor allocation, discovers and binds USB serial subdrivers, allocates per-port devices and URBs, bridges TTY operations to subdriver callbacks, handles disconnect and PM, and provides registration APIs used by every USB serial module.

## Important APIs, Types, and Functions
Global state includes `serial_minors` IDR, `table_lock`, and `usb_serial_driver_list`. Exported APIs include `usb_serial_port_get_by_minor()`, `usb_serial_claim_interface()`, `usb_serial_put()`, `usb_serial_port_softint()`, `usb_serial_suspend()`, `usb_serial_resume()`, `__usb_serial_register_drivers()`, and `usb_serial_deregister_drivers()`. Core functions cover tty install/open/close/write/ioctl/termios, endpoint discovery/setup, probe/disconnect, PM reset resume, driver registration, and fallback operation initialization.

## Control Flow, State, and Persistence
Initialization allocates a 512-minor tty driver on major 188, registers the USB serial bus, installs tty operations, registers the generic driver, and exposes ttyUSB devices dynamically. During probe, the core finds the matching serial subdriver under `table_lock`, creates `struct usb_serial`, calls subdriver probe, gathers endpoints from the primary and optional sibling interface, validates endpoint requirements, calculates port count, allocates `usb_serial_port` devices, allocates read/write/interrupt URBs and buffers, calls attach, reserves tty minors with IDR, and registers each `ttyUSBn` device. TTY install looks up by minor, takes a serial reference and module reference, sets initial termios, and stores `driver_data`. Open/close route through `tty_port_open()` with runtime PM around subdriver open/close. Writes, modem control, termios, throttling, and ioctls dispatch to `serial->type` callbacks with generic fallbacks if the subdriver did not provide them.

Disconnect marks the serial disconnected under `disc_mutex`, vhangs tty ports, poisons URBs, wakes waiters, removes device nodes, calls subdriver disconnect, releases sibling interfaces, and drops the serial reference. Suspend invokes subdriver suspend once across sibling interfaces and poisons URBs; resume unpoisons and invokes subdriver resume or generic resume. Lifetime is kref-based; `destroy_serial()` releases minors, calls subdriver release, drops interface/device references, and frees ports when their device refs reach zero.

State is in kernel memory only: IDR minor map, registered-driver list, krefs, port devices, tty state, URBs, FIFOs, and PM counters. There is no on-disk persistence.

## Dependencies and Integration Points
The file integrates Linux USB core, TTY core, device model, IDR, kfifo, module ownership, USB serial bus code, generic USB serial helpers, and optional console support. Subdrivers depend on `__usb_serial_register_drivers()` via the `module_usb_serial_driver()` macro and on generic callbacks installed by `usb_serial_operations_init()`.

## Risks and Test Signals
Risks include lifetime races among disconnect, tty cleanup, URB callbacks, and module unload; endpoint-to-port mapping mistakes; sibling-interface ownership; PM suspend counts across sibling interfaces; and dynamic-ID probe ordering. Test signals include binding/unbinding multiple subdrivers, minor exhaustion/unwind, hot unplug during open/write, module unload with active ttys, suspend/resume and reset-resume paths, missing endpoint rejection, generic fallback callback behavior, and `/proc` `usbserinfo` output.
