# sources/distributed-fs/ceph-client/net/rxrpc/conn_service.c

## Purpose
`conn_service.c` manages service-side connection lookup, publication, preallocation, initialization from incoming packets, service upgrade, and unpublication from peer connection trees.

## Important APIs and functions
- `rxrpc_find_service_conn_rcu()` finds a service connection in a peer rbtree keyed by epoch and cid.
- `rxrpc_prealloc_service_connection()` allocates a service connection and places it on namespace service/proc lists.
- `rxrpc_new_incoming_connection()` initializes a preallocated connection from the first incoming packet and publishes it.
- `rxrpc_unpublish_service_conn()` removes a service connection from the peer tree.

## Control flow
Packet input first finds or creates a peer, then looks for a service connection under that peer. If no connection exists, `call_accept.c` consumes a preallocated connection and calls `rxrpc_new_incoming_connection()`. That function copies protocol identifiers, service ID, security index, direction, and security module, decides secured vs unsecured state, applies service ID upgrade when requested by the first packet, sets active count, and publishes into `peer->service_conns`.

## State and persistence behavior
Peer service connections are stored in an rbtree guarded by a seqlock so RCU readers can retry on mutation. Preallocated service connections start with refcount 2 because namespace service/proc lists hold them before activation. Published connections carry `RXRPC_CONN_IN_SERVICE_CONNS`; unpublish clears the flag and erases the node.

## Dependencies and integration points
This file is tightly coupled with `call_accept.c`, `io_thread.c`, `conn_object.c`, peer allocation/lookup, rxrpc security selection, namespace service connection lists, and service upgrade configuration in `rxrpc_sock`.

## Risks
The service tree is exposed to attacker-chosen epoch/cid values, so the rbtree design avoids hash bucket stuffing but still depends on correct seqlock retry behavior. Publishing assumes incoming connection setup is non-reentrant for a given connection. Replacement of dead extant nodes must avoid live duplicate connections.

## Test signals
Exercise lookup under concurrent publish/unpublish, new service connection setup, service upgrade on first packet only, security-index zero vs nonzero state, stale dead-node replacement, and unpublish during service reaping.
