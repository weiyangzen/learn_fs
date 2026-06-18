# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.c

## Purpose
`tty.c` implements the user-visible tty side of the IPWireless driver. It registers the `ttyIPWp` driver, creates modem/monitor/raw tty devices per card, routes user writes to card channels, exposes PPP-related ioctls, manages modem-control lines, and tears down ttys during card removal.

## Important APIs, Types, And Functions
- `struct ipw_tty` wraps `tty_port`, minor index, hardware/network pointers, primary and secondary channel indices, tty type, cached control lines, mutex, and queued TX byte count.
- Minor layout uses 24 minors in three 8-minor ranges: modem, monitor, and optional RAS-raw.
- `ipw_open`, `ipw_close`, and `ipw_hangup` manage open count, `driver_data`, and PPP open/close for modem ttys.
- `ipw_write`, `ipw_write_room`, and `ipw_chars_in_buffer` implement transmit queue accounting.
- `ipwireless_tty_received` inserts hardware data into the tty flip buffer.
- `ipw_ioctl` supports PPP channel/unit queries, `FIONREAD`, and `TCFLSH`.
- Modem-control helpers map Linux `TIOCM_*` bits to hardware RTS/DTR/CTS/DSR/DCD state.
- `ipwireless_tty_create/free/init/release` manage per-card devices and the global tty driver.

## Control Flow And State
Module initialization registers a dynamic raw `ttyIPWp` driver. Card setup finds a free minor slot and registers a modem tty associated with dialler and RAS, a monitor tty associated with dialler, and a RAS-raw tty associated with RAS. `get_tty` hides raw RAS devices unless `loopback` is enabled.

Opening the modem tty schedules PPP open; final close or hangup schedules PPP close. Writes are serialized by `ipw_tty_mutex`, clipped to remaining transmit queue space, sent to hardware on the RAS channel, and accounted down by the send callback. Control-line changes update cached bits and hang up the tty when DCD drops.

## State And Persistence Behavior
Global `ttys[24]` stores active per-minor tty objects, and `ipw_tty_driver` stores the registered driver. Per-tty state includes open count, port tty pointer, queued byte count, cached line state, and channel associations. All state is runtime-only.

## Dependencies And Integration Points
The file depends on Linux tty core, tty flip buffers, serial/PPP ioctls, mutexes, user access helpers, and local hardware/network APIs. It bridges userspace `ttyIPWp*` nodes to PPP and card channels.

## Risks And Edge Cases
Source comments call out uncertain tty locking around write-room, modem-control ioctls, and teardown versus parallel ioctls. The send callback updates `tx_bytes_queued` without taking `ipw_tty_mutex`. `secondary_channel_idx` is unsigned but uses `-1` as a sentinel. If `ipwireless_tty_create` fails after creating earlier ttys, it does not roll them back locally.

## Test Signals
Verify modem/monitor device registration and raw RAS visibility with `loopback=1`. Open/close modem tty and confirm PPP channel lifecycle. Write near queue capacity, toggle RTS/DTR, drop DCD for hangup, and remove the card with open ttys.
