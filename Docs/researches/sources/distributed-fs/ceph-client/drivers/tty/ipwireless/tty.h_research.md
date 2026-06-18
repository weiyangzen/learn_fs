# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.h

## Purpose
`tty.h` declares the IPWireless tty-layer interface for `main.c` and `network.c`. It keeps `struct ipw_tty` opaque while exposing global driver lifecycle, per-card tty creation/freeing, receive delivery, control-line notification, and modem-type queries.

## Important APIs, Types, And Functions
- `ipwireless_tty_init` and `ipwireless_tty_release` register/unregister the global `ttyIPWp` driver.
- `ipwireless_tty_create` creates modem, monitor, and raw tty objects for a card.
- `ipwireless_tty_free` removes tty objects associated with a card.
- `ipwireless_tty_received` delivers channel data into a tty flip buffer.
- `ipwireless_tty_is_modem` identifies the PPP modem tty.
- `ipwireless_tty_notify_control_line_change` updates line state and handles DCD drop behavior.

## Control Flow And State
The header has no control flow. `main.c` calls init/release and create/free. `network.c` calls receive delivery, modem detection, and control-line notification when routing channel events.

## State And Persistence Behavior
The tty object is opaque. Implementation state includes tty-port data, channel associations, line status, and transmit accounting. All state is runtime-only and tied to module or card lifetime.

## Dependencies And Integration Points
The header integrates userspace tty devices with the card channel router and PPP network path while hiding implementation details from callers.

## Risks And Edge Cases
Lifetime ordering matters: `ipwireless_tty_free` must run before `ipwireless_network_free` because tty cleanup disassociates network channel arrays. Receive delivery assumes the tty object remains valid for the call. Control-line notifications can trigger hangup.

## Test Signals
Build users against the declarations, create/free card ttys, deliver receive data while open and closed, route RAS data to PPP only for modem ttys, and verify DCD drop hangup behavior.
