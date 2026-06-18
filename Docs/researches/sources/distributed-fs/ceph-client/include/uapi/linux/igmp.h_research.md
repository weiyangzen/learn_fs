
# sources/distributed-fs/ceph-client/include/uapi/linux/igmp.h

## Purpose

`igmp.h` defines on-wire IGMP packet layouts, IGMPv3 report/query structures, record/type constants, host state constants, timing constants, and well-known multicast groups. The complete 130-line file was read.

## Important APIs, Types, and Functions

Structures are `igmphdr`, `igmpv3_grec`, `igmpv3_report`, and `igmpv3_query`. Constants cover IGMPv3 record types, packet type values such as membership query/report/leave and mtrace, BSD-compatible host member states, `IGMP_MINLEN`, delay/timer scale/age threshold, and multicast group addresses such as `IGMP_ALL_HOSTS`, `IGMP_ALL_ROUTER`, and `IGMPV3_ALL_MCR`.

## Control Flow

No implementation flow is present. Kernel and packet-processing code parse these on-wire structures, inspect type fields, handle endian-sensitive bitfields in IGMPv3 queries, and update multicast membership state elsewhere.

## State and Persistence Behavior

The header only defines packet layouts and constants. Membership state, timers, source filters, and router-version state live in IPv4 multicast code.

## Dependencies and Integration Points

It includes `linux/types.h` and `asm/byteorder.h`. It integrates with IPv4 multicast, bridge snooping, raw packet tools, routing daemons, and netfilter/packet parsers.

## Risks and Edge Cases

Flexible arrays and bitfields require length and endian validation. Risks include malformed `grec_nsrcs`/`ngrec`, query `qrv` and suppress bit ordering, checksum handling, and use of `htonl` group constants in UAPI code.

## Test Signals

Packet parser tests should cover IGMPv1/v2/v3 headers, multiple source records, truncated reports/queries, endian bitfield layout, checksum failures, leave/query timing, and bridge snooping behavior.
