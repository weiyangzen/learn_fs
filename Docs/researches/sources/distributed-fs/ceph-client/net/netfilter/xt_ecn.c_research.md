<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ecn.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_ecn.c

## Purpose
`xt_ecn.c` implements ECN matching for IPv4 and IPv6. It can match IP-layer ECN codepoints and TCP ECE/CWR flags.

## Important APIs, Types, and Functions
`match_tcp()` reads a TCP header and checks `XT_ECN_OP_MATCH_ECE` and `XT_ECN_OP_MATCH_CWR`. `match_ip()` and `match_ipv6()` compare ECN bits in IPv4 TOS or IPv6 traffic class. `ecn_mt4()` and `ecn_mt6()` combine those checks. `ecn_mt_check4()` and `ecn_mt_check6()` validate operation masks and require TCP protocol when TCP flag matching is requested.

## Control Flow, State, and Persistence
Packet evaluation first checks TCP flags if requested, using `skb_header_pointer()` and hotdropping truncated TCP headers. Then it checks the IP ECN bits when requested. All configured checks must succeed. The module stores no packet or rule state beyond the rule data.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 iptables entries for protocol validation, TCP header definitions, and traffic-class helpers. It registers family-specific `ecn` matches.

## Risks and Test Signals
Risks include allowing TCP flag matching without `-p tcp`, mishandling fragments or truncated TCP headers, and mixing ECN codepoints with DSCP bits. Tests should cover CE/ECT0/ECT1/not-ECT values, ECE/CWR combinations, non-TCP rules rejected when TCP checks are requested, IPv6 extension-header thoff behavior from x_tables, inversion by absence of options, and hotdrop on short TCP headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ecn.c -->
