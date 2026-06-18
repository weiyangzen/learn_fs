# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa49msg.h

## Purpose
This header defines the USA49W four-port Keyspan global-control/global-status protocol. Unlike the per-port control endpoints used by some smaller adapters, USA49 messages put a port selector in the payload and send control over a global endpoint or, for USA49WG, endpoint zero.

## Important APIs, Types, and Constants
`struct keyspan_usa49_portControlMessage` begins with `portNumber` and includes clocking, baud divisor/prescaler, LCR, flow control, XON/XOFF characters, RTS/DTR setters, forwarding, loopback, TX/RX action flags, reset-data-toggle, and explicit `enablePort`/`disablePort`. `struct keyspan_usa49_globalControlMessage` controls global status behavior and remote wakeup. `struct keyspan_usa49_portStatusMessage` reports per-port modem pins, TX state, RX enabled state, control response, TX ACK, and RS-232 validity. Global status and debug structs identify non-port messages with `portNumber` values `0x80` and `0x81`.

## Control Flow
`keyspan_usa49_send_setup` fills the port-control message, sets `portNumber` from `port->port_number`, and sends it through `s_priv->glocont_urb`. For USA49WG it wraps the payload in a vendor control request on endpoint zero; for USA49W/USA49WLC it writes to the configured global control endpoint. `usa49_instat_callback` consumes `keyspan_usa49_portStatusMessage`; `usa49_glocont_callback` scans ports for pending `resend_cont` when a global control URB completes.

## State and Persistence
The header declares wire state only. Runtime enablement, modem line cache, baud cache, break state, and resend state live in `keyspan.c`. Status-suppression fields in the protocol imply firmware-side persistence until a later host control message, but the Linux driver does not expose a high-level persistent status policy.

## Dependencies and Integration Points
This header is included by `keyspan.c` and depends on `u8`. It is tightly coupled to the four-port endpoint maps in `keyspan_device_details`, especially the USA49WG special case with aggregate data input and endpoint-zero control.

## Risks
Global-control serialization means one URB is shared by all four ports; concurrent port reconfiguration can be delayed or coalesced through `resend_cont`. The protocol can suppress status messages, so incorrect use of global control could hide modem-line changes. The aggregate USA49WG path depends on the same status/error constants but parses data differently from ordinary USA49W devices.

## Test Signals
Test all four ports for independent open/close, DTR/RTS, baud, break, and receive paths; stress concurrent termios changes across ports; validate USA49WG endpoint-zero setup; verify global status reports by port number; exercise enable/disable status after close/open; and confirm TX ACK or busy resend behavior does not starve later ports.
