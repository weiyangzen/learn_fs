# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/setup_protocol.h

## Purpose
`setup_protocol.h` defines packed wire-format messages and signal numbers for the IPWireless setup protocol exchanged with card firmware. It covers version negotiation, channel configuration, open/close notifications, driver information, and reboot acknowledgement.

## Important APIs, Types, And Functions
- `TL_SETUP_VERSION`, query timeout, and maximum query count define setup protocol negotiation.
- Signal numbers identify version query/response, config/config-done, open/close, info/ack, and reboot/ack messages.
- Packed structs model each message: version query/response, config, config done, open, close, info, info ack, and reboot ack.
- Driver identity constants distinguish communication and NDISWAN-style driver info messages.
- `union ipw_setup_rx_msg` groups receive-side message formats.

## Control Flow And State
This header has no executable flow. Consumers serialize and parse these structs during firmware setup: query version, configure ports, send config done, handle asynchronous open/close, acknowledge info, and acknowledge reboot messages.

## State And Persistence Behavior
State exists as protocol bytes in transit. All structs are packed and byte-sized, so layout must remain stable across compiler and firmware boundaries.

## Dependencies And Integration Points
It is protocol glue between the Linux driver hardware/setup layer and IPWireless firmware. Higher layers observe resulting channel open/close and reboot events through hardware, network, and tty callbacks.

## Risks And Edge Cases
Adding padding or multi-byte host-endian fields would break firmware compatibility. Message numbers 0-9 are obsolete and reserved. Version retry behavior is implemented elsewhere but depends on constants from this file.

## Test Signals
Validate exact structure sizes, serialized signal numbers, version retry handling, channel open/close event propagation, info acknowledgements, and reboot message handling through the scheduled reset path.
