# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa67msg.h

## Purpose
This header defines the USA67 message format used for USA28XG-style two-port Keyspan devices running FX1 firmware. It resembles the USA26 protocol but adds an explicit port field to the control message and uses a global control endpoint for multi-port setup.

## Important APIs, Types, and Constants
`keyspan_usa67_portControlMessage` includes `port`, clocking/baud/prescaler fields, LCR, flow control, RTS/DTR-compatible outputs, forwarding and loopback fields, and TX/RX action flags. `keyspan_usa67_portStatusMessage` reports port number, CTS-like and DCD-like pins, TX state, TX ACK, RX enabled, and control response. Global control/status/debug typedefs support status-toggle messages. The LCR and RX error constants mirror the USA26-family definitions.

## Control Flow
`keyspan_usa67_send_setup` serializes this control structure to the device's global control URB. It sets `port` from the TTY port number, recomputes baud when needed, maps Linux termios to LCR bits, sets flow and XON/XOFF defaults, and uses open/close/intermediate reset modes to control TX/RX and data-toggle reset. `usa67_instat_callback` parses port status reports and updates cached CTS and DCD; `usa67_glocont_callback` scans all ports for pending setup resends after global control completion.

## State and Persistence
This file is a stateless protocol definition. Firmware may maintain port enablement, clocking, and status cadence based on messages, while Linux caches desired state in `keyspan_port_private` and resends when necessary.

## Dependencies and Integration Points
It is consumed by `keyspan.c` for products whose `keyspan_device_details.msg_format` is `msg_usa67`, currently USA28XG. It depends on the driver using the same endpoint mapping and message size expected by FX1 firmware.

## Risks
The status structure reports fewer modem lines than other formats, so DSR/RI are unavailable in `keyspan.c` for USA67 devices. Shared global control creates the same ordering risk as USA49: a busy control URB can defer setup from another port. RX error constants include break, but receive code does not fully surface break as a TTY break event.

## Test Signals
Validate two-port setup serialization, per-port `port` selection, baud/prescaler fallback, status report parsing, DCD hangup behavior, endpoint mapping for USA28XG, open/close reset-data-toggle, and concurrent setup resend across both ports.
