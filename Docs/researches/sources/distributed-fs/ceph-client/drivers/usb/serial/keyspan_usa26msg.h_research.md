# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa26msg.h

## Purpose
This header defines the Keyspan USA26/USA28X-style async message protocol consumed by `keyspan.c`. It is a wire-format contract for host-to-device port control messages, device-to-host status messages, and RX/TX data framing. It has no executable code but directly determines how setup messages and receive parsers interpret bytes.

## Important APIs, Types, and Constants
`struct keyspan_usa26_portControlMessage` contains requested configuration fields (`setClocking`, baud bytes, external/rx clocking, `setLcr`, LCR bits, flow-control flags, RTS/DTR-compatible outputs, prescaler) and action fields (`_txOn`, `_txOff`, `txFlush`, `txBreak`, `rxOn`, `rxOff`, `rxFlush`, `rxForward`, `returnStatus`, `resetDataToggle`). `struct keyspan_usa26_portStatusMessage` reports port number, CTS-like and DCD-like pins, DSR, RI, TX state, RX enablement, and control-response status.

LCR constants encode data bits, stop bits, and parity. RX error bits (`RXERROR_OVERRUN`, `RXERROR_PARITY`, `RXERROR_FRAMING`, `RXERROR_BREAK`) are shared with `keyspan.c` receive callbacks. Global control/status/debug message structs exist for status-toggle management but are lightly used by the current driver.

## Control Flow
`keyspan_usa26_send_setup` fills `keyspan_usa26_portControlMessage` when ports open, close, change termios, change break state, or update modem outputs. The driver sets `setClocking` and `setPrescaler` only when baud changes, always programs LCR and flow-control intent, and uses the action flags to enable/disable TX/RX depending on reset mode. `usa26_indat_callback` implements this header's RX framing: byte 0 is a status byte when bit 7 is clear, or alternating status/data pairs when bit 7 is set.

## State and Persistence
The header declares only packed-by-convention message layouts. Persistence is external: `keyspan.c` caches baud, cflag, flow-control mode, modem lines, and break state, then serializes them into these fields for each control transfer.

## Dependencies and Integration Points
It depends on Linux integer type `u8` from the including C file and is included only by `keyspan.c`. Field names deliberately encode historical USA17/USA26 dual meanings, so the integration point is both the Linux driver and the firmware running on Keyspan adapters.

## Risks
The structs are wire layouts without explicit `__packed`; because all fields are `u8`, padding risk is low, but reordering or changing field types would break firmware compatibility. Constants such as `MAX_DATA_LEN` and RX error names are duplicated across message headers, so accidental include-order or macro reuse changes can affect shared parser code. Break RX error reporting is defined here but only partially surfaced by the driver.

## Test Signals
Validate serialized setup size and field offsets, baud/prescaler programming for USA26-format products, correct LCR mapping for CS5-CS8/parity/stop bits, RX status/data and alternating error/data packet parsing, modem status update behavior, and open/close reset-data-toggle behavior.
