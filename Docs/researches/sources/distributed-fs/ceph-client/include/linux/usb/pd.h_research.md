# `sources/distributed-fs/ceph-client/include/linux/usb/pd.h`

## Purpose

`pd.h` is the central USB Power Delivery protocol definition header. It defines PD control/data/extended message types, message headers, extended headers, wire-format PD messages, source/sink extended data blocks, PDO/RDO/APDO helpers, status/PPS/country structures, timers, and many bitfield helpers used by TCPM/TCPCI and Type-C drivers.

## Important APIs, Types, and Constants

- Enums define PD control messages, data messages, and extended messages across PD revisions.
- Header macros encode/decode message type, power role, data role, revision, message ID, data-object count, and extended-header bit; inline helpers decode little-endian headers.
- Extended header macros encode/decode chunking, chunk number, request-chunk, and data size.
- `struct pd_message` and `struct pd_chunked_ext_message_data` describe the on-wire packed message layout.
- `count_chunked_data_objs()` computes data-object count for chunked extended data.
- PDO helpers cover fixed, battery, variable, programmable supply, and adjustable supply objects, with units for voltage/current/power.
- RDO helpers encode fixed, battery, programmable, and adjustable requests and expose flags such as giveback, capability mismatch, USB suspend, communications capable, and no-suspend.
- Additional packed structures describe sink caps extended, PPS status, status messages, country info/codes, revision, and battery-related payloads.

## Control Flow and Lifetimes

TCPM and TCPC drivers construct PD headers and payload objects, transmit them through a port controller, parse received messages, and advance the PD policy engine. PDOs advertise capabilities; RDOs request a selected object; extended messages may be chunked and require size/count calculations. The header supplies encoding/decoding primitives while policy and retransmission live in implementation files.

## State and Persistence Behavior

PD protocol state such as message IDs, negotiated revision, power/data roles, partner capabilities, and selected PDOs lives in TCPM runtime state. The header defines immutable wire-format constants and helper macros. Packed structs are transient buffers as seen on the wire.

## Dependencies and Integration Points

It depends on bitfield helpers, kernel types, and Type-C role enums. It is included by `tcpm.h`, `tcpci.h`, `pd_vdo.h`, and Type-C/PD policy code. It bridges USB PD wire encoding to Type-C power, data, and alt-mode management.

## Risks and Edge Cases

Bitfield units are easy to misuse: fixed PDO voltage is in 50 mV units, current in 10 mA units, and APDO/AVS have different units. Header count must match payload size. Extended chunk sizing must include the extended header offset. PD revision gates message types and fields. Packed structures require endian conversion before arithmetic.

## Test Signals

Run TCPM PD negotiation tests for source/sink roles, fixed/PPS/AVS PDOs, RDO selection, extended messages, chunked payloads, hard/soft reset, role swaps, malformed headers, endian conversion, and PD revision compatibility.
