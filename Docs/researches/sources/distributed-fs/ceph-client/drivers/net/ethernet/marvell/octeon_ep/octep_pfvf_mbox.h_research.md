# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.h

## Purpose
This header defines the PF/VF mailbox protocol shared by the PF implementation: protocol versions, opcodes, response types, status constants, link enums, mailbox timing/fragment constants, and the packed 64-bit command/response word format.

## Important APIs, Types, And Functions
- Versions: `enum octep_pfvf_mbox_version` and `OCTEP_PFVF_MBOX_VERSION_CURRENT`.
- Opcodes: `enum octep_pfvf_mbox_opcode` covers version, MTU, MAC, link info, stats, Rx/link state, link status, device remove, firmware info, offloads, and link notification.
- Word types and status: `OCTEP_PFVF_MBOX_TYPE_CMD`, `RSP_ACK`, `RSP_NACK`, plus timeout/NACK/busy status codes.
- Protocol payload: `union octep_pfvf_mbox_word` overlays one `u64` with typed bitfield views for generic data, fragments, version, MAC, MTU, link state/status, firmware info, and offloads.
- Exported PF functions: `octep_pfvf_mbox_work()`, `octep_setup_pfvf_mbox()`, `octep_delete_pfvf_mbox()`, and `octep_pfvf_notify()`.

## Control Flow
The union layout allows a VF to write a single 64-bit command word and the PF to overwrite the mailbox data register with a single 64-bit response. Bulk commands use `s_data.frag` to distinguish the initial length request from subsequent six-byte fragment reads. The PF code uses opcode-specific union members to avoid separate serialization buffers for small commands.

## State And Persistence
The header itself defines no storage. It constrains runtime state in mailbox users by limiting inline payload data to 48 bits or six bytes, setting maximum retries/timeouts, and defining the current protocol version. Protocol version negotiation is persisted only in memory inside PF/VF device structures.

## Dependencies And Integration Points
The protocol is consumed by `octep_pfvf_mbox.c` on the PF side and mirrored in the VF mailbox header. It depends on Linux bit macros and Ethernet lengths through including source context. Firmware-related commands are bridged by PF control mailbox code, while notification opcodes are generated from firmware-to-host control messages.

## Risks And Edge Cases
- Bitfield packing and endianness must match PF and VF builds; the `__packed` union is a hardware/protocol ABI.
- The PF and VF headers duplicate protocol definitions; drift between them can break negotiation and command decoding.
- `OCTEP_PFVF_MBOX_MAX_DATA_SIZE` is six bytes because opcode/type/fragment fields consume the remaining bits; callers must not copy larger inline payloads.
- MTU constants represent hardware frame sizes, not netdev MTU directly.

## Test Signals
Compile both PF and VF users, compare enum/opcode values across PF and VF protocol headers, run version negotiation, exercise each opcode with ACK/NACK paths, and validate multi-fragment data transfers where payload lengths are not multiples of six.
