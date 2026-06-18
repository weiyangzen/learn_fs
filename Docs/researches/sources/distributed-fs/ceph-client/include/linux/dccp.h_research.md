# sources/distributed-fs/ceph-client/include/linux/dccp.h

Purpose: Supplies small kernel helpers for interpreting DCCP packet headers on top of the UAPI DCCP definitions.

Important APIs, types, and functions: Inline helpers are `dccp_hdrx()`, `__dccp_basic_hdr_len()`, `dccp_hdr_seq()`, and `__dccp_hdr_len()`. They consume `struct dccp_hdr`, optional `struct dccp_hdr_ext`, and `dccp_packet_hdr_len()`.

Control flow: Callers inspect the DCCP X bit to decide whether an extended sequence header follows the base header. Sequence extraction builds either a 48-bit extended sequence from high and low fields or a short sequence from base fields. Header length combines base/extension length and packet-type-specific header length.

State and persistence: No state is stored. The helpers decode transient packet bytes.

Dependencies and integration points: Depends on `<uapi/linux/dccp.h>` layout and network byte-order helpers. Used by DCCP protocol parsing, skb validation, and congestion/control-path code.

Risks and test signals: Risks include using helpers before ensuring the skb contains enough linear header bytes, endian mistakes, and malformed X-bit/header-length combinations. Test short and extended DCCP headers, each packet type, truncated skb paths, and sequence number boundary values.
