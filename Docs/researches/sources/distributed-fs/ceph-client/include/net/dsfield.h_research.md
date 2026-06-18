# sources/distributed-fs/ceph-client/include/net/dsfield.h

Read `sources/distributed-fs/ceph-client/include/net/dsfield.h` completely for this pass (53 lines, 1147 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dsfield.h_research.md`.

Purpose: provides inline helpers to read and modify the Differentiated Services field in IPv4 and IPv6 headers while preserving ECN bits and maintaining the IPv4 header checksum.

Important APIs/types/functions: `ipv4_get_dsfield()` returns `iph->tos`. `ipv6_get_dsfield()` extracts the IPv6 traffic class from the first 16 bits of the header. `ipv4_change_dsfield()` applies `(old_tos & mask) | value`, incrementally adjusts the IPv4 header checksum, and stores the new TOS. `ipv6_change_dsfield()` updates the traffic-class bits in the IPv6 version/traffic-class/flow-label word.

Control flow: packet marking or QoS code reads current DS field, computes a masked replacement value, and calls the appropriate IPv4/IPv6 changer. IPv4 uses one's-complement adjustment instead of recomputing the full header checksum; IPv6 has no header checksum.

State and persistence: mutates packet headers in-place. No separate state is stored.

Dependencies and integration points: depends on Linux IP/IPv6 header definitions and byteorder helpers. It is used by TC, netfilter, tunnel, qdisc, and QoS code that marks DSCP/ECN bits.

Risks: the `mask` argument preserves bits where set and `value` must already be positioned in DS field bits; misuse can overwrite ECN or DSCP unintentionally. IPv4 checksum math is sensitive to carry handling. IPv6 helper writes through the first 16-bit word and must preserve version and flow-label bits.

Test signals: IPv4 and IPv6 DSCP/ECN rewrite tests, checksum validation after IPv4 changes, masks that preserve ECN bits, zero/full mask cases, and packet capture verification of traffic-class fields.
