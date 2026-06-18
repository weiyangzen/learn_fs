<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_multiport.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_multiport.c

## Purpose
`xt_multiport.c` implements matching multiple TCP, UDP, UDP-Lite, SCTP, or DCCP ports in one rule, including optional port ranges in newer revisions.

## Important APIs, Types, and Functions
`ports_match_v0()`, `ports_match_v1()`, and the shared match functions evaluate `struct xt_multiport`, `xt_multiport_v1`, and protocol ports read from the transport header. `multiport_mt_check()` and `multiport_mt6_check()` validate that the enclosing rule protocol is one of the supported L4 protocols. `multiport_mt_reg[]` registers revisions for IPv4 and IPv6.

## Control Flow, State, and Persistence
Fragments are ignored because transport ports may be absent. The matcher reads source and destination ports, then evaluates the configured mode: source ports, destination ports, or either. Revision 1 supports ranges encoded by pflags. No state is persisted.

## Dependencies and Integration Points
It depends on x_tables, IPv4/IPv6 iptables rule metadata for protocol checks, `skb_header_pointer()`, and common transport header layouts where the first four bytes are source/destination ports.

## Risks and Test Signals
Risks include malformed port arrays, missing `-p` protocol checks, range encoding mistakes, fragment behavior, and protocol families with similar port layouts but different parser assumptions. Tests should cover TCP/UDP/UDPLite/SCTP/DCCP, source/destination/either modes, ranges, maximum port count, invalid protocols rejected, fragments, truncated transport headers, and inversion by surrounding rule semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_multiport.c -->
