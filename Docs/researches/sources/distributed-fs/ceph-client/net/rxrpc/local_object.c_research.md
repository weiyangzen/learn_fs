<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_object.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/local_object.c

## Purpose
`local_object.c` manages AF_RXRPC local endpoint objects. It allocates, deduplicates, references, activates, deactivates, opens, and destroys the UDP tunnel socket backing an rxrpc local address, and it owns local endpoint list membership in the per-network namespace.

## Important APIs, Types, And Functions
Important functions include `rxrpc_lookup_local()`, `rxrpc_get_local()`, `rxrpc_get_local_maybe()`, `rxrpc_put_local()`, `rxrpc_use_local()`, `rxrpc_unuse_local()`, `rxrpc_destroy_local()`, `rxrpc_destroy_all_locals()`, and `rxrpc_local_dont_fragment()`. Internal helpers include `rxrpc_alloc_local()`, `rxrpc_open_socket()`, `rxrpc_local_cmp_key()`, `rxrpc_encap_err_rcv()`, and the client connection reap timer callback.

## Control Flow
Lookup takes `rxnet->local_mutex`, searches `rxnet->local_endpoints` for an address match ignoring service ID, rejects service socket sharing, tries to reuse a live endpoint, or allocates a replacement/new object. Socket open creates a UDP socket, installs rxrpc tunnel callbacks and `sk_user_data`, enables ICMP error reporting and DF behavior, starts the `rxrpc_io_thread`, and publishes the thread pointer after readiness. Unuse decrements active users and stops the IO thread at zero. Destruction removes the endpoint from the namespace list, cleans local connections, shuts down and releases the socket, purges receive queues, drops client connections, and drains the page fragment cache before RCU frees the object.

## State And Persistence
Persistent state lives in `struct rxrpc_local`: `ref`, `active_users`, net/rxnet pointers, socket, IO thread, endpoint address, service lock, queues, connection IDs, client bundle/connection structures, timers, and debug ID. List membership is protected by `local_mutex` and RCU; lifetime combines refcounting with an active-user count that controls transport shutdown.

## Dependencies And Integration Points
The file depends on UDP tunnel setup, IPv4/IPv6 ICMP error delivery, per-net namespace storage from `net_ns.c`, receive encapsulation in `rxrpc_encap_rcv`, IO thread processing, client/service connection cleanup, peer keepalive users, and tracing.

## Risks And Edge Cases
The code intentionally replaces dying endpoints but bind/open may still fail if the old socket still owns the address. Services cannot share a UDP endpoint with other services. `sk_user_data` and socket shutdown ordering are critical because callbacks can race teardown. Active-user and refcount transitions must stay paired to avoid stopping a socket while peers or calls still need it.

## Test Signals
Test endpoint reuse, duplicate service bind rejection, IPv4/IPv6 socket creation, ICMP error callback delivery, DF toggling, IO-thread start/stop, lookup races during endpoint death, namespace exit leak checks, and lockdep/RCU coverage around `local_endpoints`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_object.c -->
