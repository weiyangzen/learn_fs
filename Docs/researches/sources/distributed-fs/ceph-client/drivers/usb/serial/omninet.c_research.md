# sources/distributed-fs/ceph-client/drivers/usb/serial/omninet.c

## Purpose

`omninet.c` is a Linux usb-serial protocol driver for ZyXEL omni.net USB terminal adapters and a rebranded BT IgnitionPro device. The hardware uses fixed 64-byte host frames with a four-byte control header, so the driver adapts usb-serial generic buffering to that packet format.

## Important APIs, Types, And Functions

The file defines `struct omninet_header` for the four-byte protocol header (`oh_seq`, `oh_len`, `oh_xxx`, `oh_pad`) and `struct omninet_data` for the transmit sequence counter. Constants define header length, fixed bulk-out frame size, and maximum payload size. The USB driver callbacks are `omninet_calc_num_ports()`, `omninet_port_probe()`, `omninet_port_remove()`, `omninet_process_read_urb()`, and `omninet_prepare_write_buffer()`.

The registered `usb_serial_driver` uses two bulk-out endpoints in descriptors but remaps to a single logical port and a single selected bulk-out endpoint.

## Control Flow

During port-count calculation, `omninet_calc_num_ports()` selects the second bulk-out endpoint for the one logical port and reduces `num_bulk_out` to one. Port probe allocates `struct omninet_data` and stores it as private port data; remove frees it.

Receive processing expects a device frame beginning with `struct omninet_header`. If the URB length does not exceed the header or the header length is zero, it drops the frame. Otherwise it copies at most the lesser of available bytes after the header and `oh_len` into the tty flip buffer and pushes it.

Transmit preparation always returns `64` so the generic write path sends fixed-size frames. It limits payload to 60 bytes, drains bytes from the tty write FIFO into the frame after the header, increments the per-port sequence byte, writes the payload length, sets `oh_xxx` to `0x03`, and clears the pad byte.

## State And Persistence

State is limited to the in-memory `od_outseq` sequence counter stored per port. There is no hardware register mirror, firmware, persistent storage, or modem-control cache. All buffering outside that counter is handled by the usb-serial generic FIFO and URB infrastructure.

## Dependencies And Integration Points

The driver depends on the usb-serial core's generic read/write machinery, tty flip buffers, kfifo write buffering, and USB ID matching. It does not implement custom open, close, termios, modem-control, or ioctl handlers. User-space sees a one-port tty whose packets are translated to and from omni.net's fixed-size frame format.

## Risks And Edge Cases

Because transmitted frames are always 64 bytes, the buffer passed to `omninet_prepare_write_buffer()` must be sized accordingly by the usb-serial core. The protocol fields beyond length and sequence are only partially understood; `oh_xxx` is hard-coded to `0x03`. Receive drops short or zero-length frames silently. Sequence counter wrap is natural for `u8` and not checked. Endpoint remapping assumes the second bulk-out endpoint is present.

## Test Signals

Test enumeration for each supported USB ID, endpoint remapping to the second bulk-out endpoint, transmit framing at 0, 1, 60, and larger-than-60 byte writes, sequence increment and wrap, receive frames with valid header length, truncated payloads, short headers, zero `oh_len`, disconnect during generic IO, and compatibility with generic termios defaults.
