# sources/distributed-fs/ceph-client/include/net/inet_sock.h

Purpose: defines `struct inet_sock`, IPv4 request/cork/options structures, socket flags, and helpers shared by INET protocols.

Important APIs/types: `struct ip_options` and `ip_options_rcu` store IPv4 options. `struct inet_request_sock` extends request sockets with addresses, ports, TCP option negotiation flags, mark, and IPv4/IPv6 options. `struct inet_cork` and `inet_cork_full` persist packet-building state while a socket is corked. `struct inet_sock` embeds `struct sock` first, optional IPv6 info, address/port aliases, flags, source address, options, IPID counter, TOS/TTL/PMTU/multicast fields, local port range, multicast list, and cork. Flag helpers manipulate `inet_flags`, and conversion helpers handle full sockets, request sockets, and time-wait exclusion.

Control flow and state: socket create/configure paths set options and flags; transmit paths read cork and address fields; receive lookup uses address/port aliases. `inet_sk_state_load()` pairs with state stores for lockless readers. Request helpers derive mark and bound device from listener/sysctls.

Dependencies and integration: depends on flow, DSCP, sock, request sock, TCP states, l3mdev, and netns hash. It underpins TCP, UDP, RAW, ping, IPv6 dual-stack, and route lookup.

Risks: first-member layout and alias macros are structural contracts. Atomic flag and state access must respect concurrency. Tests should cover socket option flags, corked sends, request mark/bound-device inheritance, nonlocal bind validation, full-socket conversion, checksum-conversion counters, and IPv4/IPv6 dual-stack fields.
