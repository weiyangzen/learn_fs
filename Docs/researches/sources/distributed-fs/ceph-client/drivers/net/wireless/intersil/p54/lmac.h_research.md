# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/lmac.h

## Purpose
This header defines the Prism54 LMAC host/firmware protocol: control frame types, p54 header flags, RX/TX payload layouts, scan/MAC/LED/QoS/statistics/key/power-save payloads, helper macros, and prototypes for common firmware I/O and TX functions.

## Important APIs, Types, and Functions
- `enum p54_control_frame_types` enumerates setup, scan, trap, DCF, keycache, TIM, PSM, TX cancel/done, LED, EEPROM readback, statistics, and other firmware controls.
- `struct p54_hdr` is the common LMAC header with flags, payload length, request ID, type, and retry fields.
- Macros `GET_REQ_ID`, `FREE_AFTER_TX`, `IS_DATA_FRAME`, and `GET_HW_QUEUE` decode SKB contents.
- Protocol structs cover exported/dependent interfaces, EEPROM readback, RX data metadata, traps, TX status, TX data command, MAC setup, scan bodies, LED, EDCF, statistics, synth config, timers, keys, power save, multicast filter, TX cancel, TIM, and ARP table.
- Prototypes expose LED, TX, scan, MAC, crypto, EEPROM, RSSI, and IE helpers.

## Control Flow
No executable logic is present. Runtime code casts SKB payloads to these packed structs and transmits/receives them through bus-specific transports.

## State and Persistence Behavior
These structs describe transient firmware command and indication frames. State is persisted in `p54_common` or firmware memory, not in the header. Request IDs tie transmitted frames to firmware memory allocations and completion feedback.

## Dependencies and Integration Points
It depends on p54 common types, Linux bit/endian helpers, and mac80211 SKB conventions. It is central to `fwio.c`, `main.c`, transport TX/RX paths, and EEPROM readback.

## Risks and Edge Cases
The layouts are firmware ABI and are packed. Any mismatch in lengths, endian conversion, or firmware-version-specific struct selection can break device operation. `FREE_AFTER_TX()` depends on exact control flags to decide SKB ownership after transport completion.

## Test Signals
Signals include successful firmware command processing, correct RX/TX status interpretation, stable scan/channel changes, key upload, power-save transitions, and absence of malformed control-frame responses.
