# sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.c

## Purpose
This is the USB serial driver for KLSI KL5KUSB105-based adapters, specifically the PalmConnect USB serial adapter. It exposes one serial port through the generic USB serial data path but adds device-specific control requests for port settings, read enablement, modem-line polling, and KLSI packet framing.

## Important APIs, Types, and Functions
`struct klsi_105_port_settings` is the five-byte settings payload sent to the device. `struct klsi_105_private` caches that settings payload, cached modem line state, and a spinlock. Important functions include `klsi_105_chg_port_settings`, `klsi_105_get_line_state`, `klsi_105_open`, `klsi_105_close`, `klsi_105_set_termios`, `klsi_105_tiocmget`, `klsi_105_prepare_write_buffer`, and `klsi_105_process_read_urb`.

The `usb_serial_driver` uses generic throttle/unthrottle/open data machinery but overrides packet preparation and read processing to add/remove a little-endian length header.

## Control Flow
Probe allocates and initializes private settings to 9600 8-bit defaults. Open sends a known default settings packet, calls `usb_serial_generic_open` to start generic URB handling, sends `KL5KUSB105A_SIO_CONFIGURE_READ_ON`, polls line state, and caches it. On failure after generic open, it sends READ_OFF and closes generic URBs. Close sends READ_OFF and then calls `usb_serial_generic_close`.

Writes are framed by `klsi_105_prepare_write_buffer`: it drains FIFO bytes after a two-byte little-endian count and returns header plus payload length. Reads are inverse-framed by `klsi_105_process_read_urb`: empty packets are ignored; packets shorter than the header are rejected; declared length is clamped to actual payload size before being pushed to TTY.

Termios handling maps supported baud rates to KLSI constants, supports only 7 or 8 data bits, strips unsupported parity/stop/flow settings, encodes the accepted baud back into termios, and sends the updated five-byte settings payload. `klsi_105_tiocmget` polls modem line state on demand and returns cached DSR/CTS bits.

## State and Persistence
The only persistent state is volatile per-port state in `klsi_105_private`: current settings and last line state. Device read enablement is toggled on open/close. There is no firmware load or file-backed state.

## Dependencies and Integration Points
This file depends on `kl5kusb105.h` for vendor IDs, request codes, baud constants, data-bit constants, and line-state masks. It integrates with USB serial generic open/close/read/write paths, TTY termios, unaligned little-endian helpers, and the TTY flip buffer.

## Risks
The protocol is reverse engineered and comments explicitly note uncertain modem-line mapping and missing handshaking support. `B0` handling is not implemented. Unsupported termios settings are silently cleared or ignored, which can surprise applications expecting parity, stop bits, or hardware/software flow control. Length-framed reads are robust to overlong declarations but still depend on correct packet framing from device firmware.

## Test Signals
Test open error unwind, READ_ON/READ_OFF sequencing, write header encoding, malformed short and mismatched read packets, baud mapping and fallback, 7/8 data-bit changes, clearing of unsupported termios flags, `TIOCMGET` line polling, and close/disconnect during generic URB activity.
