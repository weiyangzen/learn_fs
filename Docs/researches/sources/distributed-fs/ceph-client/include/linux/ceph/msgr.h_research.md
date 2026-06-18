# sources/distributed-fs/ceph-client/include/linux/ceph/msgr.h

## Purpose

`msgr.h` defines Ceph messenger wire-level constants and packed message structures: banners, msgr2 feature bits, entity names and addresses, v1 connection tags, connect request/reply structs, message headers, priorities, and footers.

## Important APIs, Types, and Functions

Important definitions include `CEPH_BANNER`, `CEPH_BANNER_V2`, `CEPH_MSGR2_SUPPORTED_FEATURES`, `ceph_seq_t`, `ceph_seq_cmp()`, `ceph_entity_name`, `ceph_entity_addr`, `ceph_entity_inst`, `ceph_msg_connect`, `ceph_msg_connect_reply`, `ceph_msg_header_old`, `ceph_msg_header`, `ceph_msg_header2`, `ceph_msg_footer_old`, and `ceph_msg_footer`.

## Control Flow

Wire negotiation starts with banner exchange, then connect request/reply tags such as READY, RESETSESSION, RETRY_SESSION, RETRY_GLOBAL, FEATURES, or auth challenges. Message transfer uses headers, payload sections, and footers with CRC/signature flags.

## State and Persistence Behavior

No local mutable state exists. The constants are persistent network ABI. Sequence comparison is rollover-safe for 32-bit connection sequence numbers.

## Dependencies and Integration Points

It is included by `ceph_fs.h`, `decode.h`, `rados.h`, and `messenger.h`. It is the low-level contract consumed by messenger v1/v2 implementations and address encoding code.

## Risks and Edge Cases

Packed struct changes are wire breaks. Header old/new/header2 variants must be selected by protocol version correctly. `ceph_addr_equal_no_type()` ignores address type intentionally; callers needing msgr1/msgr2 distinction must not use it. CRC/signature flags must match payload handling.

## Test Signals

Validate banner parsing, connect tag handling, header/footer size and field offsets, sequence rollover comparisons, CRC/signature flag behavior, and mixed msgr1/msgr2 negotiation.
