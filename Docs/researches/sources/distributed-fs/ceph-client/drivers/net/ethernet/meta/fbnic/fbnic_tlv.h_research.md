# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.h

## Purpose
`fbnic_tlv.h` defines the on-wire/on-page TLV layout for FBNIC firmware messages and the parser/builder API used by firmware mailbox code.

## Important APIs, Types, And Functions
Key types are `struct fbnic_tlv_hdr`, `struct fbnic_tlv_msg`, `enum fbnic_tlv_type`, `struct fbnic_tlv_index`, and `struct fbnic_tlv_parser`. Macros describe alignment/size, result array capacity, unknown IDs, typed attribute descriptors, parser table entries, value pointer access, boolean flag reads, getter shorthands, and the test message schema. Function declarations cover allocation, put helpers, nested helpers, getters, address copy, array parsing, attribute/message parsing, error parsing, and test creation/parser.

## Control Flow
The header establishes the parser contract: each message parser table maps a message ID to an attribute index and callback, while each attribute index maps IDs to expected type/length. Message length is in dwords including the header; attribute length is bytes including the header; all payloads are aligned to 32-bit boundaries.

## State And Persistence
TLV state lives in caller-owned page buffers. Header bitfields persist in little-endian firmware message format and vary by CPU bitfield ordering macros. Parser result arrays contain non-owning pointers into the parsed message.

## Dependencies And Integration Points
The header includes byteorder, bits, constants, and types. It forward declares `fbnic_dev` for test helpers. Firmware command/response modules include it to build messages and define parser tables.

## Risks
Bitfield layout depends on `__LITTLE_ENDIAN_BITFIELD`/`__BIG_ENDIAN_BITFIELD`; unsupported build environments fail intentionally. Attribute IDs must fit the results array if callers want direct indexed access. The alignment and maximum raw-data constants assume page-sized messages with space reserved for safety.

## Test Signals
Compile on supported endian configurations, TLV self-test success, parser tables ending with `FBNIC_TLV_ATTR_LAST`, parser arrays ending with `FBNIC_TLV_MSG_ERROR`, and correct little-endian integer round trips are the main signals.
