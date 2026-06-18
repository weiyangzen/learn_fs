# sources/distributed-fs/ceph-client/net/rxrpc/call_accept.c

## Purpose
`call_accept.c` handles service-side call acceptance. It prepares backlog objects for services, turns the first incoming DATA packet into a live service call, attaches the call to a service connection, and charges user or kernel accept slots with application-supplied call IDs.

## Important APIs and functions
- `rxrpc_service_prealloc()` allocates the `rxrpc_backlog` container for a service socket.
- `rxrpc_service_prealloc_one()` fills circular preallocation pools for peers, service connections, and calls, registers the call under `rx->calls`, attaches user IDs and optional kernel callbacks, and queues it in the call backlog.
- `rxrpc_discard_prealloc()` drains unused peer, connection, and call preallocations during service shutdown.
- `rxrpc_alloc_incoming_call()` consumes preallocated objects, optionally creates a new peer and service connection, or references an existing connection, then initializes call fields from the connection.
- `rxrpc_new_incoming_call()` is called from packet input to validate service/security state, allocate/initialize the call, notify the application, start connection challenge if needed, and queue the first packet to the call.
- `rxrpc_user_charge_accept()` and exported `rxrpc_kernel_charge_accept()` are the userspace/kernel charging entry points.

## Control flow
Services first create `rx->backlog`; user or kernel code charges individual accept entries with a user call ID. On the first DATA packet for a missing service call, `io_thread.c` calls `rxrpc_new_incoming_call()`. That function checks the local service binding, service ID, security class, listen/shutdown state, and backlog availability. It then consumes a preallocated call plus a connection/peer if needed, calls `rxrpc_incoming_call()`, optionally notifies application code, queues a connection challenge for secured service connections, assesses MTU, links error delivery, queues the packet to the call, and drops its input reference.

## State and persistence behavior
The service backlog is a set of ring buffers with release/acquire head and tail updates because producers charge accept entries and the I/O thread consumes them. Calls are inserted into the socket rbtree and socket call list before entering the backlog. Incoming calls transition from `RXRPC_CALL_SERVER_PREALLOC` to live server receive state in `rxrpc_incoming_call()`. Service connections either come from preallocation and get published to the peer service tree, or are refcounted if already present.

## Dependencies and integration points
This file integrates with peer allocation, service connection publishing, security lookup, call object creation/release, socket notification callbacks, direct reject/abort packet marking, MTU assessment, and the I/O thread's packet dispatch. Kernel services can receive callbacks through `rxrpc_kernel_ops`.

## Risks
The main risks are backlog exhaustion returning BUSY, duplicate user call IDs, consuming backlog entries out of order, service shutdown racing incoming packets, and missing security rejection paths. The invariant that preallocated calls, connections, and peers remain ordered by capacity is asserted in the allocator.

## Test signals
Exercise accept charging limits, duplicate user IDs, missing services, unsupported security, listen-disabled shutdown, peer reuse vs new peer allocation, secured service challenge initiation, and backlog discard on socket close.
