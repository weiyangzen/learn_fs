# sources/distributed-fs/ceph-client/drivers/usb/serial/wishbone-serial.c

## Purpose

`wishbone-serial.c` is a minimal usb-serial driver for the GSI Wishbone-Serial adapter. Its main device-specific job is to notify Etherbone firmware when a serial stream opens or closes so Wishbone negotiation and bus-cycle state are reset cleanly.

## Important APIs, Types, and Functions

The driver matches one vendor-specific interface using `USB_DEVICE_AND_INTERFACE_INFO(0x1D50, 0x6062, 0xFF, 0xFF, 0xFF)`. `usb_gsi_openclose()` sends vendor request `GSI_VENDOR_OPENCLOSE` to endpoint zero with `wValue` set to open or closed. `wishbone_serial_open()` issues the open notification before `usb_serial_generic_open()`, and unwinds by sending close if generic open fails. `wishbone_serial_close()` closes the generic stream then sends the close notification. `wishbone_serial_device` registers a single-port usb-serial driver.

## Control Flow

Probe and disconnect are handled by the usb-serial core. On tty open, the driver sends the vendor control request to the current interface number, then starts the generic bulk read/write path. On tty close, it stops the generic path and sends the close request so firmware can drop the Wishbone cycle line even if userspace did not do so.

## State and Persistence Behavior

The file stores no private driver state. The only state transition is firmware-side open/closed status communicated over control endpoint zero. No host-side persistence or cached configuration exists.

## Dependencies and Integration Points

It depends on usb-serial core, tty open/close callbacks, generic usb-serial data transport, and the device firmware's vendor-specific control request. Userspace sees a normal tty port; Etherbone/Wishbone-specific semantics remain inside the adapter firmware.

## Risks and Test Signals

Risks include treating any nonzero `usb_control_msg()` return as an error even though control helpers can return transferred lengths in some contexts, firmware dependence on the exact interface number, and leaving firmware marked open if close control transfer fails. Test signals include USB control traces on open/close, generic tty data transfer after open, failure injection for the open request, and close behavior after userspace exits without an orderly protocol shutdown.
