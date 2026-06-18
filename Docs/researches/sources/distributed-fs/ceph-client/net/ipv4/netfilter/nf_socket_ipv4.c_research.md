# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_socket_ipv4.c

## Purpose
Slow-path IPv4 socket lookup for netfilter socket matching and transparent proxy users. It extracts packet or quoted ICMP tuples, accounts for SNATed replies, and returns matching TCP/UDP sockets.

## Important APIs, types, and functions
The exported entry is `nf_sk_lookup_slow_v4()`. `extract_icmp4_fields()` recovers an inner TCP/UDP tuple from ICMP errors. `nf_socket_get_sock_v4()` dispatches to `inet_lookup()` or `udp4_lib_lookup()`. Optional conntrack handling uses `nf_ct_get()`, established/related reply states, and `IPS_SRC_NAT_DONE`.

## Control flow
The lookup rejects non-initial fragments. TCP/UDP packets provide the tuple directly and compute data offset. ICMP packets must be ICMP errors quoting TCP or UDP. For SNATed reply packets, conntrack rewrites the local destination address/port to the original pre-SNAT source. The final protocol lookup uses the input device index.

## State and persistence
No owned persistent state. It reads skb, conntrack, namespace, and socket table state and returns sockets according to underlying lookup reference semantics.

## Dependencies and integration points
Integrates with netfilter socket infrastructure, TCP/UDP/ICMP parsing, inet socket lookup tables, and optionally conntrack. Consumers include socket match and TPROXY paths.

## Risks
Tuple extraction must handle truncation safely via `skb_header_pointer()`. NAT reversal only targets SNAT reply cases. Wildcard sockets may be returned and must be filtered by higher-level users where inappropriate.

## Test signals
Cover TCP/UDP lookup, fragments, ICMP errors with valid/truncated inner headers, SNATed replies, related ICMP replies, no-conntrack builds, device-bound sockets, wildcard sockets, and namespace isolation.
