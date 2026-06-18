# sources/distributed-fs/ceph-client/drivers/usb/serial/navman.c

## Purpose

`navman.c` is a minimal USB serial driver for read-only Navman/Talon Technology and Mobile Action i-gotU style devices. It exposes one tty port, receives data from an interrupt-in endpoint, and intentionally rejects writes because the supported device class is receive-only.

## Important APIs, Types, And Functions

The driver has no private data structure. It defines a USB ID table for `0x0a99:0x0001` and `0x0df7:0x0900`, then registers one `struct usb_serial_driver` named `navman`. The relevant callbacks are `navman_open()`, `navman_close()`, `navman_write()`, and `navman_read_int_callback()`.

`navman_read_int_callback()` is the only data path. It receives the interrupt URB, handles normal shutdown statuses, logs unexpected statuses, inserts non-empty payloads into the tty flip buffer, and resubmits the interrupt URB with `GFP_ATOMIC`.

## Control Flow

When a tty is opened, `navman_open()` submits `port->interrupt_in_urb` if the endpoint exists. Each interrupt completion pushes data to the tty layer and resubmits itself, keeping a continuous interrupt polling loop alive until close or shutdown. `navman_close()` kills the interrupt URB. Any tty write calls return `-EOPNOTSUPP`.

## State And Persistence

There is effectively no driver-owned persistent state beyond the usb-serial core's port and URB objects. No private allocation, register mirror, firmware, filesystem persistence, or cached modem status exists. Runtime state is the submitted or killed interrupt URB.

## Dependencies And Integration Points

The file integrates with the USB core, usb-serial framework, tty flip buffer API, and module USB serial registration. User integration is a one-port tty device that can be read but not written. A source comment notes a missing future termios method that would suppress echo flags for the receive-only device.

## Risks And Edge Cases

The driver assumes interrupt payloads are directly tty data. Unexpected URB statuses are logged and resubmitted except for normal teardown statuses. If a device lacks an interrupt-in URB, open succeeds with no submitted receive path because `result` remains zero. Writes are not supported, so user programs expecting full serial semantics must tolerate `-EOPNOTSUPP`.

## Test Signals

Test binding against both USB IDs, open/close URB submit and kill, receive delivery through the interrupt endpoint, zero-length interrupt packets, unexpected interrupt URB status resubmission, disconnect while open, and user-space writes returning `-EOPNOTSUPP`.
