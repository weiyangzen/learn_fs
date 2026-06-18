# sources/distributed-fs/ceph-client/net/rxrpc/conn_object.c

## Purpose
`conn_object.c` provides common connection allocation, lookup, refcounting, disconnection, timers, cleanup, service-connection reaping, and namespace teardown checks for both client and service connections.

## Important APIs and functions
- `rxrpc_alloc_connection()` initializes a connection object, timers, work items, queues, locks, default no-security module, and debug ID.
- `rxrpc_find_client_connection_rcu()` looks up client connections by local connection ID and validates epoch/local/peer port.
- `__rxrpc_disconnect_call()` caches terminal per-channel ACK/ABORT state.
- `rxrpc_disconnect_call()` detaches a completed call from client or service connection state.
- `rxrpc_poke_conn()`, `rxrpc_queue_conn()`, `rxrpc_put_connection()`, and `rxrpc_get_connection*()` manage connection work and refs.
- `rxrpc_service_connection_reaper()` expires idle service connections.
- `rxrpc_destroy_all_connections()` asserts namespace cleanup.

## Control flow
Call completion eventually calls `rxrpc_disconnect_call()`. Client calls delegate channel/cache handling to `conn_client.c`; service calls clear the channel, update idle timestamp, decrement active count, and arm the service reaper when the connection becomes idle. Connection timers poke the I/O thread. Last put schedules or performs cleanup depending on context, active timers, and processor work.

## State and persistence behavior
Connections are refcounted and RCU freed. Service connections also use `active` to represent live channel usage and reaper eligibility. Cleanup removes proc-list entries, handles PMTU probe loss state, purges connection rx queue and response skb, releases client ID/bundle/peer/local/key/security resources, drains tx page fragments, and waits for RCU before namespace counters reach zero.

## Dependencies and integration points
It integrates with client connection IDR, service peer trees, PMTU handling, output terminal retransmission, security clear hooks, local/peer/bundle refs, workqueues, timers, proc lists, and namespace lifecycle.

## Risks
Context-sensitive destruction is high risk: softirq or busy work paths must defer cleanup. Service reaping must not remove preallocated or active connections. `__rxrpc_disconnect_call()` must cache enough terminal state for duplicate packet handling after call free. Client lookup by cid must reject stale epoch or wrong peer port.

## Test signals
Test duplicate terminal packet handling after call free, service idle reaping, closed-service fast expiry, client lookup rejection, PMTU probe cleanup, namespace destroy leak assertions, and last-put cleanup from softirq/workqueue contexts.
