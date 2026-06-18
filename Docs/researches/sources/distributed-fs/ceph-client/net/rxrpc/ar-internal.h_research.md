# sources/distributed-fs/ceph-client/net/rxrpc/ar-internal.h

## Purpose
`ar-internal.h` is the private contract for the AF_RXRPC implementation. It defines the socket, local endpoint, peer, connection, call, transmit-buffer, transmit-queue, ACK-summary, state, flag, event, and security-operation structures shared by the rxrpc source files. It also declares the cross-file APIs used by receive dispatch, call lifecycle, connection management, output, peer/local handling, security, key management, recvmsg/sendmsg, statistics, and tracing.

## Important APIs, types, and functions
- `struct rxrpc_net` stores per-network-namespace state: active calls, connection and bundle proc lists, service connection reaper state, peers, keepalive state, and rx/tx statistics.
- `struct rxrpc_sock` extends `struct sock` and owns service backlog preallocation, receive queues, socket call indexes, security keys, service IDs, and application callbacks.
- `struct rxrpc_local` represents a UDP endpoint and owns the I/O kthread queues: `rx_queue`, `conn_attend_q`, `call_attend_q`, `new_client_calls`, client bundle tree, and idle client connection list.
- `struct rxrpc_peer` is the remote transport endpoint, with service-connection tree, error target list, PMTU state, RTT cache, and congestion threshold.
- `struct rxrpc_connection` models a virtual RxRPC connection, including four channels, security state, connection-level rx queue, timers/work items, retransmittable terminal packet state, and service/client identity.
- `struct rxrpc_call` models one RPC call and carries call state, socket ownership, timers, tx/rx queues, congestion state, RACK/TLP state, ACK-generation state, RTT samples, completion, abort metadata, and user-visible identifiers.
- `struct rxrpc_security` is the pluggable security interface for no-security, rxkad, and rxgk implementations.
- Inline helpers such as `rxrpc_set_call_state()`, `rxrpc_call_state()`, `rxrpc_is_conn_aborted()`, `rxrpc_queue_rx_call_packet()`, `rxrpc_tx_window_space()`, and sequence comparison helpers encode ordering, queueing, and wraparound assumptions used throughout the implementation.

## Control flow and integration
The header ties the main runtime loop together: UDP input enters through `rxrpc_encap_rcv()`, the local I/O thread calls into packet input, call packets are queued to `call->rx_queue`, and call/connection pokes place objects on local attend queues. Client calls are created in socket/sendmsg code, queued through `local->new_client_calls`, assigned to bundle channels by `conn_client.c`, then driven by `call_event.c` and `input.c`. Service calls are preallocated through `call_accept.c`, attached to service connections, and published through peer service trees. Output functions declared here send ACK, DATA, ABORT, RESPONSE, reject, and PMTU-probe packets.

## State and persistence behavior
The persistent in-memory state is mostly refcounted and RCU protected. Calls and connections are listed in namespace-global structures for proc/debug and teardown checks. Socket-visible call completion is ordered with release/acquire barriers around `_state`, `completion`, `abort_code`, and `error`. Connection abort state uses release/acquire ordering around `conn->state`. Call and connection timers are reduced to the earliest pending deadline, and final destruction may be deferred to workqueue or RCU when invoked from softirq or while processing is active.

## Dependencies
This header depends on Linux networking (`sock`, `sk_buff`, UDP transport), keyrings, RCU, IDR/rbtree/list primitives, timers, workqueues, seqlocks, atomics/refcounts, minmax RTT helpers, and `protocol.h` wire-format definitions. It is the dependency hub for every rxrpc implementation file in this subset.

## Risks and invariants
Important invariants include backlog ordering `calls >= conns >= peers`, four channels per connection, no serial number zero, call completion before final put, socket release before call free, connection final ACK bits matching channel cached terminal state, and seq-number comparisons using wrap-safe helpers. Bugs here affect the whole subsystem, especially memory ordering, refcount ownership, timer cancellation, and queue ownership.

## Test signals
Useful signals are KUnit/static assertions around inline helpers, lockdep and KCSAN coverage for state transitions, packet-driven integration tests for call phase transitions, namespace teardown leak checks for `nr_calls` and `nr_conns`, and tracepoint validation for call/connection refcount and timer flows.
