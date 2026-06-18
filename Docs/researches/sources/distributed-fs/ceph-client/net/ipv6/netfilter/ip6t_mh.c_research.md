# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_mh.c

Purpose: Implements the IPv6 xtables `mh` match for Mobile IPv6 Mobility Header type ranges.

Important APIs/types/functions: Uses `mh_mt6`, `mh_mt6_check`, `type_match`, `struct ip6_mh`, `struct ip6t_mh`, and registers with `.proto = IPPROTO_MH`.

Control flow: The match refuses nonzero fragment offsets, safely reads the Mobility Header at `par->thoff`, hotdrops tinygrams or headers whose payload proto is not `IPPROTO_NONE`, and matches the type against an inclusive range with optional inversion. Checkentry rejects unknown inversion flags.

State and persistence: Stateless.

Dependencies/integration: Depends on Mobile IPv6 header definitions and xtables protocol-filtered match dispatch.

Risks and test signals: Risks include hotdrop on truncated MH, fragment handling expectations, and invalid payload-proto enforcement. Tests should cover type ranges, inversion, nonzero fragment offsets, truncated headers, bad payload proto, and explicit `-p mh` dispatch.
