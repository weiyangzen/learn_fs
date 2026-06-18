# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cpl5_cmd.h

## Purpose
`cpl5_cmd.h` defines Chelsio T1/T2 CPL5 protocol opcodes, errors, helper macros, and packed command structures. CPL messages are the firmware/hardware command and completion protocol for TCP offload, packet TX/RX, route/L2/SMT table operations, TCB manipulation, and internal MSS notifications.

## Important APIs, Types, and Constants
`enum CPL_opcode` assigns 8-bit opcode values for passive/active open, close, abort, peer close, TCB get/set, PCMD, RX/TX data, RX/TX packets, L2T/SMT/RTE operations, ARP miss, migration, errors, and `CPL_MSS_CHANGE`. `enum CPL_error` defines firmware error statuses. Helper macros `V_OPCODE`, `G_OPCODE`, `G_TID`, `MK_OPCODE_TID`, `OPCODE_TID`, and `GET_TID` pack and unpack the opcode/TID word. Major structures include open/listen/accept/establish commands, TCB commands, close/abort commands, data and packet headers, LSO headers, L2T/SMT/RTE read/write requests and replies, and `cpl_mss_change`.

## Control Flow and Integration
The header has no code flow, but driver/offload code uses these layouts to construct messages sent to the adapter and parse messages received from it. `union opcode_tid` is the common first word for connection-oriented commands. Packet TX/RX structures use endian-guarded bitfields for interface id, checksum disable/valid flags, VLAN validity, packet status, LSO header sizes, and table selectors.

## State and Persistence
The structures represent transient command/completion buffers exchanged with hardware. TIDs refer to hardware connection-table state, while L2T/SMT/RTE/TCB commands manipulate hardware tables that persist until overwritten, reset, or adapter reinitialization. The header itself stores no state.

## Dependencies and Risks
The header depends on `<asm/byteorder.h>` defining a supported bitfield endian mode and on network byte-order helpers used by consumers. Risks include opcode/value drift from firmware, unaligned command assumptions, endian bitfield mistakes, missing explicit packing if compiler layout changes, and confusion between host and network byte order in TID/opcode fields.

## Test Signals
Compile on supported endian targets, run offload command encode/decode tests, validate `GET_TID` and opcode packing, exercise TX packet and LSO descriptors, parse RX packet checksum/VLAN flags, and test L2T/SMT/RTE/TCB operations against hardware or protocol-level simulators.
