<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmp.c

## Purpose
Implements IPv4 ICMP conntrack tuple handling, echo-like flow tracking, ICMP error correlation to existing connections, netlink tuple encoding, and timeout policy support.

## Important APIs, Types, and Functions
Key functions are `icmp_pkt_to_tuple()`, `nf_conntrack_invert_icmp_tuple()`, `nf_conntrack_icmp_packet()`, `nf_conntrack_inet_error()`, and `nf_conntrack_icmpv4_error()`. Descriptor `nf_conntrack_l4proto_icmp` provides netlink tuple policy and timeout policy operations. Default timeout is `30*HZ`.

## Control Flow
Tuple extraction records ICMP type, code, and echo ID. New ICMP flows are allowed only for request-like types in `valid_new`; replies share the inverted tuple via `invmap`. ICMP errors validate header length, checksum on PREROUTING when enabled, known type range, and whether the type is an error. Error packets parse the embedded inner tuple, invert it, find the related conntrack in the right zone, and ensure the outer destination matches the found tuple destination before setting skb conntrack to RELATED.

## State and Persistence
State is limited to per-net ICMP timeout and skb conntrack association for RELATED errors. ICMP entries keep normal core conntrack state and accounting, but no extra protocol-private mutable fields are stored.

## Dependencies and Integration Points
Depends on IPv4 header/checksum helpers, conntrack tuple/core/zone APIs, timeout extension, netlink conntrack attributes, and invalid logging. It shares `nf_conntrack_inet_error()` with ICMPv6-style error correlation.

## Risks
Incorrect outer/inner destination validation can mark unrelated errors as RELATED. ICMP type inversion tables must cover only request/reply pairs. Accepting non-error ICMP in the error path avoids overtracking but makes tests sensitive to type selection.

## Test Signals
Verify echo, timestamp, info, and address request/reply tracking; invalid new ICMP types; bad checksums; short packets; related errors for TCP/UDP flows; forged outer-destination mismatch logs; and ctnetlink ICMP tuple filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmp.c -->
