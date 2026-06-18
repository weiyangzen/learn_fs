
# sources/distributed-fs/ceph-client/include/trace/events/sock.h

## Purpose
Defines socket tracepoints for receive-queue pressure, socket memory limits, TCP/INET state transitions, socket error reports, data-ready callbacks, and send/receive message lengths.

## Important APIs, Types, and Functions
The header exports TCP state enums and `show_inet_sock_state()`. Events are `sock_rcvqueue_full`, `sock_exceed_buf_limit`, `inet_sock_set_state`, `inet_sk_error_report`, `sk_data_ready`, and the `sock_msg_length` class used by `sock_send_length` and `sock_recv_length`. Fields include socket cookies, protocol/family, ports, v4/v6 addresses, queue allocation/limits, rmem/wmem, old/new states, errors, and message lengths.

## Control Flow
Networking code emits these events when receive queues fill, per-protocol memory pressure exceeds limits, INET sockets change state, errors are reported, data-ready callbacks run, and send/receive operations account message lengths. Address/port fields are captured at the event site.

## State and Persistence
The header owns no socket state. Trace records persist snapshots of socket identifiers, memory accounting, addresses, ports, states, errors, and lengths in trace buffers. Socket cookies give tooling a more stable correlation key than raw pointers.

## Dependencies and Integration Points
Depends on socket, inet, TCP state, and tracepoint helpers. Integrates with core networking, TCP/UDP diagnostics, BPF socket tracing, memory-pressure analysis, and latency/throughput instrumentation.

## Risks
Socket tracepoints can expose address/port metadata and high event volume. State enum mappings must stay current. Call sites must handle IPv4/IPv6 address capture correctly, and consumers should not treat cookies as globally persistent across reboot.

## Test Signals
Signals include TCP connect/close state transitions, UDP/TCP receive queue saturation, memory pressure tests, socket error injection, BPF attachment, IPv4/IPv6 address formatting, and send/receive size accounting checks.
