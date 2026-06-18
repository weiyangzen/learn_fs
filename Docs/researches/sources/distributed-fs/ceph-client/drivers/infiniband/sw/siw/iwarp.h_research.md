# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/iwarp.h

## Purpose

`iwarp.h` defines SIW's iWARP wire-format contract for MPA, DDP, and RDMAP framing over TCP, including structures, bit masks, helpers, terminate codes, and opcodes.

## Important APIs, Types, and Functions

It defines MPA revisions/keys/private-data limits/flags, MPA v2 controls, marker/trailer formats, `struct iwarp_ctrl`, RDMA write/read/send/terminate packet layouts, tagged/untagged control structs, `union iwarp_hdr`, terminate error enums, DDP/RDMAP/LLP error codes, and inline field accessors.

## Control Flow

The header has no runtime logic. SIW CM/TX/RX code uses it to negotiate MPA, format outgoing FPDUs, parse incoming frames, validate versions/opcodes, and construct terminate messages.

## State and Persistence Behavior

No mutable state is stored. The definitions describe protocol bytes carried on TCP streams and transient parser views over buffers.

## Dependencies and Integration Points

It depends on RDMA CM private-data size, Linux endian/fixed-width types, and architecture byte-order bitfields. It integrates with SIW connection management and QP TX/RX protocol code.

## Risks and Edge Cases

Wire layout is endian-sensitive. `struct iwarp_terminate` bitfields depend on architecture byte-order macros. Some MPA v2 control values overlap by request/reply context. CRC, marker, and padding lengths must match framing code.

## Test Signals

Test MPA v1/v2 negotiation, private data boundaries, CRC/marker handling, write/read/send/send-invalidate/terminate parsing, terminate code round trips on little/big endian builds, malformed opcode/version rejection, and interop with SIW or hardware iWARP peers.
