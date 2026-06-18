# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/emad.h

## Purpose
`emad.h` defines Ethernet Management Datagram constants shared by mlxsw code that builds, sends, receives, or diagnoses EMAD register-access frames. It contains frame sizing, Ethernet header constants, TLV type and length constants, operation classes, methods, and status decoding.

## Important APIs, Types, and Functions
- `MLXSW_EMAD_MAX_FRAME_LEN` and `MLXSW_EMAD_MAX_RETRY` define transport limits and retry behavior.
- Ethernet header constants define Mellanox multicast-like DMAC/SMAC, ethertype `0x8932`, protocol, and version.
- TLV enums cover END, OP, STRING, REG, and LATENCY TLVs. Operation enums cover request/response and query/write/send/event methods.
- `enum mlxsw_emad_op_tlv_status` enumerates device result codes.
- `mlxsw_emad_op_tlv_status_str()` converts status codes into diagnostic strings.

## Control Flow
This header has no runtime state or control flow beyond the inline status-string switch. It is included by EMAD handling code to keep protocol constants centralized.

## State and Persistence
No persistent state exists. Constants encode protocol layout and retry policy.

## Dependencies and Integration Points
The header is consumed by mlxsw core EMAD transport paths and register-access logic. It sits above bus implementations such as PCI and I2C because EMAD frames are carried over the bus transmit path.

## Risks
Protocol constants must match firmware expectations exactly. Unknown status codes map to `*UNKNOWN*`, so callers should log numeric status as well when available. Changing retry or frame-size constants can affect register-access reliability under busy firmware.

## Test Signals
Exercise EMAD query/write success, busy/ack retransmit handling, unsupported register/method/class errors, and unknown status logging. Packet captures or debug traces should show the expected ethertype, TLV order, and frame length.
