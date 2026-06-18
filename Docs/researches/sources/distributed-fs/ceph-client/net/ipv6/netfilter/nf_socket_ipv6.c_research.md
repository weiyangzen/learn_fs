# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_socket_ipv6.c

Purpose: Provides slow-path IPv6 socket lookup for netfilter socket matching. It maps packets, including ICMPv6 errors quoting inner TCP/UDP headers, to local TCP/UDP sockets.

Important APIs, types, and functions: `nf_sk_lookup_slow_v6()` is exported. `extract_icmp6_fields()` parses ICMPv6 errors and extracts the quoted inner tuple. `nf_socket_get_sock_v6()` dispatches to `inet6_lookup()` for TCP and `udp6_lib_lookup()` for UDP.

Control flow: The lookup locates the transport header with `ipv6_find_hdr()` and rejects fragmented packets. For TCP/UDP it reads ports directly and computes data offset for TCP. For ICMPv6 it ignores informational messages, parses the quoted IPv6 header and extension headers, accepts only quoted TCP/UDP, and reverses tuple roles because the quoted source is local. If conntrack says the packet is an established/related reply for a completed SNAT flow, it substitutes the original source address/port to find the local socket. It then calls protocol-specific socket lookup using the incoming interface.

State and persistence: No persistent state. It uses conntrack state when present and borrows pointers to header-backed addresses, with a stack copy for quoted IPv6 headers.

Dependencies and integration: Depends on IPv6 header parsing, TCP/UDP hash lookup, conntrack NAT metadata, and netfilter socket match/tproxy users.

Risks and test signals: Risks include tuple reversal mistakes for ICMP errors, NAT reply handling, fragmented packet rejection, and safe header access with non-linear skbs. Tests should cover direct TCP/UDP packets, ICMPv6 errors quoting TCP/UDP, SNAT reply lookup, packets with extension headers, fragments, and missing/truncated headers.
