# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.h

## Purpose
Defines the common wlcore ACX firmware ABI: interrupt bits, ACX header, packed payload structures, constants/enums, ACX numeric ids, and prototypes for the common ACX helper functions.

## Important APIs, types, and functions
- Interrupt masks include watchdog, init-complete, event mailboxes, command complete, hardware available, data, trace, and software watchdog bits.
- `struct acx_header` is the common command/information-element prefix with id and length.
- Payload structures cover sleep auth, roles, PSM, RX/TX lifetimes, slots, multicast groups, beacon filtering, event masks, feature config, TX power, wake-up conditions, AID, preamble/CTS, rate policy, AC/TID config, memory config/map, RX config, BET, ARP, PM, keep-alive, RSSI/SNR, HT, BA, TSF, streaming, AP retry, PS config, FM coexistence, rate management, hangover, RX filters, and roaming stats.
- ACX id enum maps symbolic names to firmware numeric ids.
- Function prototypes match `acx.c`, including optional PM filter helpers.

## Control flow
No executable flow. The header constrains every ACX command/interrogate transaction built by wlcore and lower drivers.

## State and persistence behavior
No local state. Packed structures describe transient command payloads or volatile firmware response snapshots. Some payload fields correspond to firmware state that persists until reconfigured or reset.

## Dependencies and integration points
Includes wlcore and command headers and is included by common wlcore modules and chip-family modules such as wl18xx. It is the central compatibility contract between host driver and TI firmware for configuration.

## Risks and test signals
Highest risk is ABI drift: packing, flexible-array sizing, endian annotations, enum/id values, and fixed table lengths. Compile tests catch only syntax; runtime tests must cover boot/init, association, AP mode, scans, power save, BA, RX filters, statistics, event masks, and all lower-driver ACX extensions.
