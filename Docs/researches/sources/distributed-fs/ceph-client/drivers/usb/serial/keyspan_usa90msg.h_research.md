# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa90msg.h

## Purpose
This header defines the USA90 protocol used by the high-speed Keyspan USA19HS path. It supports explicit RX/TX modes, richer flow-control bitmaps, status counters, and a 64-byte raw data mode used by `keyspan.c` at higher baud rates.

## Important APIs, Types, and Constants
`struct keyspan_usa90_portControlMessage` contains setters and values for baud clocking, LCR, RX/TX mode, TX/RX flow control, XON/XOFF and immediate character transmission, RTS/DTR, forwarding thresholds, TX ACK policy, port enablement, flush/break/loopback state, RX flush/forward, XOFF cancellation, and status return. `struct keyspan_usa90_portStatusMessage` reports MSR-like state, CTS/DCD/DSR/RI, XOFF, break, overrun/parity/frame counters, port state, ACKs, and control response.

Constants define LCR bits, TX/RX flow-control masks, DMA/by-hand modes, RX error bits, port-state bits, and MSR bits. `RXMODE_DMA` and `TXMODE_DMA` are especially important because `keyspan_usa90_send_setup` selects DMA above 57600 baud and `usa90_indat_callback` changes receive parsing based on the cached baud.

## Control Flow
The driver uses `keyspan_usa90_send_setup` for USA19HS setup. On baud change it computes divisor bytes, sets RX/TX mode setters, and falls back to 9600 on invalid baud. Every setup message supplies the mode matching the cached baud, LCR when changed, flow-control fields, forwarding defaults, port enablement, break state, and RTS/DTR values. `usa90_instat_callback` updates modem-line cache from `keyspan_usa90_portStatusMessage` and treats the adapter as single-port.

## State and Persistence
The header stores no state itself. Runtime mode selection depends on `p_priv->baud`, so stale baud state would cause mismatched data parsing. Firmware-side counters for RX errors are reported in status messages, but the current driver primarily updates modem lines and does not expose all counters.

## Dependencies and Integration Points
It integrates only through `keyspan.c` and the USA19HS device metadata. The protocol is tied to the high-speed product's different endpoint layout with no input-ack endpoint and no endpoint flipping.

## Risks
Data parsing changes at the 57600 threshold; if the device and driver disagree about mode, RX bytes can be interpreted incorrectly. Several status fields and error counters are defined but underused, reducing observability for parity/framing/break diagnostics. The macro `USA_USA_MSR_RI` appears oddly named and must not be confused with generic MSR naming in other drivers.

## Test Signals
Test baud transitions around 57600, raw DMA receive versus by-hand status/data receive, invalid baud fallback, DTR/RTS and CTS flow-control fields, port enable/disable on open/close, break assertion, status-length tolerance, and disconnect during active out-control URB submission.
