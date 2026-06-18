# sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.c

## Purpose
This driver supports Magic Control Technology USB-RS232 converters and compatible Sitecom, D-Link, and Belkin devices. It exposes one serial port, programs UART-like settings through vendor control requests, reads data through a second interrupt-in endpoint workaround, tracks modem status changes, and implements TTY modem, break, throttle, and termios operations.

## Important APIs, Types, and Functions
`struct mct_u232_private` stores the special read URB, spinlock, cached modem control state, last LCR/LSR/MSR, and RX throttle flags. Key functions include `mct_u232_calculate_baud_rate`, `mct_u232_set_baud_rate`, `mct_u232_set_line_ctrl`, `mct_u232_set_modem_ctrl`, `mct_u232_get_modem_stat`, `mct_u232_msr_to_icount`, `mct_u232_msr_to_state`, `mct_u232_open`, `mct_u232_close`, `mct_u232_read_int_callback`, `mct_u232_set_termios`, `mct_u232_break_ctl`, `mct_u232_tiocmget`, `mct_u232_tiocmset`, `mct_u232_throttle`, and `mct_u232_unthrottle`.

## Control Flow
Probe validates the expected second interrupt-in endpoint, stores that URB as the data-read URB, and points its context at the primary port. Open adjusts Sitecom bulk-out size, initializes DTR/RTS according to baud state, programs modem control and 8N1 line control, polls current modem status, submits the special read URB, and also submits the normal interrupt-in URB for status. Close kills both URBs and delegates to generic close.

Baud setting converts Linux speed to either a divisor (`115200 / baud`) or product-specific code for Sitecom/Belkin variants, sends `MCT_U232_SET_BAUD_RATE_REQUEST`, then sends two extra vendor requests mirroring the Windows driver: an unknown zero-byte request and a CTS gating request based on `CRTSCTS`. Termios updates baud, handles B0 by dropping or reasserting DTR/RTS, maps parity/data/stop to LCR bits, clears mark/space parity, sends line control, and caches state.

The read interrupt callback handles two kinds of URBs. When the transfer buffer length is greater than two, it treats the packet as bulk-like data and pushes it to TTY. Otherwise, it treats data[0] as MSR and data[1] as LSR, updates cached modem state and icount deltas, wakes modem-status waiters, and resubmits. LSR error handling is present only in disabled code.

## State and Persistence
Per-port volatile state includes control lines, last LCR/MSR/LSR, throttle state, and the selected special read URB. Device register state persists in hardware until changed or unplugged. No file-backed state exists.

## Dependencies and Integration Points
This file depends on `mct_u232.h`, Linux USB serial core, generic modem wait/count helpers, TTY termios, unaligned little-endian helpers, and spinlocks. It integrates with user-space through normal serial data, `TIOCMGET`/`TIOCMSET`, `TIOCMIWAIT`, `get_icount`, break control, and hardware-flow-control behavior.

## Risks
The hardware protocol is reverse engineered and includes unknown requests. The second endpoint workaround assumes `serial->port[1]->interrupt_in_urb` exists and remains valid for the primary port. LSR error reporting is not implemented, so parity/framing/break errors may be invisible. Throttle only drops RTS when CRTSCTS is enabled; non-RTS flow control is not implemented. Product-specific baud coding is subtle and could regress compatible devices.

## Test Signals
Test all USB IDs, endpoint validation failure, Sitecom 16-byte bulk-out quirk, baud mappings for regular and Sitecom/Belkin devices, B0 DTR/RTS behavior, CTS gating request with and without CRTSCTS, MSR-to-icount updates, `TIOCMIWAIT`, data URB versus status URB parsing, throttle/unthrottle RTS changes, and break LCR programming.
