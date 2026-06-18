# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa28msg.h

## Purpose
This header documents and defines the USA28/USA18/USA19 message format used by older Keyspan adapters. It supplies control and status structures for `keyspan.c` and documents how parity-aware data packets differ from the USA26-family framing.

## Important APIs, Types, and Constants
`struct keyspan_usa28_portControlMessage` carries baud selection (`setBaudRate`, `baudLo`, `baudHi`), always-sent parity/flow/modem-output fields, forwarding and break timing parameters, and action flags for TX/RX enable, flush, break, force-XOFF, status return, and data-toggle reset. `struct keyspan_usa28_portStatusMessage` reports port number, CTS/DSR/DCD/RI, TX-off/XOFF state, `dataLost`, RX enablement, break state, invalid RS-232 input, and control response.

`TX_OFF` and `TX_XOFF` document transmit state bits. `RX_PARITY_BIT` and `TX_PARITY_BIT` describe parity byte encoding for data streams, though the current driver mostly treats USA28 input as raw bytes and does not fully implement parity handling.

## Control Flow
`keyspan_usa28_send_setup` builds this control message on open, close, break, modem, and termios changes. It computes baud divisor bytes through the product's baud callback, sets RTS/DTR, sets CTS flow-control intent, uses fixed forwarding and break thresholds, and toggles the RX/TX action fields based on open or close mode. `usa28_instat_callback` consumes `keyspan_usa28_portStatusMessage` reports and updates modem-line cache and DCD hangup behavior.

## State and Persistence
The header is stateless. The driver keeps runtime settings in `keyspan_port_private` and serializes them into this structure for every setup message. Status reports update volatile cached modem state only.

## Dependencies and Integration Points
The sole direct integration is `keyspan.c`. The comments are also part of the integration contract with Keyspan firmware, describing the USB OUT request-ack prefix and parity/data alternation rules.

## Risks
The driver's current receive path does not fully implement the parity-data framing described here; parity mode may be less complete than the protocol allows. As with other Keyspan headers, macro names overlap with other included message headers, so maintainers must treat the include set as one coupled protocol namespace. Invalid packet sizes in status callbacks are dropped after debug logging.

## Test Signals
Test USA28 open/close setup serialization, baud divisor fallback, RTS/DTR and CTS-flow fields, status length validation, DCD transition hangup, data receive with normal and parity modes if hardware/firmware supports it, and control response behavior after reset-data-toggle requests.
