# sources/distributed-fs/ceph-client/net/rxrpc/call_object.c

## Purpose
`call_object.c` owns call allocation, publication, lookup, connection setup for client calls, incoming call activation, reference management, socket detachment, buffer cleanup, final destruction, and the kernel query API for call security.

## Important APIs and functions
- `rxrpc_alloc_call()` initializes a call object, queues, timers, refcount, default windows, congestion state, RTT state, and namespace counters.
- `rxrpc_new_client_call()` creates and publishes a client call under a user call ID, then queues it for connection assignment.
- `rxrpc_incoming_call()` activates a preallocated service call on a connection/channel.
- `rxrpc_poke_call()` queues a call for I/O thread attention.
- `rxrpc_release_call()` and `rxrpc_release_calls_on_socket()` detach calls from a socket.
- `rxrpc_put_call()`, `rxrpc_cleanup_call()`, and `rxrpc_destroy_call()` implement final lifetime cleanup.
- `rxrpc_kernel_query_call_security()` exposes service/security info to kernel users.

## Control flow
Client creation obtains a global user or kernel call slot, allocates security, publishes the call in the socket rbtree/list and namespace call list, releases the socket lock, then queues the call on `local->new_client_calls` for the I/O thread to bind to a connection. Incoming service calls are supplied by `call_accept.c` and get call ID, cid, service, state, channel pointer, error target link, and timer initialized here.

## State and persistence behavior
Calls have a strict lifecycle: allocated with refcount 1, published in socket and namespace lists, optionally assigned a connection/channel, completed through `call_state.c`, released from socket ownership, then final-put removes from namespace list and destroys buffers, connection, bundle, peer, local, and key references. The call limiter semaphores cap user and kernel call creation separately.

## Dependencies and integration points
This file connects socket send/recv APIs, client bundle lookup, service accept, connection disconnection, workqueue/RCU destruction, key/security initialization, and proc/debug lists. It relies on `rxrpc_set_call_completion()` for successful or failed terminal states.

## Risks
Duplicate user call IDs must be detected under `rx->call_lock`. Error after socket publication intentionally leaves completion for recvmsg rather than returning sendmsg failure. Release requires `RXRPC_CALL_RELEASED` exactly once; final put asserts completion. Destruction must be safe under RCU and while timers/work may still be active.

## Test signals
Cover duplicate user IDs, client connection allocation failure after socket publication, service incoming activation, socket close with accepted and to-be-accepted calls, final refcount cleanup, limiter release, and namespace teardown leak detection.
