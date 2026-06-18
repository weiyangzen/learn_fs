
# sources/distributed-fs/ceph-client/include/trace/events/sctp.h

## Purpose
Defines SCTP tracepoints for path probing and congestion/window probing so network diagnostics can observe association path state and transport-level flow-control values.

## Important APIs, Types, and Functions
Events are `sctp_probe_path` and `sctp_probe`. `sctp_probe_path` records association pointer, transport pointer, source/destination socket addresses, state, path MTU, cwnd, ssthresh, partial bytes acknowledged, flight size, error count, and heartbeat interval. `sctp_probe` records association pointer, transport pointer, mark, rwnd, unacknowledged count, and flight size.

## Control Flow
SCTP code emits these tracepoints around path monitoring and congestion/window updates. The event assignment copies address structures and transport counters from live association/transport state into tracing records.

## State and Persistence
The header owns no state. Trace records persist snapshots of SCTP association and transport counters, address pairs, and flow-control metrics in the tracing ring buffer.

## Dependencies and Integration Points
Depends on SCTP socket/transport structures at call sites and `linux/tracepoint.h`. Integrates with the SCTP stack, networking trace tools, congestion diagnostics, and heartbeat/path-failover investigations.

## Risks
Address formatting and transport pointer values are diagnostic, not stable identifiers. High-frequency SCTP traffic can generate large trace volume. Consumers must handle both IPv4 and IPv6 socket address payloads correctly.

## Test Signals
Signals include SCTP association setup, multihoming failover, heartbeat timeout tests, cwnd/rwnd changes under load, packet loss injection, and trace output validation for IPv4/IPv6 paths.
