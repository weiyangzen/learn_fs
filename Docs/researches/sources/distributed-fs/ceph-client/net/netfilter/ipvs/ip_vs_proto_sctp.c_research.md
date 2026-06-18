# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto_sctp.c

## Purpose
Implements SCTP protocol support for IPVS, including connection scheduling, SNAT/DNAT port rewrite, CRC handling, SCTP association state transitions, per-netns timeout tables, and SCTP application helper binding.

## Important APIs, Types, and Functions
`sctp_conn_schedule()` finds services for new SCTP associations. `sctp_snat_handler()` and `sctp_dnat_handler()` rewrite source or destination ports and recompute SCTP CRC when needed. `sctp_csum_check()` validates CRC32c. `sctp_events` maps SCTP chunk types to IPVS events, and `sctp_states` is the state transition table. `set_sctp_state()` and `sctp_state_transition()` update connection state and active/inactive counters. `sctp_register_app()`, `sctp_unregister_app()`, and `sctp_app_conn_bind()` manage app helpers. `ip_vs_protocol_sctp` registers the protocol contract.

## Control Flow
Scheduling inspects the SCTP header and first chunk. It schedules only INIT packets unless sloppy SCTP mode is enabled, rejects ABORT as a connection opener, and handles ICMP-embedded headers by reading the first four bytes of ports. NAT handlers ensure the SCTP header is writable, optionally invoke app helpers, rewrite the port, and recompute CRC unless GSO or hardware SCTP CRC offload keeps checksum work deferred. State transitions read the first chunk, detect bundled ABORT after COOKIE chunks where relevant, map chunk type to an event, adjust `NOOUTPUT` direction handling, update active/inactive counters, assure conntrack controls on establishment, and set timeout from the per-netns table.

## State and Persistence
Per-netns state includes SCTP app hash tables and copied timeout table. Per-connection state includes IPVS SCTP state, timeout, old state, `NOOUTPUT`, inactive flag, and sequence/app metadata. The file owns static transition tables and timeout defaults.

## Dependencies and Integration Points
Depends on Linux SCTP headers, SCTP checksum support, IP/IPv6 checksum helpers, IPVS app helper APIs, IPVS service lookup, connection table lookups, sysctl sloppy SCTP, and Netfilter verdicts. It integrates with generic protocol registration in `ip_vs_proto.c`.

## Risks
Only the first chunk is inspected except for limited COOKIE plus ABORT detection, so unusual chunk bundling can affect state accuracy. CRC recomputation decisions depend on GSO and device `NETIF_F_SCTP_CRC`. `sctp_csum_check()` directly accesses `skb->data + sctphoff` after writability assumptions, so callers must ensure header presence. Sloppy mode permits scheduling non-INIT openers and can create broader matching behavior.

## Test Signals
Run SCTP association setup and shutdown through IPVS, including INIT, INIT-ACK, COOKIE-ECHO, COOKIE-ACK, DATA, SHUTDOWN, ABORT, and bundled COOKIE/ABORT cases. Validate NAT port rewrite and CRC, GSO/offload behavior, app helper binding, sloppy SCTP behavior, timeout state names, IPv6 fragments, and active/inactive counter transitions.
