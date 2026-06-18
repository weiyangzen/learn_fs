<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/proc.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/proc.c

## Purpose
`proc.c` implements `/proc/net/rxrpc` diagnostics for calls, connections, bundles, peers, local endpoints, and statistics. It provides seq_file operations and a write handler to clear counters.

## Important APIs, Types, And Functions
The file defines `rxrpc_call_seq_ops`, `rxrpc_connection_seq_ops`, `rxrpc_bundle_seq_ops`, `rxrpc_peer_seq_ops`, `rxrpc_local_seq_ops`, `rxrpc_stats_show()`, and `rxrpc_stats_clear()`. Show helpers format call state, connection state, bundle flags, peer RTT/MTU, local endpoint queue/use counts, and stat groups.

## Control Flow
Each seq start/next/stop pair acquires the appropriate lock: calls use RCU list iteration, conns and bundles use `conn_lock`, peers iterate hash buckets with encoded positions under RCU, and locals iterate the endpoint hlist under RCU. Show callbacks print a header for the start token/head and then format one object. Stats show reads atomic counters; stats clear accepts only empty/newline writes and resets the relevant atomic counters and arrays.

## State And Persistence
No protocol state is owned here. The file observes namespace lists/hash tables and atomics from `struct rxrpc_net`, plus per-object fields such as call windows, connection channels, bundle connection IDs, peer PMTU/RTT, local active users, and queue lengths.

## Dependencies And Integration Points
Proc entries are created by `net_ns.c`. The file depends on call/connection/peer/local layout, state-name tables, kernel key serial numbers, seq_file networking helpers, RCU/list/hash iteration primitives, and rxrpc stats counters incremented throughout TX/RX paths.

## Risks And Edge Cases
Diagnostics are lock-light and can show moving values. Peer hash iteration encodes bucket and index into `loff_t`; position handling must avoid infinite loops and UINT overflow. Stats clear uses `memset()` on atomic arrays, which assumes atomic_t storage representation is compatible with zeroing.

## Test Signals
Read all proc files under active traffic, exercise namespace isolation, clear stats with valid and invalid writes, check peer hash iteration across empty buckets, and run under lockdep/RCU debug while calls/connections are created and destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/proc.c -->
