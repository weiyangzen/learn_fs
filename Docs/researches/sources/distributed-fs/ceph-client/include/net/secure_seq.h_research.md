# sources/distributed-fs/ceph-client/include/net/secure_seq.h

## Purpose
This header declares secure per-flow sequence and ephemeral-port hash helpers used by TCP and related networking code to generate hard-to-predict initial sequence numbers, timestamp offsets, and port-selection hashes.

## Important APIs, Types, And Functions
`union tcp_seq_and_ts_off` overlays a 64-bit hash with 32-bit TCP sequence and timestamp offset fields. APIs include `secure_ipv4_port_ephemeral()`, `secure_ipv6_port_ephemeral()`, `secure_tcp_seq_and_ts_off()`, and `secure_tcpv6_seq_and_ts_off()`. Inline compatibility helpers `secure_tcp_seq()` and `secure_tcpv6_seq()` use `init_net` and return only the sequence half.

## Control Flow
Protocol code supplies source/destination addresses and ports. The implementation returns deterministic secret-keyed values for the flow and network namespace; callers use either the full sequence/timestamp pair or only the sequence value.

## State And Persistence
No state is declared here. Security depends on hidden secret material maintained by the implementation and network namespace context.

## Dependencies And Integration Points
It depends on Linux integer/endian types and `struct net`. It integrates with TCP ISN generation, timestamp randomization, and ephemeral port selection for IPv4 and IPv6.

## Risks And Test Signals
Risks include namespace confusion through init_net wrappers, weak hash secret rotation, endian mistakes, and flow-collision behavior. Test signals are TCP connection establishment, timestamp offset distribution, per-net namespace behavior, and port-randomization collision/regression tests.
