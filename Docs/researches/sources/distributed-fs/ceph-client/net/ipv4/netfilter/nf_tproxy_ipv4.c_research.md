# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_tproxy_ipv4.c

## Purpose
IPv4 transparent proxy socket helpers. The file locates listener or established sockets for redirected TCP/UDP traffic, chooses a local address when one is not specified, and handles TCP TIME_WAIT sockets for redirected SYNs.

## Important APIs, types, and functions
Exported symbols are `nf_tproxy_handle_time_wait4()`, `nf_tproxy_laddr4()`, and `nf_tproxy_get_sock_v4()`. It uses TCP/UDP lookup helpers, TIME_WAIT release/deschedule helpers, and `enum nf_tproxy_lookup_t` to distinguish listener versus established lookup.

## Control flow
For TIME_WAIT TCP sockets, a pure SYN triggers listener lookup at the requested or original destination tuple; if found, the time-wait socket is descheduled and replaced. `nf_tproxy_laddr4()` returns user address or first primary ingress-device IPv4 address, falling back to destination. `nf_tproxy_get_sock_v4()` performs TCP listener/established lookup or UDP lookup with filtering for connected/wildcard state and requested mode.

## State and persistence
No persistent module state. It manipulates socket references and may deschedule a TIME_WAIT socket. Address selection reads RCU-protected in-device addresses.

## Dependencies and integration points
Integrates with netfilter TPROXY, IPv4 device address management, TCP/UDP socket tables, and TIME_WAIT handling. Used by TPROXY rule implementations preserving original destination semantics.

## Risks
Reference handling is central for listener refcounts, rejected UDP `sock_put()`, and TIME_WAIT release/deschedule. Wildcard listener behavior is intentional for TPROXY but must be filtered by callers that do not want it. Header truncation must not leak references.

## Test signals
Test TCP established/listener lookup, wildcard and specific binds, SYN to TIME_WAIT redirection, malformed TCP headers, UDP connected versus wildcard sockets, device-bound lookup, user local address, and ingress primary-address fallback.
