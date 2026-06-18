# sources/distributed-fs/ceph-client/net/netfilter/xt_REDIRECT.c

Purpose: `REDIRECT` NAT target redirects traffic to the local host in PREROUTING or LOCAL_OUT.

Important APIs/types/functions: `redirect_tg4()`, `redirect_tg6()`, `redirect_tg4_check()`, `redirect_tg6_checkentry()`, `redirect_tg_destroy()`, and nf_nat_redirect helpers.

Control flow: check rejects explicit MAP_IPS, validates IPv4 range size, and pins conntrack. Runtime converts IPv4 legacy range or uses IPv6 range directly, calls redirect helper with hook number, and returns NAT verdict.

State and persistence: NAT bindings live in conntrack; rules hold conntrack netns refs. Dependencies include nat table hooks, nf_nat_redirect, conntrack, and IPv4/IPv6 range ABIs. Risks: invalid explicit address mapping, hook restrictions, legacy range conversion, and ref cleanup. Test signals: IPv4/IPv6 redirects, port ranges, MAP_IPS rejection, rangesize rejection, prerouting/local-out, and destroy put.
