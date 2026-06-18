# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_tproxy_ipv6.c

Purpose: Implements IPv6 transparent proxy socket helpers for netfilter TPROXY. It selects local addresses, finds listener/established sockets, and handles TCP TIME_WAIT redirection.

Important APIs, types, and functions: Exported helpers are `nf_tproxy_laddr6()`, `nf_tproxy_handle_time_wait6()`, and `nf_tproxy_get_sock_v6()`. Lookups use `inet6_lookup_listener()`, `__inet6_lookup_established()`, and `udp6_lib_lookup()`.

Control flow: `nf_tproxy_laddr6()` returns a user-supplied local address unless it is unspecified; otherwise it scans the ingress device's IPv6 addresses under lock and selects the first non-tentative, non-deprecated address, falling back to the original destination. `nf_tproxy_handle_time_wait6()` parses TCP, and for bare SYNs to TIME_WAIT sockets attempts to find a listener at the proxy local address/port, replacing the TIME_WAIT socket if successful. `nf_tproxy_get_sock_v6()` dispatches TCP listener/established lookups or UDP lookup, then filters UDP results according to connected/wildcard state and requested lookup type.

State and persistence: No persistent module state. It manipulates socket references: listeners returned from listener lookup get a refcount bump, UDP sockets may be `sock_put()` if unsuitable, and TIME_WAIT sockets may be descheduled/released.

Dependencies and integration: Depends on IPv6 address configuration, TCP/UDP socket tables, TPROXY core enums, and ingress device context. Used by xt/nft transparent proxy rule implementations.

Risks and test signals: Risks include incorrect wildcard listener semantics, reference handling, TIME_WAIT replacement, and address selection on devices with tentative/deprecated addresses. Tests should cover TCP listener and established lookup, UDP connected versus wildcard sockets, SYN to TIME_WAIT, unspecified user local address, bound interface behavior, and truncated TCP headers.
