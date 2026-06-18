# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rpfilter.c

Purpose: Implements the IPv6 xtables `rpfilter` match, checking whether reverse routing for a packet's source would use the ingress interface.

Important APIs/types/functions: Uses `rpfilter_mt`, `rpfilter_check`, `rpfilter_lookup_reverse6`, `struct xt_rpfilter_info`, `ip6_route_lookup`, l3mdev helpers, and route flags.

Control flow: Loopback packets pass subject to inversion. Unspecified source addresses pass because forwarding will drop them later. Otherwise, it builds a reverse `flowi6` from packet source, optional destination source constraint, flow label, nexthdr, mark if enabled, link-local/strict interface constraints, and l3mdev context. It rejects route errors, reject/anycast routes, and local routes unless `ACCEPT_LOCAL`; it accepts if the route device or master matches ingress or loose mode is set. Checkentry allows only raw or mangle tables and known option bits.

State and persistence: Stateless beyond per-rule flags.

Dependencies/integration: Depends on IPv6 FIB lookup, netdevice/l3mdev, and xtables pre-routing hook.

Risks and test signals: Risks include policy routing mark behavior, l3mdev matching, local/anycast route handling, and table restriction regressions. Tests should cover strict/loose modes, valid-mark, accept-local, invert, link-local sources, VRF/l3mdev ingress, raw/mangle checkentry, and asymmetric route topologies.
