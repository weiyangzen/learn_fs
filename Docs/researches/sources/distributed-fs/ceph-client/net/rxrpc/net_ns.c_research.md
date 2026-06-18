<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/net_ns.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/net_ns.c

## Purpose
`net_ns.c` creates and tears down AF_RXRPC per-network namespace state. It initializes namespace-scoped call, connection, local endpoint, peer, keepalive, reaper, statistics, and `/proc/net/rxrpc` structures.

## Important APIs, Types, And Functions
The file defines `rxrpc_net_id`, `rxrpc_net_ops`, `rxrpc_init_net()`, `rxrpc_exit_net()`, `rxrpc_service_conn_reap_timeout()`, and `rxrpc_peer_keepalive_timeout()`. It initializes `struct rxrpc_net` fields and proc entries backed by seq operations from `proc.c`.

## Control Flow
Namespace init marks the rxrpc namespace live, generates a random epoch with `RXRPC_RANDOM_EPOCH`, initializes call and connection lists/counters/locks, service connection reaper work and timer, local endpoint list and mutex, peer hash and keepalive buckets, and creates proc entries for calls, conns, bundles, peers, locals, and stats. Namespace exit marks the namespace dead, synchronously stops keepalive timers/work, destroys calls, connections, peers, and locals, then removes proc state.

## State And Persistence
State persists in `struct rxrpc_net` for the lifetime of the network namespace. The `live` bit gates timers/work. The epoch tags outgoing packets from the namespace. Proc entries expose namespace-local runtime state and counters.

## Dependencies And Integration Points
This file integrates with Linux pernet operations, procfs, call/connection/peer/local object destructors, peer keepalive worker, service connection reaper, and statistics display/clear support.

## Risks And Edge Cases
Exit ordering is important: timers can rearm work, so the peer keepalive timer is deleted both before and after work cancellation. Calls and connections must be gone before peers and locals are leak-checked. Proc creation failures leave the namespace non-live and abort initialization.

## Test Signals
Exercise namespace create/destroy loops, proc entry visibility per namespace, timer/work cancellation on namespace teardown, leak diagnostics from destroy-all functions, and concurrent sockets active during namespace shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/net_ns.c -->
