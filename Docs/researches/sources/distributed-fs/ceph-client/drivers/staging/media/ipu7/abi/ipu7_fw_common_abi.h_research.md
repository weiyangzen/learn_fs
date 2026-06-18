# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_common_abi.h

## Purpose

This header defines common GOFO firmware ABI primitives used by boot, ISYS, PSYS, and message protocols: address type, version structures, TLV headers/lists, error records, generic message headers, indirect/log messages, and common queue IDs.

## Important APIs, Types, and Functions

Important definitions include `ia_gofo_addr_t`, `struct ia_gofo_version_s`, `IA_GOFO_MSG_VERSION_INIT`, `struct ia_gofo_msg_version_list`, `struct ia_gofo_tlv_header`, `struct ia_gofo_tlv_list`, `struct ia_gofo_msg_err`, `struct ia_gofo_msg_header`, `struct ia_gofo_msg_header_ack`, `struct ia_gofo_msg_indirect`, and log message types. Queue IDs include ACK, LOG, and device input queues.

## Control Flow

No runtime control flow is implemented. Other ABI headers embed these common structs at the head of command, ack, log, graph, task, and stream messages.

## State and Persistence Behavior

The packed structures describe DMA/message queue tokens and payloads persisted only while firmware communication buffers are valid.

## Dependencies and Integration Points

It includes Linux fixed-width types. It is foundational for `ipu7_fw_boot_abi.h`, `ipu7_fw_msg_abi.h`, and `ipu7_fw_isys_abi.h`.

## Risks and Edge Cases

Packed TLV layout, alignment constants, and header embedding must match firmware parsers. The macro typo `IA_GOFO_MSG_ERR_UNSPECIFED` is ABI-visible naming but not behavioral. Error group/code checks should use `IA_GOFO_MSG_ERR_IS_OK()`.

## Test Signals

Compile ABI users, validate message sizes/offsets against firmware documentation, and test non-OK firmware errors through ack structures.
