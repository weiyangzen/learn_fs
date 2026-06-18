# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32_parse.h

Purpose: provides static parser tables and field-fill helpers that map supported TC u32 offsets/masks into `ch_filter_specification` match fields.

Important APIs/types: `struct cxgb4_match_field`, IPv4/IPv6 fill helpers for TOS, fragment flag, protocol, source/destination addresses, L4 port fill helper, field arrays `cxgb4_ipv4_fields`, `cxgb4_ipv6_fields`, `cxgb4_tcp_fields`, `cxgb4_udp_fields`, `struct cxgb4_next_header`, jump arrays `cxgb4_ipv4_jumps`/`cxgb4_ipv6_jumps`, `struct cxgb4_link`, and `struct cxgb4_tc_u32_table`.

Control flow/state: the `.c` parser walks these tables by selector offset and invokes `val` callbacks. Jump arrays describe supported u32 link shapes from IPv4 IHL/protocol or fixed IPv6 header to TCP/UDP port parsing. Link entries persist partial specs and a bitmap of hardware filter TIDs associated with each linked bucket.

Dependencies/integration: depends on Linux TC u32 selector/key layouts and Chelsio filter specification fields. It is private to `cxgb4_tc_u32.c` but encodes much of the supported offload grammar.

Risks: byte-order and offset assumptions are precise; incorrect masks can silently encode wrong hardware matches. Fragment parsing only supports specific MF/DF patterns. IPv6 extension headers are not modeled; jumps assume the fixed 40-byte header.

Test signals: parser unit coverage for each offset, endian-sensitive address/port/TOS extraction, supported and rejected fragment masks, IPv4 IHL jumps, IPv6 fixed-header jumps, and link bitmap accounting.
