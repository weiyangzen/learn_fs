<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_l2tp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_l2tp.c

## Purpose
`xt_l2tp.c` implements matching for L2TP headers carried over UDP or directly over IP. It supports L2TPv2 and L2TPv3 fields such as tunnel id, session id, version, type, and optional sequence numbers.

## Important APIs, Types, and Functions
`struct l2tp_data` is the parsed temporary view. `l2tp_udp_mt()` parses UDP-encapsulated L2TP, `l2tp_ip_mt()` parses direct L2TP/IP, and `l2tp_mt4()`/`l2tp_mt6()` dispatch by family and protocol. `l2tp_match()` compares parsed data with `struct xt_l2tp_info`. `l2tp_mt_check()`, `l2tp_mt_check4()`, and `l2tp_mt_check6()` validate flags, hooks, and protocol rule requirements.

## Control Flow, State, and Persistence
The packet path rejects fragments, fetches UDP or L2TP headers with skb helpers, validates version-specific layouts, parses v2 flags and optional Ns/Nr fields, parses v3 session/tunnel identifiers, then applies enabled comparisons with inversion. Checkentry requires the enclosing iptables rule to specify UDP or L2TPIP and rejects v2 direct-IP mode. There is no persistent module state.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 iptables entry metadata, UDP headers, L2TP protocol constants, and hook masks for PREROUTING, INPUT, OUTPUT, and FORWARD.

## Risks and Test Signals
Risks include variable header length parsing, truncated UDP payloads, version confusion between v2 and v3, direct-IP restrictions, and sequence-field presence handling. Tests should cover UDP and direct-IP L2TPv3, L2TPv2 over UDP, fragments, short headers, tunnel/session id matching, flags and inversion, missing protocol rules rejected at checkentry, and IPv6 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_l2tp.c -->
