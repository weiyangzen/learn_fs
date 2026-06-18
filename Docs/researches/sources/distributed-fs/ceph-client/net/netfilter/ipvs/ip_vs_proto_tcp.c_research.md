# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_tcp.c

## Purpose
Implements TCP protocol support for IPVS: new-connection scheduling, NAT port and checksum rewriting, TCP state tracking, per-netns timeout tables, secure TCP mode transitions, and TCP application helper binding.

## Important APIs, Types, and Functions
`tcp_conn_schedule()` locates a service and creates an IPVS connection for acceptable TCP openers. `tcp_snat_handler()` and `tcp_dnat_handler()` rewrite ports and update TCP checksums. `tcp_csum_check()` validates checksums before app payload mangling. `tcp_states` and `tcp_states_dos` are transition tables selected by `tcp_timeout_change()`. `set_tcp_state()` and `tcp_state_transition()` update connection state and active/inactive counters. `tcp_register_app()`, `tcp_unregister_app()`, `tcp_app_conn_bind()`, and `ip_vs_tcp_conn_listen()` provide helper and LISTEN-state support. `ip_vs_protocol_tcp` registers the protocol operations.

## Control Flow
Scheduling rejects RST openers and, unless sloppy TCP is enabled, non-SYN packets; ICMP paths only require embedded ports. A matching service may drop under overload via `ip_vs_todrop()`, schedule a real server, or invoke `ip_vs_leave()` on no destination. NAT handlers ensure TCP header writability, validate checksum before helper mangling, invoke app helpers, rewrite source or destination port, and choose fast incremental checksum, partial checksum adjustment, or full recomputation based on payload changes and SKB checksum mode. State transition reads TCP flags, applies input/output/input-only transition table rows, updates active/inactive counters, assures conntrack at ESTABLISHED, and refreshes timeout.

## State and Persistence
Per-netns TCP state is app helper hash tables, app counts, timeout table copy, and selected state table. Per-connection state includes TCP state, old state, timeout, flags, app binding, and destination counters. Static timeout defaults cover all IPVS TCP states.

## Dependencies and Integration Points
Depends on TCP/IP header helpers, IPv6 checksum support, IPVS app helper APIs, connection/service lookup, sysctls for sloppy and secure TCP, Netfilter verdicts, and the generic protocol registry. TCP app helpers are bound only for MASQ/NAT forwarding.

## Risks
State tables are dense and easy to regress, especially `NOOUTPUT` and secure TCP modes. App helper payload mangling changes checksum behavior and can require seqadj conntrack support elsewhere. Header parsing for ICMP-embedded packets sees only ports. Counter transitions depend on the active-state table matching protocol semantics. Sloppy mode can schedule midstream packets.

## Test Signals
Cover normal SYN/SYN-ACK/ACK establishment, FIN/RST teardown, secure TCP mode, sloppy TCP mode, Active FTP SYN+ACK scheduling, app helper NAT with checksum and sequence adjustments, IPv4/IPv6 checksum modes, CHECKSUM_PARTIAL/COMPLETE/NONE paths, LISTEN timeout setup, and active/inactive destination counter changes.
