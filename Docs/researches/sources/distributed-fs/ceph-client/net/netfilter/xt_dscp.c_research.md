<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dscp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_dscp.c

## Purpose
`xt_dscp.c` implements DSCP and legacy TOS field matches for IPv4 and IPv6. It lets rules classify packets by differentiated-services or TOS bits in the IP header.

## Important APIs, Types, and Functions
`dscp_mt()` and `dscp_mt6()` compare IPv4 `ip_hdr(skb)->tos >> XT_DSCP_SHIFT` and IPv6 `ipv6_get_dsfield(ipv6_hdr(skb)) >> XT_DSCP_SHIFT` against `struct xt_dscp_info`. `tos_mt()` compares masked TOS through `struct xt_tos_match_info`. `dscp_mt_check()` rejects DSCP values above `XT_DSCP_MAX`.

## Control Flow, State, and Persistence
There is no persistent state. Packet evaluation reads the already-parsed network header, extracts DSCP or TOS, compares against configured values, and applies inversion.

## Dependencies and Integration Points
The module registers `dscp` matches for IPv4 and IPv6 plus a protocol-unspecified `tos` match. It uses x_tables, IPv4/IPv6 header helpers, and userspace UAPI match structures.

## Risks and Test Signals
Risks include confusing DSCP values with full TOS/traffic-class bytes, IPv6 traffic-class extraction, and invalid userspace DSCP values. Tests should cover all DSCP edge values, ECN bits not affecting DSCP comparison, TOS masks, inversion, IPv4 and IPv6 packets, and checkentry rejection of out-of-range DSCP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dscp.c -->
