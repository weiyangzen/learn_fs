# sources/distributed-fs/ceph-client/net/netfilter/xt_TPROXY.c

Purpose: legacy `TPROXY` target assigns prerouting packets to local transparent sockets and optionally rewrites skb marks.

Important APIs/types/functions: `tproxy_tg4()`, `tproxy_tg4_v0()`, `tproxy_tg4_v1()`, `tproxy_tg6_v1()`, check/destroy functions, nf_tproxy socket helpers, and nf_defrag enable/disable.

Control flow: check enables defrag and requires TCP/UDP non-inverted protocol matches. Runtime rejects fragments, reads transport header, finds established socket or listener, handles TCP TIME_WAIT, checks transparency, updates mark with mask/value, assigns socket, and accepts or drops.

State and persistence: configured address/port/mark plus per-rule defrag enablement. Dependencies include x_tables, mangle PREROUTING, nf_tproxy, inet socket lookup, and nf_defrag. Risks: defrag cleanup on validation failure, socket reference ownership, IPv6 TIME_WAIT target values, and mark rewrite coupling. Test signals: IPv4 v0/v1, IPv6 v1, TCP/UDP validation, fragments, listener/established/TIME_WAIT paths, non-transparent sockets, mark update, and defrag balance.
