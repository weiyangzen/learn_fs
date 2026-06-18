# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_udp.c

## Purpose
Implements UDP protocol support for IPVS, including datagram service scheduling, NAT port and checksum rewriting, a simple timeout/state model, and UDP application helper binding.

## Important APIs, Types, and Functions
`udp_conn_schedule()` finds a virtual service by packet ports and schedules a connection. `udp_snat_handler()` and `udp_dnat_handler()` rewrite UDP source or destination ports. `udp_csum_check()` validates UDP checksums when present. `udp_register_app()`, `udp_unregister_app()`, and `udp_app_conn_bind()` manage UDP helpers. `udp_state_transition()` refreshes timeout and assures conntrack on output. `ip_vs_protocol_udp` registers the protocol.

## Control Flow
Scheduling extracts UDP ports from the packet or ICMP payload, drops truncated packets, finds a matching service by mark/protocol/address/port, optionally drops under IPVS overload, and calls `ip_vs_schedule()` or `ip_vs_leave()`. NAT handlers ensure header writability, invoke app helpers when present, rewrite the selected port, and update checksums. UDP with zero checksum avoids incremental checksum work except when full recomputation is forced by payload changes or partial checksum state. The state transition simply sets the normal UDP timeout.

## State and Persistence
Per-netns UDP state includes helper hash tables and a copied timeout table with a normal five-minute timeout. Per-connection state is minimal: timeout, app pointer, flags, and endpoint data. UDP has one normal state for state-name reporting.

## Dependencies and Integration Points
Depends on UDP/IP headers, IPv6 checksum helpers, IPVS service lookup and NAT app APIs, SKB checksum modes, Netfilter verdicts, and generic protocol registration. Helpers bind only for MASQ/NAT forwarding.

## Risks
UDP zero-checksum handling differs from TCP; full recomputation may create `CSUM_MANGLED_0`. Stateless UDP services depend on timeout tuning for connection table size. App helper mangling can force full checksum computation. ICMP handling only has embedded ports. Fragmented IPv6 packets bypass NAT header rewrite for non-first fragments.

## Test Signals
Test UDP service scheduling, one-packet services, zero and nonzero UDP checksums, IPv4/IPv6 NAT rewrite, CHECKSUM_PARTIAL/COMPLETE/NONE paths, app helper binding and payload changes, timeout refresh on traffic, overload drops, and truncated packet drops.
